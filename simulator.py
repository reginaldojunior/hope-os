#!/usr/bin/env python3
#
#  Hope OS
#
#  Copyright (C) 2026  Hope OS Project
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import clear_screen, print_banner, get_input
from auth import login, current_user
from menus import run_scheduler_menu, run_memory_menu, run_sync_menu, run_user_menu, run_info_menu, run_disk_menu


def main():
    from ui import boot_sequence
    boot_sequence()

    while True:
        if not current_user["username"]:
            if not login():
                continue

        clear_screen()

        print("\n")
        print("  ╔═════════════════════════════════════════════════════════════╗")
        print(f"  ║  HOPE OS v{VERSION}  │  Usuário: {current_user['username']:<12} │  Role: {current_user['role']:<10} ║")
        print("  ╠═════════════════════════════════════════════════════════════╣")
        print("  ║  [1] Escalonamento de Processos                               ║")
        print("  ║  [2] Gerenciamento de Memória                                ║")
        print("  ║  [3] Sincronização de Processos                              ║")
        print("  ║  [4] Gerenciar Usuário                                       ║")
        print("  ║  [5] Sobre o Sistema                                         ║")
        print("  ║  [6] Gerenciamento de Discos                                 ║")
        print("  ║  [0] Sair                                                    ║")
        print("  ╚═════════════════════════════════════════════════════════════╝")

        choice = get_input()

        if choice == "0":
            print("\n  [SHUTDOWN] Encerrando Hope OS...")
            time.sleep(0.5)
            print("  [SHUTDOWN] Sistema encerrado com sucesso.\n")
            break

        clear_screen()

        if choice == "1":
            run_scheduler_menu()
        elif choice == "2":
            run_memory_menu()
        elif choice == "3":
            run_sync_menu()
        elif choice == "4":
            run_user_menu()
        elif choice == "5":
            run_info_menu()
        elif choice == "6":
            run_disk_menu()
        else:
            print("  [!] Opção inválida!")
            time.sleep(1)


if __name__ == "__main__":
    from config import VERSION
    main()
