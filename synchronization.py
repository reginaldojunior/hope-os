import time
import threading


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
