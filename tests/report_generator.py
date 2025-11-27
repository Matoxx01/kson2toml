from datetime import datetime
from pathlib import Path

def generate_html_report(results, total, passed, failed):
    """
    Generate an HTML report with test results
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KSON2TOML Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: white;
        }}
        .summary-card.total {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .summary-card.passed {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }}
        .summary-card.failed {{
            background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
        }}
        .summary-card h2 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .summary-card p {{
            margin: 5px 0 0 0;
            font-size: 1.1em;
        }}
        .test-result {{
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid;
        }}
        .test-result.passed {{
            background-color: #e8f5e9;
            border-color: #4CAF50;
        }}
        .test-result.failed {{
            background-color: #ffebee;
            border-color: #f44336;
        }}
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .test-name {{
            font-weight: bold;
            font-size: 1.2em;
            color: #333;
        }}
        .test-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }}
        .test-status.passed {{
            background-color: #4CAF50;
        }}
        .test-status.failed {{
            background-color: #f44336;
        }}
        .test-content {{
            margin-top: 15px;
        }}
        .code-block {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
        }}
        .error-block {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
            color: #856404;
        }}
        .section-title {{
            font-weight: bold;
            color: #555;
            margin-top: 15px;
            margin-bottom: 5px;
        }}
        .module-section {{
            margin-top: 40px;
        }}
        .module-title {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 KSON2TOML Test Report</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        
        <div class="summary">
            <div class="summary-card total">
                <h2>{total}</h2>
                <p>Total Tests</p>
            </div>
            <div class="summary-card passed">
                <h2>{passed}</h2>
                <p>Passed ({100*passed//total if total > 0 else 0}%)</p>
            </div>
            <div class="summary-card failed">
                <h2>{failed}</h2>
                <p>Failed ({100*failed//total if total > 0 else 0}%)</p>
            </div>
        </div>
"""
    
    # Group results by module
    results_by_module = {}
    for result in results:
        module = result['module']
        if module not in results_by_module:
            results_by_module[module] = []
        results_by_module[module].append(result)
    
    # Generate sections for each module
    for module_name, module_results in results_by_module.items():
        module_passed = sum(1 for r in module_results if r['passed'])
        module_total = len(module_results)
        
        html_content += f"""
        <div class="module-section">
            <div class="module-title">
                <h2>{module_name}</h2>
                <p>{module_passed}/{module_total} tests passed</p>
            </div>
"""
        
        for result in module_results:
            status_class = 'passed' if result['passed'] else 'failed'
            status_text = 'PASSED ✓' if result['passed'] else 'FAILED ✗'
            
            html_content += f"""
            <div class="test-result {status_class}">
                <div class="test-header">
                    <div class="test-name">{result['test_name']}</div>
                    <div class="test-status {status_class}">{status_text}</div>
                </div>
                
                <div class="test-content">
                    <div class="section-title">KSON Source:</div>
                    <div class="code-block">{html_escape(result['kson_source'])}</div>
                    
                    <div class="section-title">Expected TOML:</div>
                    <div class="code-block">{html_escape(result['toml_expected'])}</div>
"""
            
            if result['toml_generated']:
                html_content += f"""
                    <div class="section-title">Generated TOML:</div>
                    <div class="code-block">{html_escape(result['toml_generated'])}</div>
"""
            
            if result['errors']:
                html_content += """
                    <div class="section-title">Errors:</div>
                    <div class="error-block">
"""
                for error in result['errors']:
                    html_content += f"                        <p>{html_escape(error)}</p>\n"
                html_content += """                    </div>
"""
            
            html_content += """                </div>
            </div>
"""
        
        html_content += """        </div>
"""
    
    html_content += """    </div>
</body>
</html>"""
    
    # Write HTML report
    report_path = Path(__file__).parent / 'test_report.html'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def html_escape(text):
    """Escape HTML special characters"""
    if text is None:
        return ""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))