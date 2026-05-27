import sys
import os
import logging
from pathlib import Path
import re
import shutil

# Adiciona o diretório atual ao path para importações
sys.path.append(str(Path(__file__).resolve().parent))

import config
from extractor import DocumentExtractor
from classifier import ClassificationResult
from router import FileRouter

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RecursiveTest")

class HeuristicMockClassifier:
    """Classificador simulado local robusto baseado na pasta de origem e nome do arquivo."""
    
    def classify_document(self, file_path: Path, extracted_text: str, is_scanned: bool, mime_type: str) -> ClassificationResult:
        file_name = file_path.name.lower()
        parent_name = file_path.parent.name
        
        # 1. Pastas originais da RELAÇÃO JURÍDICA (Devem usar os nomes originais estáticos exatos)
        if parent_name == "01 PROPOSTA E CONTRATO":
            if "contrato" in file_name:
                nome = "Contrato de Honorarios.pdf"
            else:
                nome = "Proposta de Servicos.pdf"
            return ClassificationResult(
                classificado=True,
                codigo_materia=None,
                caminho_pasta_destino="01_RELAÇÃO_JURÍDICA/01 PROPOSTA E CONTRATO",
                nome_arquivo_higienizado=nome,
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Contrato ou Proposta de Serviços."
            )
            
        elif parent_name == "02 PROCURAÇÃO E SUBSTABELECIMENTO":
            return ClassificationResult(
                classificado=True,
                codigo_materia=None,
                caminho_pasta_destino="01_RELAÇÃO_JURÍDICA/02 PROCURAÇÃO E SUBSTABELECIMENTO",
                nome_arquivo_higienizado="Procuracao.pdf",
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Procuração ou Substabelecimento."
            )
            
        elif parent_name == "03 DOCUMENTOS DE IDENTIFICAÇÃO":
            if "cnpj" in file_name:
                nome = "CNPJ.pdf"
            else:
                nome = "Contrato Social.pdf"
            return ClassificationResult(
                classificado=True,
                codigo_materia=None,
                caminho_pasta_destino="01_RELAÇÃO_JURÍDICA/03 DOCUMENTOS DE IDENTIFICAÇÃO",
                nome_arquivo_higienizado=nome,
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Documento de Identificação societária."
            )
            
        # 2. Pasta original do FINANCEIRO
        elif parent_name == "02_FINANCEIRO":
            return ClassificationResult(
                classificado=True,
                codigo_materia=None,
                caminho_pasta_destino="02_FINANCEIRO",
                nome_arquivo_higienizado="Comprovante de Pagamento.pdf",
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Comprovante de Pagamento."
            )
            
        # 3. Subpastas de 03_CASO
        elif parent_name == "01 Requerimento de Acesso":
            if "oab" in file_name:
                return ClassificationResult(
                    classificado=True,
                    codigo_materia=None,
                    caminho_pasta_destino="01_RELAÇÃO_JURÍDICA/03 DOCUMENTOS DE IDENTIFICAÇÃO",
                    nome_arquivo_higienizado="OAB.pdf",
                    confianca_percentual=100,
                    justificativa_semantica="Mapeamento Simulado: OAB do advogado."
                )
            elif "requerimento" in file_name:
                return ClassificationResult(
                    classificado=True,
                    codigo_materia="TCE",
                    caminho_pasta_destino="03_CASO/02_TCE/02_Defesa_e_Justificativas",
                    nome_arquivo_higienizado="Requerimento de Acesso.pdf",
                    confianca_percentual=100,
                    justificativa_semantica="Mapeamento Simulado: Requerimento de acesso aos autos."
                )
            elif "gmail" in file_name or "mail" in file_name:
                return ClassificationResult(
                    classificado=True,
                    codigo_materia="TCE",
                    caminho_pasta_destino="03_CASO/02_TCE/02_Defesa_e_Justificativas",
                    nome_arquivo_higienizado="Comprovante de Envio Requerimento.pdf",
                    confianca_percentual=100,
                    justificativa_semantica="Mapeamento Simulado: Comprovante de envio de requerimento."
                )
            elif "relato" in file_name:
                return ClassificationResult(
                    classificado=True,
                    codigo_materia="TCE",
                    caminho_pasta_destino="03_CASO/02_TCE/01_Notificacoes_e_Relatorios",
                    nome_arquivo_higienizado="Relatorio de Fiscalizacao.pdf",
                    confianca_percentual=100,
                    justificativa_semantica="Mapeamento Simulado: Relatório ou Histórico de Trâmites."
                )
                
        elif parent_name == "02 Notas Fiscais":
            # Extrai o número da NF se disponível no nome
            import re
            match = re.search(r"\d+", file_name)
            num = match.group() if match else "0000"
            return ClassificationResult(
                classificado=True,
                codigo_materia=None,
                caminho_pasta_destino="02_FINANCEIRO",
                nome_arquivo_higienizado=f"Nota Fiscal {num}.pdf",
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Nota Fiscal do caso."
            )
            
        elif parent_name == "03 Petição Administrativa":
            if "altera" in file_name:
                nome = "Contrato Social.pdf"
                dest = "01_RELAÇÃO_JURÍDICA/03 DOCUMENTOS DE IDENTIFICAÇÃO"
                cod = None
            elif "cnpj" in file_name:
                nome = "CNPJ.pdf"
                dest = "01_RELAÇÃO_JURÍDICA/03 DOCUMENTOS DE IDENTIFICAÇÃO"
                cod = None
            elif "procura" in file_name:
                nome = "Procuracao.pdf"
                dest = "01_RELAÇÃO_JURÍDICA/02 PROCURAÇÃO E SUBSTABELECIMENTO"
                cod = None
            else:
                nome = "Peticao Administrativa.pdf"
                dest = "03_CASO/02_TCE/02_Defesa_e_Justificativas"
                cod = "TCE"
            return ClassificationResult(
                classificado=True,
                codigo_materia=cod,
                caminho_pasta_destino=dest,
                nome_arquivo_higienizado=nome,
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Documento da Petição Administrativa."
            )
            
        elif parent_name == "04 Casos Paradigmaticos":
            return ClassificationResult(
                classificado=True,
                codigo_materia="TCE",
                caminho_pasta_destino="03_CASO/02_TCE/03_Julgamento_e_Acordaos",
                nome_arquivo_higienizado="Acordao Tribunal de Contas.pdf",
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Acórdão paradigma do TCE."
            )
            
        elif parent_name == "05 Documento disponibilizado_22.04.2026":
            return ClassificationResult(
                classificado=True,
                codigo_materia="LIC",
                caminho_pasta_destino="03_CASO/01_LIC/01_Edital_e_Anexos",
                nome_arquivo_higienizado="Despacho Cotacao Precos.pdf",
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Despacho do processo de cotação."
            )
            
        # 4. Arquivos soltos na raiz de 03_CASO
        elif parent_name == "03_CASO":
            if "confirmando" in file_name or "envio" in file_name:
                nome = "Comprovante de Envio Peticao.pdf"
                dest = "03_CASO/02_TCE/02_Defesa_e_Justificativas"
                cod = "TCE"
            elif "edital" in file_name or "prodnorte" in file_name:
                nome = "Edital de Licitacao.pdf"
                dest = "03_CASO/01_LIC/01_Edital_e_Anexos"
                cod = "LIC"
            elif "manifesta" in file_name:
                nome = "Razoes de Justificativa.pdf"
                dest = "03_CASO/02_TCE/02_Defesa_e_Justificativas"
                cod = "TCE"
            elif "notificac" in file_name:
                nome = "Notificacao Recomendatoria MPC.pdf"
                dest = "03_CASO/02_TCE/01_Notificacoes_e_Relatorios"
                cod = "TCE"
            elif "relato" in file_name:
                nome = "Relatorio de Fiscalizacao.pdf"
                dest = "03_CASO/02_TCE/01_Notificacoes_e_Relatorios"
                cod = "TCE"
            elif "integra" in file_name or "íntegra" in file_name:
                nome = "Processo Administrativo Integral.pdf"
                dest = "03_CASO/02_TCE/01_Notificacoes_e_Relatorios"
                cod = "TCE"
            else:
                nome = file_path.name
                dest = "raiz"
                cod = None
            return ClassificationResult(
                classificado=True if dest != "raiz" else False,
                codigo_materia=cod,
                caminho_pasta_destino=dest,
                nome_arquivo_higienizado=nome,
                confianca_percentual=100,
                justificativa_semantica="Mapeamento Simulado: Arquivo da raiz de 03_CASO."
            )
            
        # Fallback padrão
        return ClassificationResult(
            classificado=False,
            codigo_materia=None,
            caminho_pasta_destino="raiz",
            nome_arquivo_higienizado=file_path.name,
            confianca_percentual=60,
            justificativa_semantica="Mapeamento Simulado: Classificação padrão de fallback."
        )

def run_recursive_test(root_path: Path):
    root_path = Path(root_path)
    
    logger.info(f"=== INICIANDO ROTEAMENTO RECURSIVO REAL ===")
    logger.info(f"Pasta Raiz do Cliente: {root_path}")
    logger.info("===========================================")
    
    if not root_path.exists():
        logger.error(f"Erro: Pasta raiz não existe: {root_path}")
        return
        
    # 0. Pré-cria a estrutura completa de subpastas do CASO para garantir a ordem e numeração consecutiva
    lic_dirs = [
        "01_Edital_e_Anexos",
        "02_Habilitacao_e_Cadastro",
        "03_Propostas_e_Precos",
        "04_Recursos_e_Atas",
        "05_Homologacao_e_Contrato"
    ]
    tce_dirs = [
        "01_Notificacoes_e_Relatorios",
        "02_Defesa_e_Justificativas",
        "03_Julgamento_e_Acordaos",
        "04_Recursos_e_Pedidos"
    ]
    for d in lic_dirs:
        (root_path / "03_CASO" / "01_LIC" / d).mkdir(parents=True, exist_ok=True)
    for d in tce_dirs:
        (root_path / "03_CASO" / "02_TCE" / d).mkdir(parents=True, exist_ok=True)
        
    classifier = HeuristicMockClassifier()
    router = FileRouter()
    
    # 1. Varre recursivamente para encontrar todos os arquivos PDF
    pdf_files = []
    for r, d, fs in os.walk(root_path):
        # Ignora pastas que já são os novos destinos padronizados
        part_path = Path(r)
        if any(p in part_path.parts for p in ["01_LIC", "02_TCE"]):
            continue
            
        for f in fs:
            if f.lower().endswith(".pdf"):
                pdf_files.append(Path(r) / f)
                
    logger.info(f"Encontrados {len(pdf_files)} arquivos PDF aninhados para organizar.")
    
    # 2. Processa e move cada arquivo
    for i, file_path in enumerate(pdf_files, 1):
        logger.info(f"\n--- [{i}/{len(pdf_files)}] Processando: '{file_path.name}' ---")
        
        # Extrai texto rápido
        extraction = DocumentExtractor.extract_text(file_path, max_pages=3)
        
        # Classifica
        classification = classifier.classify_document(
            file_path=file_path,
            extracted_text=extraction["text"],
            is_scanned=extraction["is_scanned"],
            mime_type=extraction["mime_type"]
        )
        
        logger.info(f"Pasta Alvo: {classification.caminho_pasta_destino} | Nome Alvo: {classification.nome_arquivo_higienizado}")
        
        # Executa a movimentação física real (dry_run=False)
        router.route_file(
            source_path=file_path,
            destination_root=root_path,
            classification=classification,
            dry_run=False
        )
        
    # 3. Limpeza: remove as pastas antigas vazias (NUNCA remove as estáticas de Relação Jurídica)
    logger.info("\n=== INICIANDO LIMPEZA DE PASTAS VAZIAS ===")
    folders_to_check = [
        root_path / "03_CASO" / "01 Requerimento de Acesso",
        root_path / "03_CASO" / "02 Notas Fiscais",
        root_path / "03_CASO" / "03 Petição Administrativa",
        root_path / "03_CASO" / "04 Casos Paradigmaticos",
        root_path / "03_CASO" / "05 Documento disponibilizado_22.04.2026"
    ]
    
    for folder in folders_to_check:
        if folder.exists() and folder.is_dir():
            # Conta se há arquivos dentro
            items = os.listdir(folder)
            if not items:
                try:
                    folder.rmdir()
                    logger.info(f"Removida pasta vazia antiga: '{folder.name}'")
                except Exception as e:
                    logger.warning(f"Não pôde remover pasta '{folder.name}': {str(e)}")
            else:
                logger.info(f"Pasta '{folder.name}' ainda contém {len(items)} arquivos. Mantida.")

if __name__ == "__main__":
    client_root = Path(r"C:\Users\genes\OneDrive\Área de Trabalho\edson\OneDrive_2026-05-26\Onda Pro Importadora_9158\01_LLC_LARISSA_8532")
    run_recursive_test(client_root)
