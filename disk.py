import os
import platform
import time


class DiskManager:
    @staticmethod
    def list_disks():
        system = platform.system()
        disks = []

        if system == "Darwin":
            result = os.popen("diskutil list").read()
            return result
        elif system == "Linux":
            result = os.popen("lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE").read()
            return result
        elif system == "Windows":
            result = os.popen("wmic diskdrive get model,size,mediatype").read()
            return result
        else:
            return "Sistema operacional não suportado para listagem de discos."

    @staticmethod
    def list_disks_parsed():
        system = platform.system()
        disks = []

        if system == "Darwin":
            try:
                result = os.popen("diskutil list").read()
                lines = result.split('\n')
                for line in lines:
                    if '/dev/disk' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            disk_info = {
                                'device': parts[0] if parts[0].startswith('/dev/') else parts[1],
                                'size': '',
                                'type': ''
                            }
                            for i, part in enumerate(parts):
                                if 'GB' in part or 'TB' in part or 'MB' in part:
                                    disk_info['size'] = part
                                if 'external' in part.lower() or 'internal' in part.lower():
                                    disk_info['type'] = part
                            disks.append(disk_info)
            except Exception as e:
                print(f"  [!] Erro ao listar discos: {e}")

        elif system == "Linux":
            try:
                result = os.popen("lsblk -J").read()
                import json
                data = json.loads(result)
                for block in data.get('blockdevices', []):
                    if block.get('type') == 'disk':
                        disks.append({
                            'device': f"/dev/{block['name']}",
                            'size': block.get('size', 'N/A'),
                            'type': 'disk',
                            'fstype': block.get('fstype', 'N/A')
                        })
            except Exception as e:
                print(f"  [!] Erro ao listar discos: {e}")

        return disks

    @staticmethod
    def format_disk(device, filesystem="FAT32", label="HOPE_OS"):
        print(f"\n  [FORMATAR] Iniciando formatação de {device}")
        print(f"  [FORMATAR] Sistema de arquivos: {filesystem}")
        print(f"  [FORMATAR] Rótulo: {label}")

        print(f"\n╔══════════════════════════════════════════════════╗")
        print(f"  ║  AVISO: Isso apagaria todos os dados em {device} ║")
        print(f"  ║  Como este é um simulador educacional,           ║")
        print(f"  ║  a formatação será apenas simulada.              ║")
        print(f"  ╚══════════════════════════════════════════════════╝")

        from ui import get_input
        confirm = get_input("\n  Confirma a simulação da formatação? (s/N): ")

        if confirm.lower() not in ['s', 'sim', 'y', 'yes']:
            print("\n  [CANCELADO] Operação cancelada pelo usuário.")
            return False

        print(f"\n  [*] Desmontando {device}...")
        time.sleep(0.5)

        print(f"  [*] Criando sistema de arquivos {filesystem}...")
        time.sleep(1)

        steps = [
            "Limpando setores...",
            "Criando tabela de partição...",
            "Formatando partições...",
            "Aplicando sistema de arquivos...",
            "Verificando integridade..."
        ]

        for step in steps:
            print(f"  [*] {step}")
            time.sleep(0.3)

        print(f"\n  [OK] Disco {device} formatado com sucesso!")
        print(f"  [OK] Sistema de arquivos: {filesystem}")
        print(f"  [OK] Rótulo: {label}")
        return True

    @staticmethod
    def get_filesystem_options():
        return {
            "1": {"name": "FAT32", "description": "Compatível com quase todos os sistemas"},
            "2": {"name": "NTFS", "description": "Padrão para Windows, suporte a arquivos grandes"},
            "3": {"name": "exFAT", "description": "Ideal para dispositivos USB e cartões SD"},
            "4": {"name": "EXT4", "description": "Padrão para Linux moderno"},
            "5": {"name": "APFS", "description": "Padrão para macOS moderno"},
            "6": {"name": "HFS+", "description": "Sistema de arquivos legado do macOS"},
        }

    @staticmethod
    def show_disk_info(device):
        system = platform.system()

        print(f"\n╔════════════════════════════════════════════════╗")
        print(f"  ║  INFORMAÇÕES DO DISCO: {device:<24}            ║")
        print(f"  ╚════════════════════════════════════════════════╝")

        if system == "Darwin":
            info = os.popen(f"diskutil info {device}").read()
            print(info)
        elif system == "Linux":
            info = os.popen(f"lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT -d {device}").read()
            print(info)
        else:
            print(f"  Dispositivo: {device}")
            print(f"  Sistema: {system}")
