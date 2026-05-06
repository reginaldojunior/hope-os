import time
from queue import Queue
import heapq
from collections import deque


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
