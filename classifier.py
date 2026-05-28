import json
import logging
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
import google.generativeai as genai
from anthropic import Anthropic

import config

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Classifier")

class ClassificationResult(BaseModel):
    classificado: bool = Field(description="Se o arquivo foi classificado com sucesso para uma pasta de destino.")
    codigo_materia: Optional[str] = Field(description="Sigla/código de segundo nível da matéria processual (ex: IP, RT, SAUDE) ou null se for Relação Jurídica ou Financeiro.")
    caminho_pasta_destino: str = Field(description="O caminho relativo da pasta de destino (ex: 01_RELAÇÃO_JURÍDICA/01 PROPOSTA E CONTRATO ou 03_CASO/IP/01_Boletim_e_Portaria). Use barras normais /.")
    nome_arquivo_higienizado: str = Field(description="Nome limpo do arquivo com a extensão correta (ex: Peticao Inicial.pdf, Contrato de Honorarios.pdf, RG.pdf).")
    confianca_percentual: int = Field(description="Percentual de confiança da IA na classificação (0 a 100).")
    justificativa_semantica: str = Field(description="Breve explicação jurídica de porque o arquivo foi parar nessa pasta.")

class DocumentClassifier:
    def __init__(self):
        # Inicializa o Gemini
        if config.GEMINI_API_KEY and config.GEMINI_API_KEY != "sua_chave_do_gemini_aqui":
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
            logger.warning("Gemini API key não configurada. O classificador Gemini não estará disponível.")

        # Inicializa o Claude
        if config.ANTHROPIC_API_KEY and config.ANTHROPIC_API_KEY != "sua_chave_do_claude_aqui":
            self.claude_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        else:
            self.claude_client = None
            logger.warning("Claude API key não configurada. O fallback do Claude não estará disponível.")

    def _load_glossary(self) -> str:
        """Carrega o glossário de conhecimento RAG completo."""
        if not config.GLOSSARY_PATH.exists():
            raise FileNotFoundError(f"Base de conhecimento não encontrada em {config.GLOSSARY_PATH}")
        with open(config.GLOSSARY_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def classify_document(self, file_path: Path, extracted_text: str, is_scanned: bool, mime_type: str) -> ClassificationResult:
        """
        Classifica um documento com base em seu texto e metadados.
        Em caso de PDF escaneado (is_scanned=True), envia o arquivo binário diretamente para a API do Gemini.
        Se a confiança do Gemini for inferior a 75%, realiza o fallback para o Claude.
        """
        file_path = Path(file_path)
        glossary_content = self._load_glossary()
        
        # Prepara o prompt do sistema instruindo o modelo
        system_instruction = f"""
Você é um agente classificador de documentos jurídicos altamente preciso. Seu papel é analisar o conteúdo de um arquivo (seja via texto bruto ou leitura multimodal de imagem/PDF) e decidir em qual pasta ele deve ser roteado e qual deve ser o seu nome higienizado.

Para classificar, consulte a taxonomia de matérias, subpastas, finalidades, palavras-chave e regras de desambiguação contidas no seguinte Glossário de Organização:

---
{glossary_content}
---

Instruções Adicionais:
1. Retorne 'classificado' como True apenas se classificar em uma subpasta válida.
2. Certifique-se de aplicar a seção '12. Guia de Desambiguação de Documentos Homônimos' para evitar conflitos de nomes (como Contrato).
3. Renomeie o arquivo com a extensão correta (ex: se o original for '.pdf', a saída deve terminar com '.pdf').
4. Se o documento for ilegível, protegido por senha ou você não tiver certeza absoluta (confiança < 75%), marque 'classificado' como False, defina o 'caminho_pasta_destino' como 'raiz' e mantenha o nome original.
"""

        result = None
        
        # 1. Tentar classificação com Gemini Flash
        if self.gemini_model:
            try:
                logger.info(f"Classificando '{file_path.name}' via Gemini Flash...")
                result = self._classify_with_gemini(file_path, extracted_text, is_scanned, mime_type, system_instruction)
                
                # Se a confiança for alta, retorna o resultado
                if result and result.confianca_percentual >= config.CONFIDENCE_THRESHOLD:
                    logger.info(f"Classificação Gemini bem-sucedida! Confiança: {result.confianca_percentual}%")
                    return result
                elif result:
                    logger.warning(f"Confiança do Gemini Flash baixa ({result.confianca_percentual}%). Tentando fallback...")
            except Exception as e:
                logger.error(f"Erro no classificador Gemini Flash: {str(e)}")
        
        # 2. Fallback para Claude (ou se confiança do Gemini for baixa)
        if self.claude_client:
            try:
                logger.info(f"Classificando '{file_path.name}' via Claude 3.5 Sonnet (Fallback)...")
                # Se o Gemini obteve texto mas teve baixa confiança, usamos esse texto ou o texto extraído
                text_to_use = extracted_text
                if is_scanned and result and result.justificativa_semantica:
                    # Tenta aproveitar qualquer informação de texto que o Gemini possa ter fornecido ou extraído
                    text_to_use = f"[Documento Escaneado] O Gemini analisou e descreveu: {result.justificativa_semantica}\n" + extracted_text

                claude_result = self._classify_with_claude(file_path.name, text_to_use, system_instruction)
                if claude_result:
                    logger.info(f"Classificação Claude bem-sucedida! Confiança: {claude_result.confianca_percentual}%")
                    return claude_result
            except Exception as e:
                logger.error(f"Erro no fallback do Claude: {str(e)}")

        # 3. Fallback final de segurança se tudo falhar ou não houver APIs disponíveis
        logger.warning(f"Roteamento de fallback de segurança (raiz) aplicado para '{file_path.name}'.")
        return ClassificationResult(
            classificado=False,
            codigo_materia=None,
            caminho_pasta_destino="raiz",
            nome_arquivo_higienizado=file_path.name,
            confianca_percentual=0,
            justificativa_semantica="Não foi possível obter classificação confiável das APIs de IA."
        )

    def _classify_with_gemini(self, file_path: Path, extracted_text: str, is_scanned: bool, mime_type: str, system_instruction: str) -> ClassificationResult:
        """Chama a API do Gemini Flash com tratamento de Rate Limit (HTTP 429 / ResourceExhausted)."""
        import time
        from google.api_core.exceptions import ResourceExhausted, GoogleAPICallError
        
        contents = []
        
        if is_scanned:
            # Envia o arquivo como multimodal
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            contents.append({
                "mime_type": mime_type,
                "data": file_bytes
            })
            contents.append(f"Classifique este arquivo de imagem/digitalização com base nas regras do sistema.")
        else:
            # Envia apenas o texto extraído
            contents.append(f"Arquivo: {file_path.name}\n\nTexto Extraído:\n{extracted_text[:12000]}")

        # Configura o modelo para retornar JSON estruturado via Pydantic
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ClassificationResult
        )

        max_retries = 5
        backoff_factor = 3
        
        for attempt in range(max_retries):
            try:
                # Instancia o modelo com a instrução do sistema para compatibilidade com versões antigas do SDK do Gemini
                model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
                response = model.generate_content(
                    contents=contents,
                    generation_config=generation_config
                )
                # Converte a resposta JSON em objeto Pydantic
                data = json.loads(response.text)
                return ClassificationResult(**data)
            except (ResourceExhausted, GoogleAPICallError) as e:
                # Verifica se é rate limit e faz retry
                if attempt < max_retries - 1:
                    sleep_time = (attempt + 1) * backoff_factor + 2
                    logger.warning(f"Rate Limit do Gemini atingido para '{file_path.name}'. Tentativa {attempt + 1}/{max_retries}. Aguardando {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    raise e
            except Exception as e:
                raise e

    def _classify_with_claude(self, file_name: str, text_content: str, system_instruction: str) -> ClassificationResult:
        """Chama a API do Claude 3.5 Sonnet."""
        # Claude não tem structured output nativo via Pydantic como o Gemini no SDK padrão,
        # então instruímos o modelo a retornar JSON e fazemos o parse manual.
        prompt = f"""
Aqui está o arquivo a ser classificado:
Nome do arquivo: {file_name}
Conteúdo de texto:
{text_content[:15000]}

Retorne a resposta estritamente no seguinte formato JSON (não adicione nenhuma outra introdução ou conclusão):
{{
  "classificado": true,
  "codigo_materia": "CÓDIGO (ex: RT, IP, etc)",
  "caminho_pasta_destino": "caminho/relativo",
  "nome_arquivo_higienizado": "Nome Limpo.pdf",
  "confianca_percentual": 95,
  "justificativa_semantica": "Explicação..."
}}
"""

        message = self.claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=system_instruction,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Tenta extrair o JSON da resposta do Claude
        text_response = message.content[0].text.strip()
        # Caso a LLM coloque blocos de código ```json ... ```
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response:
            text_response = text_response.split("```")[1].strip()
            
        data = json.loads(text_response)
        return ClassificationResult(**data)

if __name__ == "__main__":
    # Teste rápido se instanciado diretamente
    classifier = DocumentClassifier()
    print("Classificador inicializado com sucesso.")
