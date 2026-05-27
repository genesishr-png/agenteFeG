import os
import sys
import time
import logging
import subprocess
import argparse
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import config

# Configuração do Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Watcher")

class DocumentHandler(FileSystemEventHandler):
    def __init__(self, input_dir: Path, output_dir: Path, dry_run: bool = False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.ignored_extensions = {".ini", ".sys", ".tmp", ".log", ".env", ".gitignore", ".py", ".crdownload", ".part"}
        self.ignored_names = {"desktop.ini", ".ds_store", "organizacao_log.json"}
        self.last_trigger_time = 0
        self.debounce_seconds = 2.0  # Evita disparar múltiplos processos para colagens em massa

    def on_created(self, event):
        self._handle_event(event)

    def on_modified(self, event):
        # Alguns navegadores criam o arquivo vazio e depois escrevem (modificam)
        self._handle_event(event)

    def _handle_event(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in self.ignored_extensions or file_path.name.lower() in self.ignored_names:
            return

        now = time.time()
        if now - self.last_trigger_time < self.debounce_seconds:
            return
            
        self.last_trigger_time = now
        logger.info(f"Modificação detectada no arquivo: '{file_path.name}'. Aguardando estabilização...")
        
        # Debounce: aguarda o arquivo terminar de ser escrito (tamanho não muda mais)
        if file_path.exists():
            try:
                stable = False
                for _ in range(5):
                    size1 = file_path.stat().st_size
                    time.sleep(0.8)
                    if file_path.exists():
                        size2 = file_path.stat().st_size
                        if size1 == size2:
                            stable = True
                            break
                if not stable:
                    logger.warning(f"O arquivo '{file_path.name}' não estabilizou o tamanho. Processando de qualquer forma.")
            except Exception:
                pass
                
        self.trigger_processing()

    def trigger_processing(self):
        logger.info("Disparando classificação automática...")
        try:
            cmd = [
                sys.executable,
                str(Path(__file__).resolve().parent / "main.py"),
                "--input-dir", str(self.input_dir),
                "--output-dir", str(self.output_dir)
            ]
            if self.dry_run:
                cmd.append("--dry-run")
                
            subprocess.run(cmd, check=True)
        except Exception as e:
            logger.error(f"Falha ao executar main.py: {str(e)}")

def start_polling_fallback(handler: DocumentHandler):
    """Fallback em loop caso o Watchdog nativo falhe no SO."""
    logger.info("Iniciando monitoramento via Polling (Pure Python)...")
    last_files = set()
    while True:
        try:
            if not handler.input_dir.exists():
                handler.input_dir.mkdir(parents=True, exist_ok=True)
                
            current_files = set()
            for item in handler.input_dir.iterdir():
                if item.is_file() and item.suffix.lower() not in handler.ignored_extensions and item.name.lower() not in handler.ignored_names:
                    current_files.add(item.name)
                    
            new_files = current_files - last_files
            if new_files:
                logger.info(f"Novos arquivos encontrados via Polling: {new_files}")
                handler.trigger_processing()
                
            last_files = current_files
            time.sleep(4)
        except KeyboardInterrupt:
            logger.info("Serviço de Polling interrompido pelo usuário.")
            break
        except Exception as e:
            logger.error(f"Erro no loop de Polling: {str(e)}")
            time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Serviço Watcher de monitoramento de pastas.")
    parser.add_argument(
        "-i", "--input-dir",
        type=str,
        default=str(config.DEFAULT_INPUT_DIR),
        help="Pasta a monitorar"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=str(config.DEFAULT_OUTPUT_DIR),
        help="Pasta de destino organizada"
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Rodar em modo simulação"
    )
    parser.add_argument(
        "--polling",
        action="store_true",
        help="Força uso do loop de Polling direto em vez de Watchdog nativo"
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    handler = DocumentHandler(input_dir, output_dir, args.dry_run)
    
    logger.info(f"Monitorando a pasta: '{input_dir}'")
    logger.info(f"Organizando na pasta: '{output_dir}'")
    
    if args.polling:
        start_polling_fallback(handler)
        return
        
    # Inicializa o Watchdog
    observer = Observer()
    observer.schedule(handler, path=str(input_dir), recursive=False)
    
    try:
        observer.start()
        logger.info("Serviço Watchdog nativo iniciado com sucesso.")
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error(f"Erro ao iniciar o Watchdog nativo: {str(e)}. Utilizando fallback de Polling.")
        start_polling_fallback(handler)
    except KeyboardInterrupt:
        logger.info("Parando o monitor de pastas...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
