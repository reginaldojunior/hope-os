from ui import clear_screen, print_menu, print_banner, get_input
from auth import has_privilege, check_permission, current_user, USERS
from schedulers import FIFOScheduler, PriorityNonPreemptive, PriorityPreemptive, RoundRobinScheduler
from memory import MemoryManager
from synchronization import DiningPhilosophers, BankAccount, IPCPipe, IPCQueue, SharedMemory
from disk import DiskManager


def run_scheduler_menu():
    if not check_permission("escalonamento"):
        return

    while True:
        print_menu("ESCALONAMENTO DE PROCESSOS", [
            "FIFO (First In, First Out)",
            "Prioridade Não-Preemptiva",
            "Prioridade Preemptiva",
            "Round Robin",
            "Visualizar algoritmos disponíveis"
        ])

        choice = get_input()

        if choice == "0":
            break

        clear_screen()
        print_banner("ESCALONAMENTO")

        try:
            if choice in ["1", "2", "3", "4"]:
                print("  Digite os jobs: id,duração ou id,duração,prioridade")
                print("  Exemplo: 1,4 2,6 3,3")
                jobs_input = get_input("\n  Jobs: ").strip() or "1,4 2,6 3,3"

                if choice == "1":
                    jobs = [(int(j.split(",")[0]), int(j.split(",")[1])) for j in jobs_input.split()]
                    print("\n  [EXECUTANDO FIFO]\n")
                    FIFOScheduler.run(jobs)

                elif choice == "2":
                    jobs = []
                    for j in jobs_input.split():
                        parts = j.split(",")
                        jobs.append((int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 1))
                    print("\n  [EXECUTANDO PRIORIDADE NÃO-PREEMPTIVA]\n")
                    PriorityNonPreemptive.run(jobs)

                elif choice == "3":
                    jobs = []
                    for j in jobs_input.split():
                        parts = j.split(",")
                        jobs.append((int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 1))
                    quantum = int(get_input("  Quantum (padrão=1): ") or "1")
                    print("\n  [EXECUTANDO PRIORIDADE PREEMPTIVA]\n")
                    PriorityPreemptive.run(jobs, quantum)

                elif choice == "4":
                    jobs = [(int(j.split(",")[0]), int(j.split(",")[1])) for j in jobs_input.split()]
                    quantum = int(get_input("  Quantum (padrão=2): ") or "2")
                    print("\n  [EXECUTANDO ROUND ROBIN]\n")
                    RoundRobinScheduler.run(jobs, quantum)

                print("\n  [OK] Concluído!")
                input("\n  Pressione ENTER para continuar...")

            elif choice == "5":
                print("\n╔════════════════════════════════════════════════╗")
                print("  ║        ALGORITMOS DE ESCALONAMENTO             ║")
                print("  ╠════════════════════════════════════════════════╣")
                print("  ║  FIFO           │ Ordem de chegada             ║")
                print("  ║  Prioridade NP  │ Maior prioridade primeiro    ║")
                print("  ║  Prioridade P   │ Com preempção por quantum    ║")
                print("  ║  Round Robin    │ Time-slice circular          ║")
                print("  ╚════════════════════════════════════════════════╝")
                input("\n  Pressione ENTER para continuar...")

        except Exception as e:
            print(f"\n  [!] Erro: {e}")
            input("\n  Pressione ENTER para continuar...")


def run_memory_menu():
    if not check_permission("memoria"):
        return

    mm = None

    while True:
        print_menu("GERENCIAMENTO DE MEMÓRIA", [
            "Inicializar memória",
            "Alocar processo",
            "Liberar processo",
            "Visualizar estado",
            "Compactar memória",
            "Alocar páginas (Paging)",
            "Acessar página",
            "Simular acessos (string de referência)",
            "Simular acessos aleatórios",
            "Ver métricas de página",
            "Gerar gráfico das métricas",
            "Ver algoritmos disponíveis"
        ])

        choice = get_input()

        if choice == "0":
            break

        clear_screen()
        print_banner("GERENCIAMENTO DE MEMÓRIA")

        if choice == "1":
            size = int(get_input("  Tamanho total de blocos (padrão=16): ") or "16")
            mm = MemoryManager(size)
            print(f"\n  [OK] Memória inicializada com {size} blocos")
            mm.print_state()

        elif mm is None:
            print("  [!] Inicialize a memória primeiro (opção 1)")

        elif choice == "2":
            name = get_input("  Nome do processo: ")
            size = int(get_input("  Tamanho (blocos): "))
            mm.allocate(name, size)

        elif choice == "3":
            name = get_input("  Nome do processo: ")
            mm.free(name)

        elif choice == "4":
            mm.print_state()

        elif choice == "5":
            mm.compact()

        elif choice == "6":
            name = get_input("  Nome do processo: ")
            num_pages = int(get_input("  Número de páginas: "))
            mm.allocate_pages(name, num_pages)

        elif choice == "7":
            name = get_input("  Nome do processo: ")
            page_num = int(get_input("  Número da página: "))
            mm.access_page(name, page_num)

        elif choice == "8":
            name = get_input("  Nome do processo: ")
            ref_string = get_input("  String de referência (ex: 1 2 3 1 4 2 1): ")
            mm.simulate_accesses(name, ref_string)

        elif choice == "9":
            name = get_input("  Nome do processo: ")
            num_pages = int(get_input("  Número de páginas (dinâmico, ex: 10): ") or "100")
            num_accesses = int(get_input("  Total de acessos (ex: 10): ") or "100")
            expoente = int(get_input(" Digite o expoente (ex: 2)") or "2")
            mm.simulate_random_accesses(name, num_pages, num_accesses**expoente)

        elif choice == "10":
            print(f"\n  ╔════════════════════════════════════════════╗")
            print(f"  ║           MÉTRICAS DE PÁGINA                 ║")
            print(f"  ╠════════════════════════════════════════════╣")
            print(f"  ║  Page Hits:    {mm.page_hits:>10}                ║")
            print(f"  ║  Page Faults:  {mm.page_faults:>10}                ║")
            print(f"  ║  Hit Rate:     {mm.get_hit_rate():>10.4f}             ║")
            print(f"  ║  Fault Rate:   {mm.get_fault_rate():>10.4f}             ║")
            print(f"  ╚══════════════════════════════════════════════╝")

        elif choice == "11":
            save_path = get_input("  Caminho para salvar (padrão: memory_metrics.png): ") or None
            mm.plot_metrics(save_path)

        elif choice == "12":
            print("\n╔════════════════════════════════════════════════╗")
            print("  ║        TÉCNICAS DE GERENCIAMENTO               ║")
            print("  ╠════════════════════════════════════════════════╣")
            print("  ║  Bitmap     │ Representa blocos livres/ocupados║")
            print("  ║  Lista Livre│ Blocos encadeados                ║")
            print("  ║  First-Fit  │ Primeiro bloco suficiente        ║")
            print("  ║  Compactação│ Une blocos livres adjacentes     ║")
            print("  ║  Paging     │ Alocação por páginas/virtualmem  ║")
            print("  ╚════════════════════════════════════════════════╝")

        print()
        input("  Pressione ENTER para continuar...")


def run_sync_menu():
    if not check_permission("sincronizacao"):
        return

    while True:
        print_menu("SINCRONIZAÇÃO DE PROCESSOS", [
            "Jantar dos Filósofos",
            "Problema do Banco (Lock)",
            "IPC com Pipe",
            "IPC com Queue",
            "Memória Compartilhada"
        ])

        choice = get_input()

        if choice == "0":
            break

        clear_screen()
        print_banner("SINCRONIZAÇÃO")

        try:
            if choice == "1":
                num = int(get_input("  Número de filósofos (padrão=5): ") or "5")
                print(f"\n  [EXECUTANDO JANTAR DOS FILÓSOFOS - {num} FILÓSOFOS]\n")
                DiningPhilosophers(num).run()

            elif choice == "2":
                ops = int(get_input("  Operações por thread (padrão=10): ") or "10")
                print(f"\n  [EXECUTANDO PROBLEMA DO BANCO]\n")
                saldo_final = BankAccount().run(ops)
                print(f"\n  Saldo final: R${saldo_final}")

            elif choice == "3":
                print("\n  [EXECUTANDO IPC COM PIPE]\n")
                IPCPipe.run()

            elif choice == "4":
                print("\n  [EXECUTANDO IPC COM QUEUE]\n")
                IPCQueue.run()

            elif choice == "5":
                print("\n  [EXECUTANDO MEMÓRIA COMPARTILHADA]\n")
                resultado = SharedMemory.run()
                print(f"\n  Valor final do contador: {resultado}")

            print("\n  [OK] Concluído!")
            input("\n  Pressione ENTER para continuar...")

        except Exception as e:
            print(f"\n  [!] Erro: {e}")
            input("\n  Pressione ENTER para continuar...")


def run_user_menu():
    while True:
        print_menu("GERENCIAR USUÁRIOS", [
            f"Usuário atual: {current_user['username']} ({current_user['role']})",
            "Ver privilégios",
            "Logout",
            "Trocar usuário"
        ])

        choice = get_input()

        if choice == "0":
            break

        if choice == "1":
            print(f"\n  Usuário: {current_user['username']}")
            print(f"  Função: {current_user['role']}")
            print(f"  Privilégios: {', '.join(current_user['privileges'])}")

        elif choice == "2":
            print(f"\n  Privilégios concedidos:")
            for priv in current_user['privileges']:
                print(f"    ✓ {priv}")

        elif choice == "3":
            from auth import logout
            logout()
            return

        elif choice == "4":
            from auth import logout
            logout()
            return

        input("\n  Pressione ENTER para continuar...")


def run_info_menu():
    from config import VERSION, BUILD

    while True:
        print_menu("SOBRE O SISTEMA", [
            "Informações do SO",
            "Créditos",
            "Usuários disponíveis"
        ], show_back=False)

        choice = get_input()

        if choice == "0":
            break

        clear_screen()

        if choice == "1":
            print(f"""
   ╔══════════════════════════════════════════════════════╗
   ║              INFORMAÇÕES DO SISTEMA                  ║
   ╠══════════════════════════════════════════════════════╣
   ║  Sistema:       Hope OS                              ║
   ║  Versão:        {VERSION:<36}                        ║
   ║  Build:         {BUILD:<36}                          ║
   ║  Usuário:       {current_user['username']:<36}       ║
   ║  Função:        {current_user['role']:<36}           ║
   ║  Privilégios:   {', '.join(current_user['privileges'][:2]):<36} ║
   ╚══════════════════════════════════════════════════════╝
            """)

        elif choice == "2":
            print("""
   ╔════════════════════════════════════════════════════╗
   ║                    CRÉDITOS                        ║
   ╠════════════════════════════════════════════════════╣
   ║  Desenvolvido para fins educacionais               ║
   ║  Disciplina: Sistemas Operacionais                 ║
   ║                                                    ║
   ║                                                    ║
   ║  Módulos:                                          ║
   ║    - Escalonamento de Processos                    ║
   ║    - Gerenciamento de Memória                      ║
   ║    - Sincronização de Processos                    ║
   ║    - Gerenciamento de Discos                       ║
   ╚════════════════════════════════════════════════════╝
            """)

        elif choice == "3":
            print("  ╔════════════════════════════════════════╗")
            print("  ║         USUÁRIOS DISPONÍVEIS           ║")
            print("  ╠════════════════════════════════════════╣")
            for user, data in USERS.items():
                print(f"  ║  {user:<12} │ {data['role']:<21} ║")
            print("  ╚════════════════════════════════════════╝")
            print("\n  Senhas padrão:")
            for user, data in USERS.items():
                if data['password']:
                    print(f"    {user}: {data['password']}")

        input("\n  Pressione ENTER para continuar...")


def run_disk_menu():
    if not check_permission("disco"):
        return

    disk_manager = DiskManager()

    while True:
        print_menu("GERENCIAMENTO DE DISCOS", [
            "Listar todos os discos",
            "Ver informações de um disco",
            "Formatar disco (FAT32)",
            "Formatar disco (NTFS)",
            "Formatar disco (exFAT)",
            "Formatar disco (EXT4)",
            "Formatar disco (APFS)",
            "Formatar disco (HFS+)",
            "Ver opções de formatação"
        ])

        choice = get_input()

        if choice == "0":
            break

        clear_screen()
        print_banner("GERENCIAMENTO DE DISCOS")

        if choice == "1":
            print("\n╔════════════════════════════════════════════╗")
            print("  ║         LISTA DE DISCOS DISPONÍVEIS        ║")
            print("  ╚════════════════════════════════════════════╝")
            print(disk_manager.list_disks())

        elif choice == "2":
            device = get_input("  Digite o dispositivo (ex: /dev/disk1): ")
            if device:
                disk_manager.show_disk_info(device)

        elif choice in ["3", "4", "5", "6", "7", "8"]:
            device = get_input("  Digite o dispositivo (ex: /dev/disk1): ")
            if device:
                fs_map = {"3": "FAT32", "4": "NTFS", "5": "exFAT", "6": "EXT4", "7": "APFS", "8": "HFS+"}
                filesystem = fs_map.get(choice, "FAT32")
                label = get_input(f"  Rótulo do volume (padrão=HOPE_OS): ") or "HOPE_OS"
                disk_manager.format_disk(device, filesystem, label)

        elif choice == "9":
            print("\n╔════════════════════════════════════════════╗")
            print("  ║           OPÇÕES DE FORMATAÇÃO              ║")
            print("  ╠═════════════════════════════════════════════╣")
            fs_options = disk_manager.get_filesystem_options()
            for key, value in fs_options.items():
                print(f"  ║  [{key}] {value['name']:<10} │ {value['description']:<30} ║")
            print("  ╚════════════════════════════════════════════╝")

        print()
        input("  Pressione ENTER para continuar...")
