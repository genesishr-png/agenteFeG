import json
import os
import shutil
from pathlib import Path

log_path = Path(r"C:\Users\genes\OneDrive\Área de Trabalho\edson\OneDrive_2026-05-26\Onda Pro Importadora_9158\01_LLC_LARISSA_8532\organizacao_log.json")

if not log_path.exists():
    print("Arquivo de log não encontrado. O rollback não pôde ser executado.")
    exit(1)

try:
    with open(log_path, "r", encoding="utf-8") as f:
        logs = json.load(f)
except Exception as e:
    print(f"Erro ao ler arquivo de log: {str(e)}")
    exit(1)

print(f"Lendo {len(logs)} entradas de log...")

count = 0
for entry in reversed(logs):
    # Só desfazemos execuções reais
    if entry.get("dry_run") is True:
        continue
        
    orig_path = Path(entry["caminho_origem"])
    dest_path = Path(entry["caminho_destino_absoluto"])
    
    if dest_path.exists():
        # Recria a pasta original se ela tiver sido removida pela rotina de limpeza
        orig_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Restaurando: '{dest_path.name}' -> '{orig_path.name}'")
        shutil.move(str(dest_path), str(orig_path))
        count += 1
    else:
        print(f"Aviso: Arquivo de destino não encontrado para restaurar: '{dest_path}'")

print(f"\nRollback concluído! {count} arquivos restaurados para suas pastas e nomes originais.")

# Remove o arquivo de log para começarmos do zero
if log_path.exists():
    os.remove(log_path)
