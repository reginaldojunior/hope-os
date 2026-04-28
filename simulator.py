#!/usr/bin/env python3
#
#  Mackenzie OS
#
#  Copyright (C) 2026  Mackenzie Universidade Presbiteriana
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
import threading
import time
import heapq
import getpass
from queue import Queue
from collections import deque

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSION = "0.0.1"
BUILD = "2026.04.01"

USERS = {
    "admin": {"password": "admin123", "role": "root", "privileges": ["all"]},
    "professor": {"password": "prof123", "role": "professor", "privileges": ["escalonamento", "memoria", "sincronizacao", "view_logs"]},
    "aluno": {"password": "aluno123", "role": "student", "privileges": ["escalonamento", "view_logs"]},
    "visitante": {"password": "", "role": "guest", "privileges": ["view_logs"]},
}

current_user = {"username": None, "role": None, "privileges": []}

class FIFOScheduler:
    @staticmethod
    def run(jobs):
        fila = Queue()
        for job_id, duracao in jobs:
            fila.put((job_id, duracao))
        
        results = []
        while not fila.empty():
            id_job, duracao = fila.get()
            print(f"  [JOB-{id_job}] Iniciado (duração {duracao}s)")
            time.sleep(0.5)
            print(f"  [JOB-{id_job}] Finalizado")
            results.append((id_job, "finalizado"))
        return results

class PriorityNonPreemptive:
    @staticmethod
    def run(jobs):
        fila = []
        for job_id, tempo, prioridade in jobs:
            heapq.heappush(fila, (prioridade, job_id, tempo))
        
        results = []
        while fila:
            prioridade, job_id, tempo = heapq.heappop(fila)
            print(f"  [JOB-{job_id}] Prioridade {prioridade} - Iniciado")
            time.sleep(0.5)
            print(f"  [JOB-{job_id}] Finalizado")
            results.append((job_id, prioridade, "finalizado"))
        return results

class PriorityPreemptive:
    @staticmethod
    def run(jobs, quantum=1):
        fila = [(p, j, t) for j, t, p in jobs]
        heapq.heapify(fila)
        
        results = []
        while fila:
            prioridade, job_id, tempo = heapq.heappop(fila)
            execucao = min(quantum, tempo)
            print(f"  [JOB-{job_id}] Prioridade {prioridade} - Executando {execucao}s")
            time.sleep(0.3)
            tempo -= execucao
            if tempo > 0:
                heapq.heappush(fila, (prioridade, job_id, tempo))
            else:
                print(f"  [JOB-{job_id}] Finalizado")
                results.append((job_id, "finalizado"))
        return results

class RoundRobinScheduler:
    @staticmethod
    def run(jobs, quantum=1):
        fila = deque([{"id": j, "tempo": t} for j, t in jobs])
        
        results = []
        while fila:
            job = fila.popleft()
            execucao = min(quantum, job["tempo"])
            print(f"  [JOB-{job['id']}] Executando {execucao}s (quantum={quantum})")
            time.sleep(0.3)
            job["tempo"] -= execucao
            if job["tempo"] > 0:
                fila.append(job)
            else:
                print(f"  [JOB-{job['id']}] Concluído")
                results.append((job["id"], "finalizado"))
        return results

class MemoryManager:
    def __init__(self, total_blocks):
        self.total_blocks = total_blocks
        self.bitmap = [0] * total_blocks
        self.allocations = {}
        self.page_hits = 0
        self.page_faults = 0
        self.page_tables = {}
        self.free_frames = {}
    
    def print_state(self):
        print(f"  Bitmap:  {' '.join(str(b) for b in self.bitmap)}")
        print(f"           {''.join(['█' if b else '░' for b in self.bitmap])}")
        free_blocks = self.bitmap.count(0)
        used_blocks = self.total_blocks - free_blocks
        print(f"  Memória: {free_blocks} livres | {used_blocks} ocupados | Total: {self.total_blocks}")
        if self.allocations:
            print(f"  Alocações:")
            for name, (start, size) in self.allocations.items():
                print(f"    - {name}: blocos [{start}-{start+size-1}] ({size} blocos)")
        if self.page_hits + self.page_faults > 0:
            print(f"  Page Hits: {self.page_hits} | Page Faults: {self.page_faults}")
            print(f"  Hit Rate: {self.get_hit_rate():.4f} | Fault Rate: {self.get_fault_rate():.4f}")
    
    def allocate(self, process_name, size):
        if size > self.total_blocks:
            print(f"  [!] Erro: tamanho maior que memória total")
            return None
        
        for i in range(len(self.bitmap) - size + 1):
            if self.bitmap[i:i+size] == [0] * size:
                for j in range(i, i + size):
                    self.bitmap[j] = 1
                self.allocations[process_name] = (i, size)
                print(f"  [OK] '{process_name}' alocado: blocos [{i}-{i+size-1}]")
                return i
        print(f"  [!] Erro: sem espaço suficiente")
        return None
    
    def free(self, process_name):
        if process_name in self.allocations:
            start, size = self.allocations[process_name]
            for j in range(start, start + size):
                self.bitmap[j] = 0
            del self.allocations[process_name]
            print(f"  [OK] Liberado: blocos [{start}-{start+size-1}]")
        else:
            print(f"  [!] Erro: processo '{process_name}' não encontrado")
    
    def compact(self):
        print("  [*] Executando compactação...")
        new_bitmap = [0] * self.total_blocks
        pos = 0
        for i, val in enumerate(self.bitmap):
            if val == 1:
                new_bitmap[pos] = 1
                pos += 1
        
        old_allocations = self.allocations.copy()
        self.allocations.clear()
        for name, (start, size) in old_allocations.items():
            self.allocations[name] = (pos, size)
            pos += size
        
        self.bitmap = new_bitmap
        print("  [OK] Compactação concluída")

    def allocate_pages(self, process_name, num_pages):
        if num_pages > self.total_blocks:
            print(f"  [!] Erro: páginas solicitadas maior que memória total")
            return None
        
        if process_name in self.page_tables:
            print(f"  [!] Erro: '{process_name}' já tem páginas alocadas")
            return None
        
        free_frames = [i for i, b in enumerate(self.bitmap) if b == 0]
        if len(free_frames) < num_pages:
            print(f"  [!] Erro: memória insuficiente para {num_pages} páginas")
            return None
        
        for i in range(num_pages):
            frame = free_frames[i]
            self.bitmap[frame] = 1
        
        self.page_tables[process_name] = {}  # Começa vazia (demand paging)
        self.allocations[process_name] = (0, num_pages)
        self.free_frames[process_name] = list(range(num_pages))  # Frames disponíveis
        print(f"  [OK] '{process_name}' alocado com {num_pages} frames (carregamento sob demanda)")
        return {}

    def access_page(self, process_name, page_num):
        if process_name not in self.page_tables:
            print(f"  [!] Erro: '{process_name}' não tem páginas alocadas")
            return False
        
        page_table = self.page_tables[process_name]
        if page_num in page_table:
            self.page_hits += 1
            print(f"  [HIT] Página {page_num} de '{process_name}' está no frame {page_table[page_num]}")
            return True
        else:
            self.page_faults += 1
            print(f"  [FAULT] Página {page_num} de '{process_name}' não está na memória")
            return False

    def simulate_accesses(self, process_name, reference_string):
        if process_name not in self.page_tables:
            print(f"  [!] Erro: '{process_name}' não tem páginas alocadas")
            return
        
        print(f"\n  [SIMULAÇÃO] Acessando páginas para '{process_name}'")
        print(f"  String de referência: {reference_string}\n")
        
        page_nums = [int(x) for x in reference_string.split()]
        
        for i, page_num in enumerate(page_nums):
            print(f"  Passo {i+1}: Acessando página {page_num}", end=" -> ")
            self.access_page(process_name, page_num)
        
        print(f"\n  [RESULTADO] Total: {len(page_nums)} acessos | Hits: {self.page_hits} | Faults: {self.page_faults}")
        print(f"  Hit Rate: {self.get_hit_rate():.2%} | Fault Rate: {self.get_fault_rate():.2%}")

    def simulate_random_accesses(self, process_name, num_virtual_pages, num_accesses):
        import random
        
        if process_name not in self.page_tables:
            print(f"  [!] Erro: '{process_name}' não tem páginas alocadas")
            return
        
        page_table = self.page_tables[process_name]
        frames = self.free_frames.get(process_name, [])
        max_pages_in_memory = len(frames)
        
        print(f"\n  [SIMULAÇÃO ALEATÓRIA] Acessando '{process_name}'")
        print(f"  Espaço virtual: {num_virtual_pages} páginas | Memória física: {max_pages_in_memory} frames")
        print(f"  Total de acessos: {num_accesses}\n")
        print(f"  [*] Páginas serão carregadas sob demanda (demand paging)\n")
        
        for i in range(num_accesses):
            page_num = random.randint(0, num_virtual_pages - 1)
            
            if page_num in page_table:
                self.page_hits += 1
                print(f"  [{i+1}] HIT - Página {page_num} no frame {page_table[page_num]}")
            else:
                self.page_faults += 1
                print(f"  [{i+1}] FAULT - Página {page_num}", end="")
                
                if len(page_table) < max_pages_in_memory:
                    frame = frames[len(page_table)]
                    page_table[page_num] = frame
                    print(f" -> Carregada no frame {frame}")
                else:
                    print(f" -> Memória cheia (requer substituição)")
        
        print(f"\n  [RESULTADO] Total: {num_accesses} acessos | Hits: {self.page_hits} | Faults: {self.page_faults}")
        print(f"  Hit Rate: {self.get_hit_rate():.2%} | Fault Rate: {self.get_fault_rate():.2%}")

    def get_hit_rate(self):
        total = self.page_hits + self.page_faults
        return self.page_hits / total if total > 0 else 0

    def get_fault_rate(self):
        total = self.page_hits + self.page_faults
        return self.page_faults / total if total > 0 else 0

    def plot_metrics(self, save_path=None):
        if not MATPLOTLIB_AVAILABLE:
            print("  [!] Erro: matplotlib não instalado. Instale com: pip install matplotlib")
            return
        
        if self.page_hits + self.page_faults == 0:
            print("  [!] Nenhum acesso à página registrado ainda")
            return
        
        labels = ['Page Hits', 'Page Faults']
        values = [self.page_hits, self.page_faults]
        colors = ['green', 'red']
        
        fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(10, 4))
        
        ax1.bar(labels, values, color=colors)
        ax1.set_title('Page Hits vs Page Faults')
        ax1.set_ylabel('Quantidade')
        for i, v in enumerate(values):
            ax1.text(i, v + 0.5, str(v), ha='center')
        
        ax2.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Proporção de Hits e Faults')
        
        hit_rate = self.get_hit_rate()
        fault_rate = self.get_fault_rate()
        
        plt.suptitle(f'Métricas de Memória - Hit Rate: {hit_rate:.2%} | Fault Rate: {fault_rate:.2%}')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"  [OK] Gráfico salvo em: {save_path}")
        else:
            plt.savefig('memory_metrics.png')
            print(f"  [OK] Gráfico salvo em: memory_metrics.png")
        
        plt.close()

class DiningPhilosophers:
    def __init__(self, num=5):
        self.num = num
        self.forks = [threading.Lock() for _ in range(num)]
    
    def run(self, iterations=1):
        results = []
        
        def filosofo(id):
            esquerda = self.forks[id]
            direita = self.forks[(id + 1) % self.num]
            
            print(f"  [FIL-{id}] Pensando...")
            time.sleep(0.2)
            
            print(f"  [FIL-{id}] Faminto")
            
            esquerda.acquire()
            print(f"  [FIL-{id}] Pegou garfo esquerdo")
            
            direita.acquire()
            print(f"  [FIL-{id}] Comendo!")
            time.sleep(0.2)
            
            direita.release()
            esquerda.release()
            print(f"  [FIL-{id}] Liberou garfos")
        
        threads = []
        for i in range(self.num):
            t = threading.Thread(target=filosofo, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return results

class BankAccount:
    def __init__(self):
        self.saldo = 2000
        self.lock = threading.Lock()
    
    def run(self, operations=10):
        self.saldo = 2000
        
        def sacar(nome, qtd):
            for _ in range(qtd):
                self.lock.acquire()
                saldo_atual = self.saldo
                time.sleep(0.01)
                self.saldo = saldo_atual - 10
                print(f"  [{nome}] Saque R$10 | Saldo: R${self.saldo}")
                self.lock.release()
        
        def depositar(nome, qtd):
            for _ in range(qtd):
                self.lock.acquire()
                saldo_atual = self.saldo
                time.sleep(0.01)
                self.saldo = saldo_atual + 10
                print(f"  [{nome}] Depósito R$10 | Saldo: R${self.saldo}")
                self.lock.release()
        
        t1 = threading.Thread(target=sacar, args=("Caixa-1", operations))
        t2 = threading.Thread(target=sacar, args=("Caixa-2", operations))
        t3 = threading.Thread(target=depositar, args=("Caixa-3", operations))
        
        t1.start()
        t2.start()
        t3.start()
        
        t1.join()
        t2.join()
        t3.join()
        
        return self.saldo

class IPCPipe:
    @staticmethod
    def run():
        from multiprocessing import Process, Pipe
        
        def processo_a(conn):
            print("  [PIPE-A] Enviando dados...")
            conn.send("Olá do Processo A")
            resposta = conn.recv()
            print(f"  [PIPE-A] Recebeu: {resposta}")
        
        def processo_b(conn):
            msg = conn.recv()
            print(f"  [PIPE-B] Recebeu: {msg}")
            time.sleep(0.2)
            conn.send("Resposta do Processo B")
        
        conn1, conn2 = Pipe()
        p1 = Process(target=processo_a, args=(conn1,))
        p2 = Process(target=processo_b, args=(conn2,))
        
        p1.start()
        p2.start()
        
        p1.join()
        p2.join()
        
        return True

class IPCQueue:
    @staticmethod
    def run():
        from multiprocessing import Process, Queue
        
        def produtor(fila, count=3):
            for i in range(count):
                job = f"Job-{i}"
                print(f"  [PROD] Enviando {job}")
                fila.put(job)
                time.sleep(0.3)
            fila.put(None)
        
        def consumidor(fila):
            while True:
                job = fila.get()
                if job is None:
                    print("  [CONS] Finalizando")
                    break
                print(f"  [CONS] Processando {job}")
                time.sleep(0.2)
        
        fila = Queue()
        p1 = Process(target=produtor, args=(fila,))
        p2 = Process(target=consumidor, args=(fila,))
        
        p1.start()
        p2.start()
        
        p1.join()
        p2.join()
        
        return True

class SharedMemory:
    @staticmethod
    def run():
        from multiprocessing import Process, Value
        import ctypes
        
        contador = Value(ctypes.c_int, 0)
        
        def incrementar(nome, qtd):
            for _ in range(qtd):
                with contador.get_lock():
                    contador.value += 1
                    print(f"  [{nome}] contador = {contador.value}")
                time.sleep(0.1)
        
        p1 = Process(target=incrementar, args=("Proc-A", 5))
        p2 = Process(target=incrementar, args=("Proc-B", 5))
        
        p1.start()
        p2.start()
        
        p1.join()
        p2.join()
        
        return contador.value

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def has_privilege(priv):
    if "all" in current_user["privileges"]:
        return True
    return priv in current_user["privileges"]

def boot_sequence():
    clear_screen()
    
    print("\n")
    print("  ███╗   ███╗ █████╗  ██████╗ ██╗  ██╗     ██████╗  ███████╗")
    print("  ████╗ ████║██╔══██╗██╔════╝ ██║  ██║    ██╔═══██╗██╔════╝")
    print("  ██╔████╔██║███████║██║      █████║      ██║   ██║███████╗")
    print("  ██║╚██╔╝██║██╔══██║██║      ██╔══██║    ██║   ██║╚════██║")
    print("  ██║ ╚═╝ ██║██║  ██║╚██████  ██║  ██║    ╚██████╔╝███████║")
    print("  ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚══════╝")
    print("                                                                                              ")
    print("  ════════════════════════════════════════════════════════════════════")
    print(f"  Sistema Operacional Educacional - Versão {VERSION} (Build {BUILD})")
    print("  Mackenzie Universidade Presbiteriana")
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

def login():
    clear_screen()
    
    print("\n")
    print("  ┌────────────────────────────────────────┐")
    print("  │         MACKENZIE OS LOGIN             │")
    print("  └────────────────────────────────────────┘")
    print()
    
    username = input("  Usuário: ").strip()
    
    if username not in USERS:
        print("\n  [!] Usuário não encontrado!")
        time.sleep(1)
        return False
    
    user_data = USERS[username]
    
    if user_data["password"]:
        password = getpass.getpass("  Senha: ")
        if password != user_data["password"]:
            print("\n  [!] Senha incorreta!")
            time.sleep(1)
            return False
    
    current_user["username"] = username
    current_user["role"] = user_data["role"]
    current_user["privileges"] = user_data["privileges"]
    
    clear_screen()
    print("\n")
    print("  ┌────────────────────────────────────────┐")
    print(f"  │  Login bem-vindo, {username.upper():<20} │")
    print(f"  │  Função: {user_data['role']:<28} │")
    print("  └────────────────────────────────────────┘")
    
    print(f"\n  Permissões: {', '.join(current_user['privileges'])}")
    print()
    input("  Pressione ENTER para continuar...")
    
    return True

def logout():
    current_user["username"] = None
    current_user["role"] = None
    current_user["privileges"] = []
    print("\n  [LOGOUT] Sessão encerrada.")
    time.sleep(1)

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

def check_permission(feature):
    if not has_privilege(feature):
        print(f"\n  [!] Sem permissão para acessar '{feature}'")
        print(f"  [!] Requer privilégios: {feature}")
        time.sleep(1)
        return False
    return True

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
                print("\n  ╔════════════════════════════════════════════════╗")
                print("  ║        ALGORITMOS DE ESCALONAMENTO             ║")
                print("  ╠════════════════════════════════════════════════╣")
                print("  ║  FIFO           │ Ordem de chegada              ║")
                print("  ║  Prioridade NP  │ Maior prioridade primeiro     ║")
                print("  ║  Prioridade P   │ Com preempção por quantum     ║")
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
            print("\n  ╔════════════════════════════════════════════════╗")
            print("  ║        TÉCNICAS DE GERENCIAMENTO             ║")
            print("  ╠════════════════════════════════════════════════╣")
            print("  ║  Bitmap      │ Representa blocos livres/ocupados║")
            print("  ║  Lista Livre │ Blocos encadeados              ║")
            print("  ║  First-Fit  │ Primeiro bloco suficiente       ║")
            print("  ║  Compactação│ Une blocos livres adjacentes     ║")
            print("  ║  Paging     │ Alocação por páginas/virtualmem ║")
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
            logout()
            return
        
        elif choice == "4":
            logout()
            return
        
        input("\n  Pressione ENTER para continuar...")

def run_info_menu():
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
  ║              INFORMAÇÕES DO SISTEMA                 ║
  ╠══════════════════════════════════════════════════════╣
  ║  Sistema:       Mackenzie OS                         ║
  ║  Versão:        {VERSION:<36} ║
  ║  Build:         {BUILD:<36} ║
  ║  Usuário:       {current_user['username']:<36} ║
  ║  Função:        {current_user['role']:<36} ║
  ║  Privilégios:   {', '.join(current_user['privileges'][:2]):<36} ║
  ╚══════════════════════════════════════════════════════╝
            """)
        
        elif choice == "2":
            print("""
  ╔══════════════════════════════════════════════════════╗
  ║                    CRÉDITOS                         ║
  ╠══════════════════════════════════════════════════════╣
  ║  Desenvolvido para fins educacionais                ║
  ║  Disciplina: Sistemas Operacionais                  ║
  ║                                                      ║
  ║  Mackenzie Universidade Presbiteriana               ║
  ║                                                      ║
  ║  Módulos:                                           ║
  ║    - Escalonamento de Processos                     ║
  ║    - Gerenciamento de Memória                       ║
  ║    - Sincronização de Processos                     ║
  ╚══════════════════════════════════════════════════════╝
            """)
        
        elif choice == "3":
            print("  ╔══════════════════════════════════════════╗")
            print("  ║         USUÁRIOS DISPONÍVEIS            ║")
            print("  ╠══════════════════════════════════════════╣")
            for user, data in USERS.items():
                print(f"  ║  {user:<12} │ {data['role']:<21} ║")
            print("  ╚══════════════════════════════════════════╝")
            print("\n  Senhas padrão:")
            for user, data in USERS.items():
                if data['password']:
                    print(f"    {user}: {data['password']}")
        
        input("\n  Pressione ENTER para continuar...")

def main():
    boot_sequence()
    
    while True:
        if not current_user["username"]:
            if not login():
                continue
        
        clear_screen()
        
        print("\n")
        print("  ╔═══════════════════════════════════════════════════════════════╗")
        print(f"  ║  MACKENZIE OS v{VERSION}  │  Usuário: {current_user['username']:<12} │  Role: {current_user['role']:<10} ║")
        print("  ╠═══════════════════════════════════════════════════════════════╣")
        print("  ║  [1] Escalonamento de Processos                               ║")
        print("  ║  [2] Gerenciamento de Memória                                ║")
        print("  ║  [3] Sincronização de Processos                              ║")
        print("  ║  [4] Gerenciar Usuário                                       ║")
        print("  ║  [5] Sobre o Sistema                                         ║")
        print("  ║  [0] Sair                                                    ║")
        print("  ╚═══════════════════════════════════════════════════════════════╝")
        
        choice = get_input()
        
        if choice == "0":
            print("\n  [SHUTDOWN] Encerrando Mackenzie OS...")
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
        else:
            print("  [!] Opção inválida!")
            time.sleep(1)

if __name__ == "__main__":
    main()
