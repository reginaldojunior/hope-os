import getpass
import time

USERS = {
    "admin": {"password": "admin123", "role": "root", "privileges": ["all"]},
    "professor": {"password": "prof123", "role": "professor", "privileges": ["escalonamento", "memoria", "sincronizacao", "disco", "view_logs"]},
    "aluno": {"password": "aluno123", "role": "student", "privileges": ["escalonamento", "view_logs"]},
    "visitante": {"password": "", "role": "guest", "privileges": ["view_logs"]},
}

current_user = {"username": None, "role": None, "privileges": []}


def has_privilege(priv):
    if "all" in current_user["privileges"]:
        return True
    return priv in current_user["privileges"]


def check_permission(feature):
    if not has_privilege(feature):
        print(f"\n  [!] Sem permissão para acessar '{feature}'")
        print(f"  [!] Requer privilégios: {feature}")
        time.sleep(1)
        return False
    return True


def login():
    from ui import clear_screen

    clear_screen()

    print("\n")
    print("  ┌────────────────────────────────────────┐")
    print("  │         HOPE OS LOGIN                  │")
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
    print("  ┌──────────────────────────────────────────┐")
    print(f" │  Login bem-vindo, {username.upper():<20} │")
    print(f" │  Função: {user_data['role']:<28}         │")
    print("  └──────────────────────────────────────────┘")

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
