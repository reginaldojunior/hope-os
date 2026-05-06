import time

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


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

        self.page_tables[process_name] = {}
        self.allocations[process_name] = (0, num_pages)
        self.free_frames[process_name] = list(range(num_pages))
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
