#!/usr/bin/env python3
# ShellcodeLoaderGUI - Carga y ejecuta shellcode .bin (Donut) en memoria
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import ctypes
from ctypes import wintypes
import os
import sys

# Constantes de Windows
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40
INFINITE = 0xFFFFFFFF

class ShellcodeLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shellcode Loader v1.0 - Donut .bin Executor")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Icono opcional (si tienes .ico)
        # self.root.iconbitmap("icon.ico")
        
        # Estilos y colores
        self.root.configure(bg='#2c3e50')
        self.font_title = ('Segoe UI', 12, 'bold')
        self.font_normal = ('Segoe UI', 10)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = tk.Label(main_frame, text="Shellcode Executor (Donut .bin)", 
                         font=('Segoe UI', 16, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Frame para selección de archivo
        file_frame = tk.Frame(main_frame, bg='#34495e', relief=tk.GROOVE, bd=2)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        tk.Label(file_frame, text="Archivo .bin:", font=self.font_normal, 
                 bg='#34495e', fg='white').pack(side=tk.LEFT, padx=10, pady=10)
        tk.Entry(file_frame, textvariable=self.file_path_var, width=40, 
                 font=self.font_normal).pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
        tk.Button(file_frame, text="Examinar", command=self.browse_file, 
                  bg='#3498db', fg='white', font=self.font_normal, 
                  activebackground='#2980b9').pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Frame para botones de acción
        btn_frame = tk.Frame(main_frame, bg='#2c3e50')
        btn_frame.pack(fill=tk.X, pady=20)
        
        self.execute_btn = tk.Button(btn_frame, text="▶ EJECUTAR SHELLCODE", 
                                     command=self.execute_shellcode_thread,
                                     bg='#27ae60', fg='white', font=self.font_title,
                                     activebackground='#2ecc71', padx=20, pady=8)
        self.execute_btn.pack(side=tk.LEFT, padx=10)
        
        self.clear_btn = tk.Button(btn_frame, text="CLEAR LOG", 
                                   command=self.clear_log,
                                   bg='#e67e22', fg='white', font=self.font_normal,
                                   activebackground='#f39c12', padx=15, pady=5)
        self.clear_btn.pack(side=tk.LEFT, padx=10)
        
        # Área de log (texto con scroll)
        log_frame = tk.Frame(main_frame, bg='#2c3e50')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(log_frame, text="Consola de ejecución:", font=self.font_normal, 
                 fg='white', bg='#2c3e50', anchor='w').pack(fill=tk.X)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                   bg='#ecf0f1', fg='#2c3e50',
                                                   font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        
        # Estado en barra inferior
        self.status_var = tk.StringVar()
        self.status_var.set("Listo. Selecciona un archivo .bin")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                              bd=1, relief=tk.SUNKEN, anchor=tk.W,
                              bg='#34495e', fg='white', font=('Segoe UI', 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def log(self, message, is_error=False):
        """Agrega mensaje al área de log con color opcional"""
        self.log_text.insert(tk.END, message + "\n")
        if is_error:
            # Marcar error en rojo
            start = self.log_text.index(tk.END + "-1l linestart")
            end = self.log_text.index(tk.END + "-1l lineend")
            self.log_text.tag_add("error", start, end)
            self.log_text.tag_config("error", foreground="red")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("Log limpiado.")
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo .bin",
            filetypes=[("Binarios Donut", "*.bin"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.log(f"Archivo seleccionado: {filename}")
            self.status_var.set(f"Archivo: {os.path.basename(filename)}")
            
    def execute_shellcode_thread(self):
        """Inicia la ejecución en un hilo separado para no bloquear la GUI"""
        threading.Thread(target=self.execute_shellcode, daemon=True).start()
        
    def execute_shellcode(self):
        bin_path = self.file_path_var.get().strip()
        if not bin_path:
            messagebox.showwarning("Sin archivo", "Por favor selecciona un archivo .bin")
            return
        if not os.path.exists(bin_path):
            messagebox.showerror("Error", "El archivo no existe")
            return
            
        # Deshabilitar botón durante ejecución
        self.execute_btn.config(state=tk.DISABLED, text="EJECUTANDO...")
        self.log("="*50)
        self.log(f"Iniciando carga de shellcode: {bin_path}")
        
        try:
            # Leer el .bin
            with open(bin_path, "rb") as f:
                shellcode = f.read()
            if not shellcode:
                self.log("ERROR: El archivo está vacío", is_error=True)
                return
            self.log(f"[+] Shellcode cargado: {len(shellcode)} bytes")
            
            # Verificar arquitectura del Python
            arch = 'x64' if sys.maxsize > 2**32 else 'x86'
            self.log(f"[*] Python corriendo en modo {arch}")
            
            # Cargar APIs de Windows
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
            
            # Configurar tipos
            kernel32.VirtualAlloc.argtypes = [wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD]
            kernel32.VirtualAlloc.restype = wintypes.LPVOID
            ntdll.RtlMoveMemory.argtypes = [wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t]
            kernel32.CreateThread.argtypes = [wintypes.LPVOID, ctypes.c_size_t, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, wintypes.LPDWORD]
            kernel32.CreateThread.restype = wintypes.HANDLE
            kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            
            # 1. Reservar memoria ejecutable
            self.log("[*] Reservando memoria con VirtualAlloc (RWX)...")
            ptr = kernel32.VirtualAlloc(None, len(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
            if not ptr:
                err = ctypes.get_last_error()
                self.log(f"[-] VirtualAlloc falló. Error: {err} (0x{err:08X})", is_error=True)
                return
            self.log(f"[*] Memoria reservada en: {hex(ptr)}")
            
            # 2. Copiar shellcode
            self.log("[*] Copiando shellcode a memoria...")
            ntdll.RtlMoveMemory(ptr, shellcode, len(shellcode))
            self.log("[+] Shellcode copiado correctamente")
            
            # 3. Crear hilo para ejecutar
            self.log("[*] Creando hilo de ejecución...")
            thread_id = wintypes.DWORD()
            h_thread = kernel32.CreateThread(None, 0, ptr, None, 0, ctypes.byref(thread_id))
            if not h_thread:
                err = ctypes.get_last_error()
                kernel32.VirtualFree(ptr, 0, 0x8000)
                self.log(f"[-] CreateThread falló. Error: {err} (0x{err:08X})", is_error=True)
                return
                
            self.log(f"[+] Shellcode ejecutándose en hilo ID: {thread_id.value}")
            self.log("[*] Esperando a que el shellcode termine (puede que nunca termine si es persistente)...")
            self.status_var.set("Shellcode en ejecución...")
            
            # Opcional: esperar un tiempo o esperar indefinidamente (puede bloquear si el shellcode no termina)
            # Para no congelar la GUI, esperamos en el hilo secundario.
            kernel32.WaitForSingleObject(h_thread, INFINITE)
            kernel32.CloseHandle(h_thread)
            self.log("[+] Hilo de shellcode finalizado.")
            self.status_var.set("Ejecución completada.")
            
        except Exception as e:
            self.log(f"[-] Excepción: {e}", is_error=True)
            self.status_var.set("Error en ejecución")
        finally:
            self.execute_btn.config(state=tk.NORMAL, text="▶ EJECUTAR SHELLCODE")
            self.log("="*50 + "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShellcodeLoaderApp(root)
    root.mainloop()
