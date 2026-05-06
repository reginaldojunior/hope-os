import os
import time
from config import VERSION, BUILD


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def boot_sequence():
    clear_screen()

    print("\n")
    print("  ██╗  ██╗ ██████╗ ██████╗ ██████╗     ██████╗  ███████╗")
    print("  ██║  ██║██╔═══██╗██╔═══██╗██╔═══██╗    ██╔═══██╗██╔════╝")
    print("  ███████║███████╔╝██████╔╝██████╔╝      ██║   ██║███████╗")
    print("  ██║  ██║██╔═══╝ ██╔═══╝ ██╔═══╝       ██║   ██║╚════██║")
    print("  ██║  ██║███████╗██║     ██████╗       ╚██████╔╝███████║")
    print("  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═════╝        ╚═════╝ ╚══════╝")
    print("                                                                                              ")
    print("  ════════════════════════════════════════════════════════════════════")
    print(f"  Sistema Operacional Educacional - Versão {VERSION} (Build {BUILD})")

    print("  Disciplina: Sistemas Operacionais")
    print("  ════════════════════════════════════════════════════════════════════")

    print("\n  [BOOT] Inicializando sistema...")
    time.sleep(0.3)
    print("  [BOOT] Carregando módulos do kernel...")
    time.sleep(0.2)
    print("  [BOOT] Verificando memória...")
    time.sleep(0.2)
    print("  [BOOT] Configurando filas de escalonamento...")
    time.sleep(0.2)
    print("  [BOOT] Sistema pronto!")
    time.sleep(0.5)


def print_banner(title):
    print("\n" + "╔" + "═" * 48 + "╗")
    print(f"║{title:^48}║")
    print("╚" + "═" * 48 + "╝")


def print_menu(title, options, show_back=True):
    print_banner(title)
    for i, option in enumerate(options, 1):
        print(f"  [{i}] {option}")
    if show_back:
        print(f"  [0] Voltar")
    print("  " + "─" * 48)


def get_input(prompt="  > "):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return "0"
