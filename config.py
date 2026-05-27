import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Caminho Base do Projeto
BASE_DIR = Path(__file__).resolve().parent

# Chaves de API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Caminhos de Diretórios Padrão
DEFAULT_INPUT_DIR = BASE_DIR / "entrada"
DEFAULT_OUTPUT_DIR = BASE_DIR / "saida"

# Caminho da Base de Conhecimento RAG (Glossário)
GLOSSARY_PATH = Path(os.getenv(
    "GLOSSARY_PATH", 
    BASE_DIR / "glossario_organizacao_pastas.md"
))

# Configurações de Fallback e Limiares
CONFIDENCE_THRESHOLD = 75  # Porcentagem mínima de confiança para aceitar a classificação
MAX_PDF_PAGES_TO_EXTRACT = 3  # Quantidade de páginas do PDF analisadas para classificação (evita estourar tokens)

def validate_config():
    """Valida as configurações críticas do sistema."""
    warnings = []
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "sua_chave_do_gemini_aqui":
        warnings.append("Aviso: GEMINI_API_KEY não configurada ou com valor padrão no arquivo .env.")
        
    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "sua_chave_do_claude_aqui":
        warnings.append("Aviso: ANTHROPIC_API_KEY não configurada no arquivo .env. Fallback para Claude não funcionará.")
        
    if not GLOSSARY_PATH.exists():
        warnings.append(f"Aviso: Arquivo do Glossário RAG não encontrado em: {GLOSSARY_PATH}")
        
    return warnings

if __name__ == "__main__":
    print("Base Dir:", BASE_DIR)
    print("Glossary Path:", GLOSSARY_PATH)
    for warning in validate_config():
        print(warning)
