import os
import shutil
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from classifier import ClassificationResult

logger = logging.getLogger("Router")

class FileRouter:
    def __init__(self, log_filename: str = "organizacao_log.json"):
        self.log_filename = log_filename

    def route_file(self, source_path: Path, destination_root: Path, classification: ClassificationResult, dry_run: bool = False) -> Optional[Path]:
        """
        Move e renomeia um arquivo para o destino correto de acordo com a classificação.
        Evita sobreescrever arquivos tratando colisões de nome.
        Retorna o caminho final do arquivo se movido, ou None se dry_run/erro.
        """
        source_path = Path(source_path)
        destination_root = Path(destination_root)
        
        if not source_path.exists():
            logger.error(f"Arquivo de origem não existe: {source_path}")
            return None

        # Determina o diretório de destino
        caminho_rel = classification.caminho_pasta_destino
        if caminho_rel.lower() == "raiz":
            destination_dir = destination_root
        else:
            destination_dir = destination_root / caminho_rel

        # Determina o nome do arquivo final
        nome_higienizado = classification.nome_arquivo_higienizado
        
        # Tratamento de colisão de nomes
        target_path = destination_dir / nome_higienizado
        if target_path.exists() and source_path.resolve() != target_path.resolve():
            stem = target_path.stem
            suffix = target_path.suffix
            counter = 1
            while True:
                new_name = f"{stem} ({counter}){suffix}"
                new_path = destination_dir / new_name
                if not new_path.exists():
                    target_path = new_path
                    break
                counter += 1
            logger.info(f"Colisão de nome detectada. Renomeando '{nome_higienizado}' para '{target_path.name}'")

        # Exibe ação no console
        action_msg = f"[SIMULAÇÃO] Moveria" if dry_run else "Movendo"
        logger.info(f"{action_msg} '{source_path.name}' ➔ '{target_path.relative_to(destination_root.parent) if target_path.is_relative_to(destination_root.parent) else target_path}'")

        if dry_run:
            # Em modo dry-run não criamos pastas nem movemos nada
            self._write_log(destination_root, source_path, target_path, classification, dry_run=True)
            return target_path

        try:
            # Cria a estrutura de diretórios pai se não existir
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            # Se for o mesmo arquivo, não precisa mover
            if source_path.resolve() == target_path.resolve():
                logger.info(f"Arquivo '{source_path.name}' já está no destino correto.")
                return target_path
                
            # Move o arquivo
            shutil.move(str(source_path), str(target_path))
            
            # Grava no log de auditoria
            self._write_log(destination_root, source_path, target_path, classification, dry_run=False)
            
            return target_path
        except Exception as e:
            logger.error(f"Erro ao mover arquivo '{source_path.name}': {str(e)}")
            return None

    def _write_log(self, destination_root: Path, source_path: Path, target_path: Path, classification: ClassificationResult, dry_run: bool):
        """Grava uma entrada no arquivo de log JSON do histórico de organização."""
        # Garante que a pasta raiz do log exista
        destination_root.mkdir(parents=True, exist_ok=True)
        log_path = destination_root / self.log_filename
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "arquivo_original_nome": source_path.name,
            "caminho_origem": str(source_path.absolute()),
            "caminho_destino_relativo": str(target_path.relative_to(destination_root)) if target_path.is_relative_to(destination_root) else str(target_path.absolute()),
            "caminho_destino_absoluto": str(target_path.absolute()),
            "classificado": classification.classificado,
            "materia_codigo": classification.codigo_materia,
            "confianca_percentual": classification.confianca_percentual,
            "justificativa_semantica": classification.justificativa_semantica,
            "dry_run": dry_run
        }
        
        logs = []
        if log_path.exists():
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                # Se o log estiver corrompido, inicia um novo
                logs = []
                
        logs.append(log_entry)
        
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Falha ao escrever no log: {str(e)}")

if __name__ == "__main__":
    # Teste rápido
    router = FileRouter()
    print("Módulo Router carregado com sucesso.")
