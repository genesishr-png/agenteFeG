import os
import zipfile
from pathlib import Path
from pypdf import PdfReader
import docx2txt

class DocumentExtractor:
    @staticmethod
    def extract_zip(zip_path: Path, temp_dir_root: Path) -> list[Path]:
        """
        Descompacta o arquivo ZIP em uma pasta temporária e retorna a lista de caminhos dos arquivos internos válidos.
        """
        zip_path = Path(zip_path)
        temp_dir_root = Path(temp_dir_root)
        
        extracted_files = []
        if not zipfile.is_zipfile(zip_path):
            return extracted_files
            
        temp_dest = temp_dir_root / f".temp_extracted_{zip_path.stem}"
        temp_dest.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dest)
                
            ignored_extensions = {".ini", ".sys", ".tmp", ".log", ".env", ".gitignore"}
            
            for root, _, files in os.walk(temp_dest):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() not in ignored_extensions and not file.startswith("."):
                        extracted_files.append(file_path)
        except Exception as e:
            print(f"Erro ao descompactar ZIP '{zip_path.name}': {str(e)}")
            
        return extracted_files

    @staticmethod
    def extract_text(file_path: Path, max_pages: int = 3) -> dict:
        """
        Extrai o texto de um arquivo (PDF, DOCX ou TXT).
        Retorna um dicionário contendo:
        - "text": O texto extraído (str)
        - "is_scanned": Se o arquivo parece ser um escaneamento/imagem (bool)
        - "mime_type": Mime-type estimado do arquivo (str)
        - "error": Mensagem de erro se ocorrer (str ou None)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {"text": "", "is_scanned": False, "mime_type": "", "error": "Arquivo não encontrado."}

        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            return DocumentExtractor._extract_pdf(file_path, max_pages)
        elif suffix == ".docx":
            return DocumentExtractor._extract_docx(file_path)
        elif suffix in [".txt", ".log", ".csv"]:
            return DocumentExtractor._extract_txt(file_path)
        else:
            # Para outros formatos (ex: jpg, png), marcamos como scanned para tratar via multimodal
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg"
            }
            mime_type = mime_map.get(suffix, "application/octet-stream")
            return {
                "text": "", 
                "is_scanned": True, 
                "mime_type": mime_type, 
                "error": None
            }

    @staticmethod
    def _extract_pdf(file_path: Path, max_pages: int) -> dict:
        """Extrai texto de um PDF digital e detecta se é escaneado."""
        try:
            reader = PdfReader(file_path)
            num_pages = len(reader.pages)
            pages_to_read = min(num_pages, max_pages)
            
            text_parts = []
            for i in range(pages_to_read):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text_parts.append(page_text)
                    
            full_text = "\n".join(text_parts).strip()
            
            # Se tivermos menos de 100 caracteres em 3 páginas, é muito provável que seja um PDF escaneado (imagem)
            is_scanned = len(full_text) < 100
            
            return {
                "text": full_text,
                "is_scanned": is_scanned,
                "mime_type": "application/pdf",
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "is_scanned": True,  # Força tratamento via multimodal/API em caso de erro de leitura de texto
                "mime_type": "application/pdf",
                "error": f"Erro ao ler PDF: {str(e)}"
            }

    @staticmethod
    def _extract_docx(file_path: Path) -> dict:
        """Extrai texto de um arquivo Word DOCX."""
        try:
            text = docx2txt.process(str(file_path)).strip()
            return {
                "text": text,
                "is_scanned": False,
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "is_scanned": False,
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "error": f"Erro ao ler DOCX: {str(e)}"
            }

    @staticmethod
    def _extract_txt(file_path: Path) -> dict:
        """Extrai texto de um arquivo TXT de texto simples."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().strip()
            return {
                "text": text[:8000],  # Limita tamanho para classificação
                "is_scanned": False,
                "mime_type": "text/plain",
                "error": None
            }
        except Exception as e:
            return {
                "text": "",
                "is_scanned": False,
                "mime_type": "text/plain",
                "error": f"Erro ao ler TXT: {str(e)}"
            }

if __name__ == "__main__":
    # Teste rápido
    test_file = Path("test.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Teste de extração de conteúdo do agente RAG.")
    
    res = DocumentExtractor.extract_text(test_file)
    print("Resultado do Teste:", res)
    
    if test_file.exists():
        os.remove(test_file)
