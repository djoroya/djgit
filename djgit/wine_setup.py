#!/usr/bin/env python3
import argparse
import os
import platform
import shlex
import subprocess
import sys

# ---------- utilidades ----------
def run(cmd, apply=False):
    print("→", cmd)
    if apply:
        subprocess.run(cmd, shell=True, check=True)

def read_os_release():
    info = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if "=" in line:
                    k,v = line.rstrip().split("=",1)
                    info[k] = v.strip('"')
    except FileNotFoundError:
        pass
    return info

def detect_family_and_codename(override_codename=None):
    info = read_os_release()
    id_like = (info.get("ID_LIKE","") + " " + info.get("ID","")).lower()
    family = "ubuntu" if "ubuntu" in id_like else ("debian" if "debian" in id_like else None)
    codename = override_codename or info.get("VERSION_CODENAME")
    return family, codename

def require_root():
    if os.geteuid() != 0:
        print("⚠️  Se requieren privilegios de administrador para instalar paquetes.")
        print("    Vuelve a ejecutar con: sudo", " ".join(map(shlex.quote, sys.argv)))
        sys.exit(1)

def check_wine():
    try:
        out = subprocess.check_output(["bash","-lc","wine --version"], stderr=subprocess.STDOUT, text=True, timeout=5)
        return out.strip()
    except Exception:
        return None

# ---------- comandos ----------
def add_architecture(apply):
    run("dpkg --add-architecture i386", apply)

def add_key_and_repo_ubuntu(codename, apply):
    run('mkdir -p /etc/apt/keyrings', apply)
    run('wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key', apply)
    repo = f'deb [signed-by=/etc/apt/keyrings/winehq-archive.key] https://dl.winehq.org/wine-builds/ubuntu/ {codename} main'
    run(f'bash -lc \'echo "{repo}" > /etc/apt/sources.list.d/winehq-{codename}.list\'', apply)

def add_key_and_repo_debian(codename, apply):
    run('mkdir -p /etc/apt/keyrings', apply)
    run('wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key', apply)
    repo = f'deb [signed-by=/etc/apt/keyrings/winehq-archive.key] https://dl.winehq.org/wine-builds/debian/ {codename} main'
    run(f'bash -lc \'echo "{repo}" > /etc/apt/sources.list.d/winehq-{codename}.list\'', apply)

def apt_update(apply):
    run("apt-get update", apply)

def install_wine(branch, apply, recommends):
    pkg = f"winehq-{branch}"
    # Wine necesita runtime i386 y fuentes comunes
    base = " --install-recommends" if recommends else ""
    run(f"apt-get install -y{base} {pkg}", apply)

def remove_wine(apply):
    cmds = [
        "apt-get purge -y 'winehq-*' 'wine-*' 'winetricks' || true",
        "apt-get autoremove -y",
        "rm -f /etc/apt/sources.list.d/winehq-*.list",
        "apt-get update"
    ]
    for c in cmds:
        run(c, apply)

def show_next_steps(prefix=None):
    print("\n✅ Instalación lista.")
    print("• Ver versión:", "wine --version")
    print("• Crear prefijo limpio (32 bits):")
    print("  WINEARCH=win32 WINEPREFIX=\"$HOME/.wine32\" winecfg")
    if prefix:
        print(f"• Lanzar app con prefijo «{prefix}»:")
        print(f"  WINEPREFIX=\"{prefix}\" wine notepad.exe")

# ---------- main ----------
def main():
    parser = argparse.ArgumentParser(
        description="Instalador Wine 9.x para Ubuntu/Debian (stable|devel|staging). "
                    "Por defecto imprime los pasos (dry-run). Usa --apply para ejecutar."
    )
    parser.add_argument("--branch", choices=["stable","devel","staging"], default="stable",
                        help="Rama de WineHQ a instalar (por defecto: stable)")
    parser.add_argument("--apply", action="store_true",
                        help="Ejecutar comandos (sin esto, solo imprime los pasos)")
    parser.add_argument("--codename", default=None,
                        help="Sobrescribir codename (ej. jammy, noble, bookworm...). Autodetectado si no se define.")
    parser.add_argument("--recommends", action="store_true",
                        help="Instalar también paquetes recomendados (suele venir bien para fuentes/gtk/etc.)")
    parser.add_argument("--remove", action="store_true",
                        help="Eliminar Wine y repos WineHQ del sistema")
    args = parser.parse_args()

    # Información previa
    print(f"💻 Sistema: {platform.system()} {platform.release()}")
    family, codename = detect_family_and_codename(args.codename)

    if args.remove:
        if args.apply:
            require_root()
        print("🧹 Eliminando Wine y repos WineHQ…")
        remove_wine(args.apply)
        return

    current = check_wine()
    if current:
        print(f"ℹ️  Wine detectado: {current}")

    if family not in {"ubuntu","debian"} or not codename:
        print("⚠️  No se pudo detectar familia/codename compatibles automáticamente.")
        print("    Usa --codename (p.ej. --codename noble | jammy | bookworm).")
        if not args.apply:
            return
        # si insiste con --apply sin codename válido, abortamos
        if not codename:
            sys.exit(2)

    if args.apply:
        require_root()

    print(f"🛠  Preparando instalación WineHQ ({args.branch}) para {family} {codename}…")

    # Pasos
    add_architecture(args.apply)
    if family == "ubuntu":
        add_key_and_repo_ubuntu(codename, args.apply)
    else:
        add_key_and_repo_debian(codename, args.apply)
    apt_update(args.apply)
    install_wine(args.branch, args.apply, args.recommends)

    # Resultado
    if args.apply:
        post = check_wine()
        if post:
            print(f"\n🎉 Wine instalado: {post}")
        show_next_steps()

if __name__ == "__main__":
    main()
