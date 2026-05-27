import argparse
import sys
import shutil
import logging
from pathlib import Path

import config
from extractor import DocumentExtractor
from classifier import DocumentClassifier
from router import FileRouter

# Configuração do Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AgenteRAG")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Agente Inteligente RAG para Organização e Higienização de Documentos Jurídicos."
    )
    parser.add_argument(
        "-i", "--input-dir",
        type=str,
        default=str(config.DEFAULT_INPUT_DIR),
        help=f"Diretório contendo os arquivos desorganizados (Padrão: {config.DEFAULT_INPUT_DIR})"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=str(config.DEFAULT_OUTPUT_DIR),
        help=f"Diretório raiz do cliente para organização (Padrão: {config.DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Simula o processamento exibindo as classificações planejadas sem alterar arquivos físicos."
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    dry_run = args.dry_run
    
    logger.info("=== Iniciando Agente de Organização Jurídica RAG ===")
    if dry_run:
        logger.info("--- MODO DE SIMULAÇÃO (DRY RUN) ATIVO ---")
        
    # Valida configurações básicas (.env e glossário)
    warnings = config.validate_config()
    for warning in warnings:
        logger.warning(warning)
        
    # Certifica a existência dos diretórios
    if not input_dir.exists():
        logger.info(f"Criando diretório de entrada: {input_dir}")
        input_dir.mkdir(parents=True, exist_ok=True)
        
    if not output_dir.exists() and not dry_run:
        logger.info(f"Criando diretório de saída: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
    # Lista arquivos no diretório de entrada
    ignored_extensions = {".ini", ".sys", ".tmp", ".log", ".env", ".gitignore", ".py"}
    ignored_names = {"desktop.ini", ".ds_store", "organizacao_log.json"}
    
    files_to_process = []
    zips_to_cleanup = []
    temp_dirs_to_cleanup = []
    
    # 1. Varre arquivos de entrada, tratando ZIPs primeiro
    for item in list(input_dir.iterdir()):
        if not item.is_file() or item.name.lower() in ignored_names or item.suffix.lower() in ignored_extensions:
            continue
            
        if item.suffix.lower() == ".zip":
            logger.info(f"Detectado arquivo compactado: '{item.name}'. Descompactando...")
            extracted = DocumentExtractor.extract_zip(item, input_dir)
            if extracted:
                files_to_process.extend(extracted)
                zips_to_cleanup.append(item)
                # O diretório temporário é a pasta pai do primeiro arquivo extraído
                temp_dirs_to_cleanup.append(extracted[0].parent)
                logger.info(f"Extraídos {len(extracted)} arquivos do zip '{item.name}'.")
            else:
                logger.warning(f"Nenhum arquivo válido extraído do zip '{item.name}'.")
        else:
            files_to_process.append(item)
            
    if not files_to_process:
        logger.info(f"Nenhum arquivo elegível para processamento encontrado em: {input_dir}")
        logger.info("=== Processamento concluído (0 arquivos) ===")
        return
        
    logger.info(f"Encontrados {len(files_to_process)} arquivos para processar.")
    
    # Inicializa os componentes
    classifier = DocumentClassifier()
    router = FileRouter()
    
    # Estatísticas
    stats = {
        "total": len(files_to_process),
        "classificados": 0,
        "fallback_raiz": 0,
        "erros": 0
    }
    
    for i, file_path in enumerate(files_to_process, 1):
        logger.info(f"[{i}/{stats['total']}] Processando: '{file_path.name}'...")
        
        try:
            # 1. Extração de texto
            extraction = DocumentExtractor.extract_text(file_path, max_pages=config.MAX_PDF_PAGES_TO_EXTRACT)
            if extraction["error"]:
                logger.error(f"Erro na extração de '{file_path.name}': {extraction['error']}")
            
            # 2. Classificação IA
            classification = classifier.classify_document(
                file_path=file_path,
                extracted_text=extraction["text"],
                is_scanned=extraction["is_scanned"],
                mime_type=extraction["mime_type"]
            )
            
            # 3. Roteamento
            final_path = router.route_file(
                source_path=file_path,
                destination_root=output_dir,
                classification=classification,
                dry_run=dry_run
            )
            
            if final_path:
                if classification.classificado:
                    stats["classificados"] += 1
                else:
                    stats["fallback_raiz"] += 1
            else:
                stats["erros"] += 1
                
        except Exception as e:
            logger.error(f"Falha ao processar arquivo '{file_path.name}': {str(e)}")
            stats["erros"] += 1
            
    # Limpeza de arquivos temporários e ZIPs originais (somente em modo real)
    if not dry_run:
        for temp_dir in temp_dirs_to_cleanup:
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Limpeza: Diretório temporário removido: {temp_dir.name}")
                except Exception as e:
                    logger.error(f"Erro ao remover diretório temporário {temp_dir}: {str(e)}")
                    
        for zip_file in zips_to_cleanup:
            if zip_file.exists():
                try:
                    zip_file.unlink()
                    logger.info(f"Limpeza: Arquivo original descompactado removido: {zip_file.name}")
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo zip {zip_file}: {str(e)}")
                    
    # Relatório Final
    logger.info("=== Relatório de Organização ===")
    logger.info(f"Total de arquivos analisados: {stats['total']}")
    logger.info(f"Arquivos classificados e movidos com sucesso: {stats['classificados']}")
    logger.info(f"Arquivos enviados para a raiz (fallback/baixa confiança): {stats['fallback_raiz']}")
    logger.info(f"Falhas / Erros de processamento: {stats['erros']}")
    logger.info("=================================")

if __name__ == "__main__":
    main()
