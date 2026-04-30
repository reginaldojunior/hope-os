# Hope OS

Simulador educacional de sistema operacional para estudos de **Sistemas Operacionais**.

## Sobre o Projeto

O Hope OS é uma ferramenta interativa de linha de comando que simula conceitos fundamentais de sistemas operacionais, permitindo que estudantes visualizem e experimentem na prática:

- **Escalonamento de Processos** (FIFO, Prioridade, Round Robin)
- **Gerenciamento de Memória** (Bitmap, Alocação, Paginação, Compactação)
- **Sincronização de Processos** (Problema dos Filósofos, Locks, IPC)
- **Controle de Acesso** com diferentes níveis de privilégio

## Funcionalidades

### 1. Escalonamento de Processos
- FIFO (First In, First Out)
- Prioridade Não-Preemptiva
- Prioridade Preemptiva (com quantum)
- Round Robin (com time-slice configurável)

### 2. Gerenciamento de Memória
- Representação de memória via Bitmap
- Alocação e liberação de processos
- Compactação de memória
- Paginação com carregamento sob demanda (Demand Paging)
- Controle de Page Hits e Page Faults
- Visualização de métricas com gráficos (matplotlib)

### 3. Sincronização e IPC
- Problema do Jantar dos Filósofos
- Problema do Banco (controle de concorrência com Lock)
- Comunicação entre processos (IPC) via Pipe
- IPC via Queue
- Memória Compartilhada

### 4. Sistema de Usuários
| Usuário | Senha | Função | Privilégios |
|---------|-------|--------|-------------|
| admin | admin123 | root | todos |
| professor | prof123 | professor | escalonamento, memória, sincronização, logs |
| aluno | aluno123 | student | escalonamento, logs |
| visitante | (vazio) | guest | logs |

## Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes do Python)

## Instalação

1. Clone ou baixe o projeto:
```bash
cd /Users/username/Documents/hope-os
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

Ou instale manualmente os pacotes principais:
```bash
pip install matplotlib numpy requests python-dotenv pdfplumber psutil
```

## Como Executar

Execute o simulador com:
```bash
python simulator.py
```

No Windows:
```bash
python simulator.py
```
Ou se preferir (se o Python estiver no PATH):
```bash
./simulator.py
```

## Instruções de Uso

### 1. Login
Ao iniciar, faça login com um dos usuários disponíveis:

```
Usuário: admin
Senha: admin123
```

Ou use `visitante` (sem senha) para acesso limitado.

### 2. Menu Principal
Após o login, você verá o menu principal com as opções:
- `[1]` Escalonamento de Processos
- `[2]` Gerenciamento de Memória
- `[3]` Sincronização de Processos
- `[4]` Gerenciar Usuário
- `[5]` Sobre o Sistema
- `[0]` Sair

### 3. Exemplos de Uso

#### Escalonamento FIFO:
1. Selecione `[1]` no menu principal
2. Selecione `[1]` para FIFO
3. Digite os jobs no formato `id,duração`:
   ```
   Jobs: 1,4 2,6 3,3
   ```

#### Gerenciamento de Memória:
1. Selecione `[2]` no menu principal
2. Selecione `[1]` para inicializar memória (ex: 16 blocos)
3. Use `[2]` para alocar processos
4. Use `[6]` para alocar páginas (paging)
5. Use `[11]` para gerar gráfico das métricas

#### Sincronização - Jantar dos Filósofos:
1. Selecione `[3]` no menu principal
2. Selecione `[1]` para Jantar dos Filósofos
3. Informe o número de filósofos (padrão: 5)

### 4. Comandos Úteis
- Digite `0` em qualquer menu para voltar
- Pressione `ENTER` para continuar após ver resultados
- No submenu de informações, você pode ver os usuários e senhas disponíveis

## Estrutura do Projeto

```
hope-os/
├── simulator.py        # Arquivo principal com todo o simulador
├── requirements.txt    # Dependências do projeto
└── README.md          # Este arquivo
```

## Dependências Principais

- **matplotlib** - Geração de gráficos para métricas de memória
- **numpy** - Suporte a arrays e cálculos numéricos
- **pdfplumber** - Manipulação de PDFs (caso necessário)
- **psutil** - Informações do sistema
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## Observações

- O simulador é **puramente educacional** e não substitui um sistema operacional real
- As operações de escalonamento e sincronização usam `time.sleep()` para simular o tempo de execução
- O módulo de memória suporta alocação contígua (bitmap) e paginação (demand paging)
- Gráficos são salvos como `memory_metrics.png` no diretório atual

## Créditos

Desenvolvido para a disciplina de **Sistemas Operacionais**.

## Licença

(GNU) Projeto desenvolvido exclusivamente para fins educacionais.
