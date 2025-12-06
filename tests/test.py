import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from kson2toml.kson2toml import kson2toml
import toml
import importlib, re
from colorama import Fore, Style, init
import importlib.util
from report_generator import generate_html_report

# All tests

def alltests():
    """
    All tests function
    - TomlString
    - TomlInteger
    - TomlFloat
    - TomlBoolean
    - TomlNull
    - TomlArray
    - TomlTable
    - TomlEmbed
    """
    
    # Get all test modules from mocks folder
    mocks_dir = Path(__file__).parent / 'mocks'
    test_modules = []
    
    # Dynamically import all test modules
    for test_file in mocks_dir.glob('Test*.py'):
        module_name = test_file.stem
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        test_modules.append((module_name, module))
    
    # ============================================================
    # PHASE 1: Validate all 'tomlexpected' first
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 1: Validating 'tomlexpected' fields")
    print("="*60)
    
    validation_errors = []
    test_metadata = []  # Store test info with names
    
    for module_name, module in test_modules:
        if hasattr(module, 'all_tests'):
            # Get test names from module
            test_names = [name for name in dir(module) 
                         if not name.startswith('_') and name != 'all_tests']
            
            for idx, test_case in enumerate(module.all_tests):
                # Find the actual test name by matching the test_case object
                test_name = None
                for name in test_names:
                    if getattr(module, name, None) is test_case:
                        test_name = name
                        break
                
                if test_name is None:
                    test_name = f"test_{idx+1}"
                
                test_metadata.append({
                    'module': module_name,
                    'test_name': test_name,
                    'test_case': test_case
                })
                
                # Validate tomlexpected
                try:
                    toml.loads(test_case['tomlexpected'])
                except toml.TomlDecodeError as e:
                    validation_errors.append({
                        'module': module_name,
                        'test': test_name,
                        'error': str(e)
                    })
                except Exception as e:
                    validation_errors.append({
                        'module': module_name,
                        'test': test_name,
                        'error': f"Unexpected error: {e}"
                    })
    
    # Report validation results
    if validation_errors:
        printmas("\n[WARNING] VALIDATION ERRORS FOUND IN 'tomlexpected':")
        print("-" * 60)
        for err in validation_errors:
            printmas(f"  [FAIL {err['module']}] [{err['test']}]")
            print(f"     Error: {err['error']}")
        print("-" * 60)
        print(f"\nTotal invalid 'tomlexpected': {len(validation_errors)}")
    else:
        printmas("\n[OK] All 'tomlexpected' fields are valid TOML")
    
    # ============================================================
    # PHASE 2: Run conversion tests
    # ============================================================
    print("\n------------- PHASE 2: Running conversion tests ------------")
    
    # Storage for test results
    all_results = []
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # Run all tests from collected metadata
    current_module = None
    for test_info in test_metadata:
        module_name = test_info['module']
        test_name = test_info['test_name']
        test_case = test_info['test_case']
        
        # Print module header when switching modules
        if current_module != module_name:
            current_module = module_name
            print(f"\n{'='*60}")
            print(f"Running tests from: {module_name}")
            print(f"{'='*60}")
        
        total_tests += 1
        
        kson_source = test_case['ksonsource']
        toml_expected = test_case['tomlexpected']
        
        # Normalize whitespace for comparison
        toml_expected_normalized = '\n'.join(
            line.strip() for line in toml_expected.strip().split('\n')
            if line.strip()
        )
        
        result = {
            'module': module_name,
            'test_name': test_name,
            'kson_source': kson_source,
            'toml_expected': toml_expected,
            'toml_expected_normalized': toml_expected_normalized,
            'passed': False,
            'errors': [],
            'toml_generated': None
        }
        
        # Step 1: Validate that tomlexpected is valid TOML
        try:
            parsed_expected = toml.loads(toml_expected)
            result['expected_valid'] = True
        except toml.TomlDecodeError as e:
            result['expected_valid'] = False
            result['errors'].append(f"Expected TOML is invalid: {e}")
            printmas(f"  [FAIL] {test_name}: Expected TOML is invalid")
            all_results.append(result)
            failed_tests += 1
            continue
        except Exception as e:
            result['expected_valid'] = False
            result['errors'].append(f"Unexpected error validating expected TOML: {e}")
            printmas(f"  [FAIL] {test_name}: Unexpected error in expected TOML")
            all_results.append(result)
            failed_tests += 1
            continue
                
        # Step 2: Convert KSON to TOML
        try:
            toml_generated = kson2toml(kson_source)
            result['toml_generated'] = toml_generated
        except Exception as e:
            result['errors'].append(f"Conversion error: {type(e).__name__}: {e}")
            printmas(f"  [FAIL] {test_name}: Conversion failed - {e}")
            all_results.append(result)
            failed_tests += 1
            continue
        
        # Step 3: Validate generated TOML is valid
        try:
            parsed_generated = toml.loads(toml_generated)
            result['generated_valid'] = True
        except toml.TomlDecodeError as e:
            result['generated_valid'] = False
            result['errors'].append(f"Generated TOML is invalid: {e}")
            printmas(f"  [FAIL] {test_name}: Generated TOML is invalid")
            all_results.append(result)
            failed_tests += 1
            continue
        except Exception as e:
            result['generated_valid'] = False
            result['errors'].append(f"Unexpected error validating generated TOML: {e}")
            printmas(f"  [FAIL] {test_name}: Unexpected error validating generated TOML")
            all_results.append(result)
            failed_tests += 1
            continue
        
        # Step 4: Compare parsed results (semantic comparison)
        semantic_match = False
        try:
            if parsed_expected == parsed_generated:
                semantic_match = True
            else:
                result['errors'].append(
                    f"Semantic mismatch:\n"
                    f"Expected: {parsed_expected}\n"
                    f"Generated: {parsed_generated}"
                )
        except Exception as e:
            result['errors'].append(f"Comparison error: {e}")
        
        # Step 5: Textual comparison (tomlexpected == toml_generated)
        # Normalize by removing ALL whitespace for strict structural comparison
        def normalize_toml_strict(text):
            """Remove all whitespace to compare structure only"""
            return ''.join(text.split())
        
        toml_expected_strict = normalize_toml_strict(toml_expected)
        toml_generated_strict = normalize_toml_strict(toml_generated)
        
        result['textual_match'] = (toml_expected_strict == toml_generated_strict)
        if not result['textual_match']:
            # Show both strict comparison and readable versions
            result['errors'].append(
                f"Textual mismatch (strict comparison):\n"
                f"Expected (no whitespace): {toml_expected_strict}\n"
                f"Generated (no whitespace): {toml_generated_strict}\n\n"
                f"Expected (readable):\n{toml_expected.strip()}\n\n"
                f"Generated (readable):\n{toml_generated.strip()}"
            )
        
        # Final verdict: BOTH semantic AND textual must match
        if semantic_match and result['textual_match']:
            result['passed'] = True
            passed_tests += 1
            printmas(f"  [PASS] {test_name}")
        else:
            failed_tests += 1
            if semantic_match and not result['textual_match']:
                printmas(f"  [FAIL] {test_name}: Textual mismatch (semantic OK)")
            elif not semantic_match and result['textual_match']:
                printmas(f"  [FAIL] {test_name}: Semantic mismatch (textual OK)")
            else:
                printmas(f"  [FAIL] {test_name}: Both semantic and textual mismatch")
        
        all_results.append(result)
    
    # Generate HTML report
    generate_html_report(all_results, total_tests, passed_tests, failed_tests)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests} ({100*passed_tests//total_tests if total_tests > 0 else 0}%)")
    print(f"Failed: {failed_tests} ({100*failed_tests//total_tests if total_tests > 0 else 0}%)")
    print(f"\nHTML report generated: {Path(__file__).parent / 'test_report.html'}")
    
    return passed_tests == total_tests

# Simple test

def kson_totoml_validation():
    """
    Testea la conversión de un archivo Kson a un string Toml
    """

    kson_file = Path(__file__).parent / 'fibonacci_sequence.kson'
    with open(kson_file, 'r') as f:
        kson_string = f.read()

    result = kson2toml(kson_string)
    print("Resultado de la conversión:")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Validar que el TOML sea válido
    try:
        parsed_toml = toml.loads(result)
        printmas("[OK] El TOML generado es valido")
        print(f"Contenido parseado: {parsed_toml}")
        return True
    except toml.TomlDecodeError as e:
        printmas("[FAIL] El TOML generado NO es valido")
        print(f"Errores encontrados:")
        print(f"  - {e}")
        return False
    except Exception as e:
        printmas("[FAIL] Error inesperado al validar el TOML")
        print(f"  - {type(e).__name__}: {e}")
        return False
    
init(autoreset=True)

def printmas(text: str):
    colors = {
        "[WARNING]": Fore.YELLOW,
        "[PASS]": Fore.GREEN,
        "[FAIL]": Fore.RED,
        "[OK]": Fore.BLUE
    }

    def replacer(match):
        tag = match.group(0)
        color = colors.get(tag, "")
        return f"{color}{tag}{Style.RESET_ALL}"

    pattern = r"\[(WARNING|PASS|FAIL|OK)\]"
    colored_text = re.sub(pattern, replacer, text)
    print(colored_text)  # ← imprime directamente
    
if __name__ == "__main__":
    success = alltests()