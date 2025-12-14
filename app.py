"""
Aplicación gráfica interactiva para convertir KSON a TOML
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from kson2toml import kson2toml
import os


class Kson2TomlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KSON to TOML Converter")
        self.root.geometry("900x700")
        
        # Configurar estilo
        self.root.configure(bg="#f0f0f0")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="KSON to TOML Converter", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Botones superiores
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        
        ttk.Button(button_frame, text="Abrir archivo KSON", 
                   command=self.load_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Guardar TOML", 
                   command=self.save_file).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Limpiar", 
                   command=self.clear_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Convertir", 
                   command=self.convert).pack(side="left", padx=5)
        
        # Etiqueta KSON
        kson_label = ttk.Label(main_frame, text="Entrada KSON:", 
                               font=("Arial", 10, "bold"))
        kson_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 5))
        
        # Text area KSON
        self.kson_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.kson_text.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=5)
        
        # Etiqueta TOML
        toml_label = ttk.Label(main_frame, text="Salida TOML:", 
                               font=("Arial", 10, "bold"))
        toml_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 5))
        
        # Text area TOML
        self.toml_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.toml_text.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=5)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_bar.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(10, 0))
    
    def load_file(self):
        """Carga un archivo KSON"""
        file_path = filedialog.askopenfilename(
            filetypes=[("KSON files", "*.kson"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.kson_text.delete(1.0, tk.END)
                self.kson_text.insert(1.0, content)
                self.status_var.set(f"Archivo cargado: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
                self.status_var.set("Error al cargar archivo")
    
    def save_file(self):
        """Guarda el resultado TOML en un archivo"""
        toml_content = self.toml_text.get(1.0, tk.END).strip()
        if not toml_content:
            messagebox.showwarning("Advertencia", "No hay contenido TOML para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".toml",
            filetypes=[("TOML files", "*.toml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(toml_content)
                messagebox.showinfo("Éxito", f"Archivo guardado: {os.path.basename(file_path)}")
                self.status_var.set(f"Archivo guardado: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
                self.status_var.set("Error al guardar archivo")
    
    def clear_all(self):
        """Limpia ambas áreas de texto"""
        self.kson_text.delete(1.0, tk.END)
        self.toml_text.delete(1.0, tk.END)
        self.status_var.set("Areas limpias")
    
    def convert(self):
        """Convierte KSON a TOML"""
        kson_content = self.kson_text.get(1.0, tk.END).strip()
        
        if not kson_content:
            messagebox.showwarning("Advertencia", "Ingrese contenido KSON para convertir")
            self.status_var.set("Entrada vacía")
            return
        
        try:
            self.status_var.set("Convirtiendo...")
            self.root.update()
            
            # Realizar la conversión
            toml_result = kson2toml(kson_content)
            
            # Mostrar resultado
            self.toml_text.delete(1.0, tk.END)
            self.toml_text.insert(1.0, toml_result)
            self.status_var.set("Conversión exitosa")
            messagebox.showinfo("Éxito", "Conversión realizada correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error de parseo", f"Error al convertir:\n{str(e)}")
            self.status_var.set("Error de parseo")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
            self.status_var.set("Error inesperado")


def main():
    """Función de entrada para la aplicación"""
    root = tk.Tk()
    app = Kson2TomlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()