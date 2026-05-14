#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ctypes
import threading
import os

MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40

class ShellcodeRunnerApp:
    def __init__(self, root):
        self.root = root
        root.title("Shellcode Executor - RAM")
        root.geometry("500x400")
        root.resizable(True, True)

        # Frame principal
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Ruta del archivo
        tk.Label(frame, text="Archivo .bin con shellcode:").pack(anchor="w")
        self.path_var = tk.StringVar()
        entry_path = tk.Entry(frame, textvariable=self.path_var, width=40)
        entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        btn_browse = tk.Button(frame, text="Examinar", command=self.browse_file)
        btn_browse.pack(side=tk.RIGHT)

        # Botón ejecutar
        self.btn_ejecutar = tk.Button(frame, text="Ejecutar shellcode en RAM", command=self.ejecutar, bg="lightgreen")
        self.btn_ejecutar.pack(pady=10)

        # Log
        tk.Label(frame, text="Consola:").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(frame, height=15, state='disabled')
        self.log.pack(fill=tk.BOTH, expand=True)

        # Si se pasa argumento desde línea de comandos, cargarlo
        import sys
        if len(sys.argv) > 1:
            self.path_var.set(sys.argv[1])

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Bin files", "*.bin"), ("All files", "*.*")])
        if filename:
            self.path_var.set(filename)

    def log_message(self, msg, color="black"):
        self.log.config(state='normal')
        self.log.insert(tk.END, msg + "\n")
        self.log.tag_config(color, foreground=color)
        self.log.insert(tk.END, "", color)
        self.log.see(tk.END)
        self.log.config(state='disabled')
        self.root.update()

    def ejecutar(self):
        ruta = self.path_var.get().strip()
        if not ruta:
            messagebox.showerror("Error", "Selecciona un archivo .bin")
            return
        if not os.path.exists(ruta):
            messagebox.showerror("Error", f"Archivo no encontrado: {ruta}")
            return

        self.btn_ejecutar.config(state='disabled', text="Ejecutando...")
        self.log_message(f"[*] Cargando shellcode desde: {ruta}", "blue")
        # Ejecutar en hilo separado para no bloquear la GUI
        thread = threading.Thread(target=self._ejecutar_shellcode, args=(ruta,), daemon=True)
        thread.start()

    def _ejecutar_shellcode(self, ruta):
        try:
            with open(ruta, "rb") as f:
                shellcode = f.read()
            if not shellcode:
                self.log_message("[-] El archivo está vacío", "red")
                return
            self.log_message(f"[+] Shellcode cargado: {len(shellcode)} bytes", "green")

            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            ptr = kernel32.VirtualAlloc(None, len(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
            if not ptr:
                self.log_message("[-] VirtualAlloc falló", "red")
                return
            ctypes.memmove(ptr, shellcode, len(shellcode))
            self.log_message("[*] Ejecutando shellcode en memoria...", "orange")
            # Ejecutar shellcode (esto puede cambiar el flujo, mostrará la ventana del payload)
            func = ctypes.CFUNCTYPE(None)(ptr)
            func()
            self.log_message("[+] Shellcode finalizado", "green")
        except Exception as e:
            self.log_message(f"[-] Error: {e}", "red")
        finally:
            self.btn_ejecutar.config(state='normal', text="Ejecutar shellcode en RAM")

if __name__ == "__main__":
    root = tk.Tk()
    app = ShellcodeRunnerApp(root)
    root.mainloop()