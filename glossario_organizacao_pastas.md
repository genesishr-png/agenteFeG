# Glossário: Agente de Organização e Renomeação de Pastas (RAG Database Edition)

Este glossário serve como base de conhecimento semântica oficial para o desenvolvimento de um agente inteligente especializado em renomeação, higienização e organização de diretórios e arquivos através de RAG (Retrieval-Augmented Generation).

> [!WARNING]
> **RESTRIÇÃO CRÍTICA DE SEGURANÇA**: O agente **NUNCA** deve alterar, renomear ou mover as pastas iniciais do cliente que contêm os números de registro administrativo (`AAAA-BB.CCCC`) e o nome do cliente. Essas pastas são estáticas (somente leitura) para o agente.

---

## 1. Conceitos Fundamentais de Organização

| Termo | Definição | Exemplo / Contexto |
| :--- | :--- | :--- |
| **Diretório Raiz (Root)** | A pasta principal que serve de ponto de partida para a organização. O agente operará a partir deste diretório. | `C:\Projetos\` ou `/Users/usuario/Documentos/` |
| **Hierarquia (Hierarchy)** | A estrutura em árvore que define a relação de subordinação entre pastas (pastas-pai e pastas-filho). | `Projetos (Pai) > 2026 (Filho) > Design (Neto)` |
| **Taxonomia (Taxonomy)** | O sistema de classificação usado para categorizar arquivos de forma lógica e consistente. | Classificar por `[Ano]/[Cliente]/[Tipo de Documento]` |
| **Caminho Absoluto (Absolute Path)** | O endereço completo de um arquivo ou pasta a partir do nível mais alto do sistema de arquivos. | `C:\Users\genes\Documentos\Financeiro\relatorio.pdf` |
| **Caminho Relativo (Relative Path)** | O endereço de um arquivo ou pasta em relação ao diretório de trabalho atual do agente. | `.\Financeiro\relatorio.pdf` |
| **Metadados (Metadata)** | Informações estruturadas que descrevem o arquivo, mas não fazem parte do seu conteúdo principal (ex: data de criação, tamanho). | A data de modificação ou tags inseridas nas propriedades do arquivo. |
| **Higienização de Caminho (Path Sanitization)** | Processo de ajustar nomes de pastas ou arquivos para que sejam válidos no sistema de arquivos, removendo caracteres proibidos (`?`, `*`, `:`, `|`). | Substituir caracteres inválidos por hifens ou espaços vazios. |

---

## 2. Convenções de Nomenclatura (Naming Conventions)

*   **snake_case**: Palavras em minúsculo separadas por sublinhado. Exemplo: `relatorio_financeiro_maio.pdf`.
*   **kebab-case**: Palavras em minúsculo separadas por hífen. Exemplo: `relatorio-financeiro-maio.pdf`.
*   **CamelCase**: Primeira letra minúscula, e as iniciais das palavras seguintes em maiúscula. Exemplo: `relatorioFinanceiroMaio.pdf`.
*   **PascalCase**: Todas as palavras iniciadas com maiúscula, sem espaços. Exemplo: `RelatorioFinanceiroMaio.pdf`.

---

## 3. Lógica de Organização e Regras do Agente

*   **Roteamento de Arquivos (File Routing / Sorting)**: Ação de mover um arquivo de uma pasta temporária para seu destino final com base em regras e RAG.
*   **Desduplicação (De-duplication)**: Processo de detectar arquivos idênticos por nome/tamanho ou através de *hashes* únicos (MD5, SHA-256) para evitar duplicidade de documentos na mesma pasta.
*   **Regras de Exclusão (Ignore/Exclude Rules)**: Arquivos e pastas que o agente nunca deve ler ou mover (ex: `.DS_Store`, `desktop.ini`, `.git`).
*   **Arquivamento (Archiving)**: Identificação de arquivos antigos para histórico (ex: `/Arquivo_Morto/2024/`).

---

## 4. Termos Técnicos do Agente Inteligente

*   **Execução Simulada (Dry Run)**: Simulação onde o agente exibe um relatório com todas as alterações previstas, sem realizá-las no disco.
*   **Processamento em Lote (Batch Processing)**: Execução massiva e automatizada de uma mesma regra em múltiplos arquivos.
*   **Expressões Regulares (Regex)**: Padrões de busca de texto para capturar e higienizar partes dos nomes (datas, CPF, etc.).
*   **Classificação Baseada em NLP**: Uso de Processamento de Linguagem Natural para classificar semanticamente o conteúdo textual extraído do arquivo.
*   **OCR (Reconhecimento Óptico de Caracteres)**: Leitura de imagens e PDFs escaneados para extrair o texto interno.
*   **Colisão de Nomes (Name Collision)**: Quando o agente tenta mover um arquivo para uma pasta onde já existe outro homônimo. Resolvido adicionando índice numérico: `documento(1).pdf`.
*   **Desfazer (Rollback)**: Capacidade de desfazer o último lote de alterações, restaurando o estado anterior do sistema de arquivos.

---

## 5. Regras de Negócio e Estrutura do Projeto (Definição de Fluxo)

*   **Identificador de Registro Administrativo (`AAAA-BB.CCCC`)**: Código único gerado pelo sistema legado. O agente **nunca** deve alterar pastas neste nível (ex: `001_CRIM_ADRIANO_6424`).
*   **Pastas Base Estáticas (Nível 1)**: Subpastas geradas de forma estática pelo legado dentro de cada pasta de cliente. O agente não pode alterá-las, apenas inserir arquivos nelas:
    *   `01_RELAÇÃO_JURÍDICA`
    *   `02_FINANCEIRO`
    *   `03_CASO`
*   **Escopo de Atuação (Ponto de Entrada)**: A pasta `03_CASO` é a zona dinâmica onde o agente cria a árvore de pastas específica baseada no **Subtipo Processual** (ex: `IP`, `RT`).

---

## 6. Arquitetura de Integração com RAG (Retrieval-Augmented Generation)

Este glossário atua como o **Banco de Dados de Conhecimento Semântico** do agente. O pipeline de classificação segue estas fases:

```
[Arquivo PDF/Word] ➔ [Extração de Texto/OCR] ➔ [LLM analisa Cabeçalho/Peça] ➔ [Consulta ao Glossário (RAG)] ➔ [Roteamento & Renomeação]
```

1.  **Ingestão e Extração de Texto**: O agente extrai o texto do arquivo (via Python libraries ou OCR se for imagem).
2.  **Segmentação Semântica (Chunking)**: O agente envia à LLM as primeiras páginas do documento (onde estão o cabeçalho judicial, qualificação de partes e pedidos).
3.  **Busca e Recuperação (RAG)**: O agente busca neste glossário a pasta destino que melhor combine com as **Palavras-chave**, **Finalidade** e **Padrão Semântico** da peça.
4.  **Ação de Destino**: O agente cria a subpasta correspondente dentro de `03_CASO` (se já não existir), renomeia o arquivo no padrão limpo e o move para o diretório final.

---

## 7. Proposta de Estrutura de Subpastas por Tipo de Processo (RAG Schema)
Abaixo está o mapeamento detalhado de todas as subpastas criadas dinamicamente dentro de `03_CASO` por tipo de processo, estruturado para consumo da LLM.

---
### A. Criminal (`CRIM`)

#### A.1. Criminal - Inquérito e Investigação (`IP`)
Estrutura para a fase pré-processual de apuração (códigos: IP, INV).
*   `01_Boletim_e_Portaria`
    *   *Finalidade*: Boletins de ocorrência, portarias e termos circunstanciados.
    *   *Palavras-chave*: "Boletim de Ocorrência", "B.O.", "Termo Circunstanciado", "Portaria de Instauração", "Delegacia de Polícia".
    *   *Padrão Semântico*: Capas de inquérito, cabeçalhos de delegacias civis ou federais, termos de abertura.
    *   *Exemplo de Renomeação*: Boletim de Ocorrencia.pdf, Portaria de Instauracao.pdf
*   `02_Depoimentos_e_Oitivas`
    *   *Finalidade*: Termos de depoimento de testemunhas, vítimas e investigado na delegacia.
    *   *Palavras-chave*: "Termo de Declarações", "Depoimento", "Oitiva", "Testemunha", "Declarativo", "Indiciado".
    *   *Padrão Semântico*: Transcrições de falas à autoridade policial na delegacia de acusados, vítimas ou terceiros.
    *   *Exemplo de Renomeação*: Termo de Declaracoes Testemunha.pdf
*   `03_Diligencias_e_Relatorios`
    *   *Finalidade*: Mandados de busca, relatórios parciais e relatórios finais da polícia.
    *   *Palavras-chave*: "Relatório de Investigação", "Mandado de Busca e Apreensão", "Auto de Exibição e Apreensão", "Relatório Parcial".
    *   *Padrão Semântico*: Descrição de diligências policiais executadas em campo, apreensões de materiais e relatórios assinados pelo escrivão/delegado.
    *   *Exemplo de Renomeação*: Mandado de Busca e Apreensao.pdf
*   `04_Laudos_e_Pericias`
    *   *Finalidade*: Perícias papiloscópicas, balísticas, laudos de corpo de delito, etc.
    *   *Palavras-chave*: "Laudo Pericial", "Corpo de Delito", "Perito Criminal", "Laudo de Constatação", "Necropsia", "Instituto Médico Legal".
    *   *Padrão Semântico*: Análise técnica laboratorial, exames físicos, perícia papiloscópica, informática ou necropsias.
    *   *Exemplo de Renomeação*: Laudo de Corpo de Delito.pdf, Laudo Pericial Balistica.pdf

#### A.2. Criminal - Ação Penal e Instrução (`AP`)
Estrutura para a fase judicial criminal comum (códigos: AP, INST).
*   `01_Denuncia_ou_Queixa`
    *   *Finalidade*: Denúncia do Ministério Público ou Queixa-Crime privada.
    *   *Palavras-chave*: "Denúncia", "Queixa-Crime", "Promotor de Justiça", "Querelante", "Querelado", "Ministério Público".
    *   *Padrão Semântico*: Petição do Ministério Público imputando fato criminoso ao réu ou queixa privada de crime de honra.
    *   *Exemplo de Renomeação*: Denuncia.pdf, Queixa Crime.pdf
*   `02_Resposta_Acusacao_e_Defesa`
    *   *Finalidade*: Respostas à acusação, defesas prévias e memoriais finais.
    *   *Palavras-chave*: "Resposta à Acusação", "Defesa Prévia", "Alegações Finais por Memoriais", "Absolvição Sumária".
    *   *Padrão Semântico*: Petições defensivas pedindo absolvição, nulidades processuais ou atenuação da pena.
    *   *Exemplo de Renomeação*: Resposta a Acusacao.pdf, Membro Defensivo Memoriais.pdf
*   `03_Atas_e_Midias_Audiencia`
    *   *Finalidade*: Atas de audiência e arquivos de áudio/vídeo dos depoimentos.
    *   *Palavras-chave*: "Ata de Audiência", "Termo de Audiência", "Gravação de Depoimento", "Mídia Audiovisual".
    *   *Padrão Semântico*: Resumo assinado pelo juiz do que ocorreu na audiência, links ou mídias integradas de gravação do Teams/Zoom.
    *   *Exemplo de Renomeação*: Ata de Audiencia.pdf, Termo de Audiencia.pdf
*   `04_Sentenca_e_Recursos`
    *   *Finalidade*: Sentença de mérito, apelações e recursos perante tribunais.
    *   *Palavras-chave*: "Sentença", "Apelação Criminal", "Recurso em Sentido Estrito", "Acórdão", "Pronúncia", "Impronúncia".
    *   *Padrão Semântico*: Decisão de mérito do juiz condenando ou absolvendo o réu, ou acórdãos de apelações colegiadas.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Acordao.pdf

#### A.3. Criminal - Execução Penal (`EP`)
Acompanhamento de cumprimento de penas (código: EP).
*   `01_Guia_de_Recolhimento_e_Pena`
    *   *Finalidade*: Guias de recolhimento, históricos de cálculo de pena e atestados de conduta.
    *   *Palavras-chave*: "Guia de Recolhimento", "Atestado de Pena a Cumprir", "Ficha Disciplinar", "Cálculo de Liquidação de Pena".
    *   *Padrão Semântico*: Histórico de punições e contagem de dias de pena emitido pela Vara de Execuções Penais.
    *   *Exemplo de Renomeação*: Guia de Recolhimento.pdf, Calculo de Pena.pdf
*   `02_Progressao_e_Beneficios`
    *   *Finalidade*: Pedidos de progressão de regime, saídas temporárias e livramento condicional.
    *   *Palavras-chave*: "Progressão de Regime", "Livramento Condicional", "Saída Temporária", "Indulto", "Comutação".
    *   *Padrão Semântico*: Manifestações ou decisões de concessão de regime semiaberto/aberto, saidinhas ou liberdade condicional.
    *   *Exemplo de Renomeação*: Pedido de Progressao de Regime.pdf
*   `03_Remissao_e_Trabalho`
    *   *Finalidade*: Atestados de trabalho e estudo para remissão e laudos criminológicos.
    *   *Palavras-chave*: "Remissão de Pena", "Atestado de Trabalho", "Atestado de Estudo", "Laudo Criminológico".
    *   *Padrão Semântico*: Comprovantes de atividade laboral e educacional dentro da unidade prisional.
    *   *Exemplo de Renomeação*: Remissao de Pena Trabalho.pdf

---
### B. Cível (`CIVIL`)

#### B.1. Cível - Conhecimento (`CON`)
Ações cíveis comuns como cobranças, indenizações e possessórias (código: CON).
*   `01_Peticao_Inicial_e_Documentos`
    *   *Finalidade*: Petição inicial, guias de custas e documentos probatórios do autor.
    *   *Palavras-chave*: "Petição Inicial", "Guia de Custas Judiciais", "Comprovante de Distribuição", "Valor da Causa".
    *   *Padrão Semântico*: Petição do autor expondo os fatos e o direito, acompanhada das guias de recolhimento de taxas estaduais.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Comprovante de Distribuicao.pdf
*   `02_Defesa_e_Contestacao`
    *   *Finalidade*: Contestação do réu, reconvenções, réplicas e impugnações.
    *   *Palavras-chave*: "Contestação", "Réplica", "Reconvenção", "Impugnação à Contestação".
    *   *Padrão Semântico*: Peças de bloqueio da defesa e a respectiva resposta do autor (réplica).
    *   *Exemplo de Renomeação*: Contestacao.pdf, Replica.pdf
*   `03_Instrucao_e_Laudos`
    *   *Finalidade*: Saneamento do processo, laudos periciais cíveis e técnicos.
    *   *Palavras-chave*: "Decisão Saneadora", "Laudo de Avaliação", "Laudo Pericial Cível", "Quesitos do Perito".
    *   *Padrão Semântico*: Provas técnicas periciais solicitadas pelo juízo (perícia grafotécnica, contábil ou de engenharia).
    *   *Exemplo de Renomeação*: Laudo Pericial Grafotecnico.pdf
*   `04_Sentenca_e_Acordao`
    *   *Finalidade*: Sentenças de primeiro grau, apelações, agravos de instrumento e acórdãos.
    *   *Palavras-chave*: "Sentença", "Recurso de Apelação", "Agravo de Instrumento", "Recurso Especial", "Acórdão".
    *   *Padrão Semântico*: Decisão do juízo de primeiro grau ou acórdão de tribunais (TJ/TRF) resolvendo o litígio.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Apelacao Civel.pdf

#### B.2. Cível - Execução e Cumprimento (`EXEC`)
Cobranças e expropriações judiciais de valores (códigos: EXEC, CUMP).
*   `01_Titulo_e_Demonstrativo_Debito`
    *   *Finalidade*: Títulos executivos judiciais/extrajudiciais e planilhas de cálculos.
    *   *Palavras-chave*: "Título Executivo Extrajudicial", "Cumprimento de Sentença", "Planilha de Débito", "Demonstrativo de Cálculo", "Nota Promissória", "Cheque".
    *   *Padrão Semântico*: Contratos assinados por testemunhas, cheques protestados ou memória discriminada do valor devido atualizado.
    *   *Exemplo de Renomeação*: Titulo Executivo.pdf, Planilha de Debito.pdf
*   `02_Penhoras_e_Bloqueios`
    *   *Finalidade*: Bloqueios SISBAJUD, buscas de bens (Renajud/Infojud) e laudos de avaliação.
    *   *Palavras-chave*: "Auto de Penhora", "SISBAJUD", "RENAJUD", "INFOJUD", "Certidão de Penhora".
    *   *Padrão Semântico*: Ordens e comprovantes de constrição judicial de contas bancárias, imóveis ou veículos.
    *   *Exemplo de Renomeação*: Bloqueio Sisbajud.pdf, Auto de Penhora.pdf
*   `03_Embargos_e_Impugnacoes`
    *   *Finalidade*: Embargos à execução, impugnações e exceções de pré-executividade.
    *   *Palavras-chave*: "Embargos à Execução", "Impugnação ao Cumprimento de Sentença", "Exceção de Pré-Executividade".
    *   *Padrão Semântico*: Peças de defesa do executado contra a cobrança, alegando excesso de execução ou impenhorabilidade.
    *   *Exemplo de Renomeação*: Embargos a Execucao.pdf, Excecao de Pre Executividade.pdf
*   `04_Leiloes_e_Adjudicacao`
    *   *Finalidade*: Editais de leilão público, autos de arrematação e termos de adjudicação.
    *   *Palavras-chave*: "Edital de Leilão", "Auto de Arrematação", "Termo de Adjudicação", "Carta de Arrematação".
    *   *Padrão Semântico*: Editais, lances aceitos e termos de transferência de propriedade forçada.
    *   *Exemplo de Renomeação*: Auto de Arrematação.pdf

#### B.3. Cível - Direito Médico e Saúde (`SAUDE`)
Disputas de cobertura de planos de saúde, erro médico e fornecimento de remédios (código: SAUDE).
*   `01_Inicial_e_Negativa_Plano`
    *   *Finalidade*: Petição inicial de obrigação de fazer, contratos do plano e carta de recusa do convênio.
    *   *Palavras-chave*: "Ação de Obrigação de Fazer", "Plano de Saúde", "Negativa de Cobertura", "ANS", "Carta de Negativa", "Recusa".
    *   *Padrão Semântico*: Comunicação formal do plano de saúde indeferindo cirurgia ou exame, contratos do convênio e carteirinha de associado.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Negativa do Plano.pdf
*   `02_Laudos_e_Relatorios_Medicos`
    *   *Finalidade*: Atestados médicos de urgência indicando a necessidade clínica do tratamento.
    *   *Palavras-chave*: "Laudo Médico de Urgência", "Relatório Médico", "CID", "Tratamento Cirúrgico", "Indicação Clínica".
    *   *Padrão Semântico*: Relatórios assinados por médicos especialistas descrevendo a urgência do caso e indicando cirurgia ou medicamento específico com o código CID.
    *   *Exemplo de Renomeação*: Relatorio Medico de Urgencia.pdf
*   `03_Orcamentos_e_Custos`
    *   *Finalidade*: Cotações de tratamentos, medicamentos especiais ou procedimentos hospitalares.
    *   *Palavras-chave*: "Orçamento de Tratamento", "Cotação de Medicamento", "Nota de Custo", "Tratamento de Saúde".
    *   *Padrão Semântico*: Cotações comerciais de hospitais, clínicas ou importadoras de medicamentos não disponíveis no SUS.
    *   *Exemplo de Renomeação*: Orcamento Hospitalar.pdf
*   `04_Liminar_e_Sentenca`
    *   *Finalidade*: Tutelas de urgência deferidas, sentenças e acórdãos colegiados.
    *   *Palavras-chave*: "Antecipação de Tutela", "Liminar Concedida", "Tutela de Urgência", "Sentença", "Apelação".
    *   *Padrão Semântico*: Decisão do juiz deferindo o início imediato de cirurgia ou tratamento, sob pena de multa diária.
    *   *Exemplo de Renomeação*: Decisao Liminar.pdf, Sentenca.pdf

#### B.4. Cível - Direito Bancário (`BANCO`)
Ações revisionais de taxas de juros, busca e apreensão de veículos e empréstimos (código: BANCO).
*   `01_Contrato_e_Planilha_Revisional`
    *   *Finalidade*: Contrato de financiamento assinado e cálculo pericial contábil de juros abusivos.
    *   *Palavras-chave*: "Cédula de Crédito Bancário", "Contrato de Financiamento", "Ação Revisional de Contrato", "Juros Abusivos", "Planilha Revisional", "Laudo Contábil".
    *   *Padrão Semântico*: Contratos de financiamento de veículos ou empréstimo consignado assinados com o banco, juntamente com o laudo pericial contábil da taxa de juros.
    *   *Exemplo de Renomeação*: Contrato de Financiamento.pdf, Planilha Revisional.pdf
*   `02_Inicial_e_Notificacoes`
    *   *Finalidade*: Petição inicial, mandados de busca e apreensão e notificações de cartórios.
    *   *Palavras-chave*: "Petição Inicial Revisional", "Busca e Apreensão", "Notificação de Débito", "Mora Constitucional", "Notificação Extrajudicial".
    *   *Padrão Semântico*: Petição inicial contestando taxas contratuais ou mandados de busca e apreensão de veículos e comprovantes de notificações recebidas de cartórios.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Notificacao Extrajudicial.pdf
*   `03_Sentenca_e_Acordos`
    *   *Finalidade*: Sentença revisional homologatória e termos de acordos de quitação com o banco.
    *   *Palavras-chave*: "Termo de Acordo de Quitação", "Sentença Revisional", "Depósito Judicial de Parcelas", "Quitação".
    *   *Padrão Semântico*: Sentença reconhecendo abuso de juros ou minuta de acordo de conciliação assinado com a instituição bancária.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Acordo de Quitacao.pdf

---
### C. Previdenciário (`PREV`)

#### C.1. Previdenciário - Aposentadorias (`APOS`)
Concessão e revisão de aposentadorias e pensões (códigos: APOS, PENS).
*   `01_CNIS_e_Carteiras_CTPS`
    *   *Finalidade*: Extratos CNIS completos, carteiras de trabalho e guias de recolhimento.
    *   *Palavras-chave*: "CNIS", "Cadastro Nacional de Informações Sociais", "Carteira de Trabalho", "CTPS", "Guia da Previdência Social".
    *   *Padrão Semântico*: Tabelas de salários de contribuição com colunas 'Competência', 'Recolhimento' e códigos como 'NIT', 'PIS', 'PASEP', ou digitalizações de páginas da CTPS com dados do empregador.
    *   *Exemplo de Renomeação*: Extrato CNIS.pdf, Carteira de Trabalho.pdf
*   `02_Processo_Administrativo_INSS`
    *   *Finalidade*: Cópia integral do processo administrativo de requerimento do INSS.
    *   *Palavras-chave*: "Processo Administrativo", "Requerimento de Benefício", "Cópia de Processo INSS", "Carta de Concessão", "Meu INSS".
    *   *Padrão Semântico*: Documentos oficiais com cabeçalho do 'Ministério da Previdência Social' ou 'Instituto Nacional do Seguro Social', histórico de requerimentos e cartas de deferimento/indeferimento.
    *   *Exemplo de Renomeação*: Processo Administrativo INSS.pdf
*   `03_Peticao_Inicial_prev`
    *   *Finalidade*: Petição inicial judicial previdenciária e comprovantes pessoais.
    *   *Palavras-chave*: "Petição Inicial Previdenciária", "Indeferimento do INSS", "Comprovante de Endereço", "Justiça Gratuita".
    *   *Padrão Semântico*: Petições destinadas a Varas Federais ou Juizados Federais (JEF), qualificando o autor e o INSS, com pedidos de concessão/revisão e jurisprudência previdenciária.
    *   *Exemplo de Renomeação*: Peticao Inicial Judicial.pdf
*   `04_Sentenca_e_Recursos`
    *   *Finalidade*: Sentenças, recursos, cálculos de parcelas atrasadas e RPVs.
    *   *Palavras-chave*: "Sentença Previdenciária", "Recurso Inominado", "RPV", "Precatório", "Cálculo de Atrasados".
    *   *Padrão Semântico*: Dispositivo de sentença reconhecendo o direito, acórdãos de Turmas Recursais/TRF, planilhas de cálculos de atrasados e guias RPV ou Precatórios.
    *   *Exemplo de Renomeação*: Sentenca Condenatoria.pdf, Requisitorio RPV.pdf

#### C.2. Previdenciário - Incapacidade (`INCAP`)
Auxílio-doença, invalidez e benefícios assistenciais (códigos: INCAP, LOAS).
*   `01_Atestados_e_Exames_Medicos`
    *   *Finalidade*: Atestados médicos, relatórios clínicos, receitas e prontuários médicos.
    *   *Palavras-chave*: "Atestado Médico", "Laudo Clínico", "Exame de Imagem", "Prontuário Médico", "Receituário".
    *   *Padrão Semântico*: Declarações assinadas por médicos com indicação de CID (Classificação Internacional de Doenças), receitas de medicamentos, exames de imagem e prontuários.
    *   *Exemplo de Renomeação*: Atestado Medico.pdf, Prontuario Clinico.pdf
*   `02_Laudo_Pericial_Judicial`
    *   *Finalidade*: Laudo conclusivo elaborado pelo perito nomeado pelo juiz.
    *   *Palavras-chave*: "Laudo Pericial Médico", "Perito do Juízo", "Incapacidade Laborativa", "CID", "Doença Ocupacional".
    *   *Padrão Semântico*: Relatório pericial assinado por perito médico oficial da Justiça Federal, respondendo a quesitos judiciais e concluindo pela incapacidade temporária ou permanente.
    *   *Exemplo de Renomeação*: Laudo Pericial Judicial.pdf
*   `03_Quesitos_e_Manifestacoes`
    *   *Finalidade*: Quesitos apresentados e manifestações técnicas sobre o laudo pericial.
    *   *Palavras-chave*: "Quesitos da Defesa", "Quesitos do Autor", "Manifestação sobre Laudo Pericial", "Impugnação ao Laudo".
    *   *Padrão Semântico*: Petição contendo perguntas (quesitos) a serem respondidas pelo perito ou manifestações técnicas sobre o laudo médico, contestando ou apoiando as conclusões.
    *   *Exemplo de Renomeação*: Quesitos da Parte Autora.pdf
*   `04_Sentenca_e_Implantacao`
    *   *Finalidade*: Sentença condenatória, ofício de implantação de benefício e RPV/Precatórios.
    *   *Palavras-chave*: "Sentença", "Implantação de Benefício", "Ofício de Concessão", "RPV", "Precatório".
    *   *Padrão Semântico*: Decisão judicial determinando a implantação imediata do benefício e ofício do juízo comunicando a APS para cumprimento da ordem.
    *   *Exemplo de Renomeação*: Sentenca Concessiva.pdf, Oficio de Implantacao.pdf

---
### D. Tributário (`TRIB`)

#### D.1. Tributário - Execução Fiscal (`EXEC`)
Defesa contra execuções fiscais da Fazenda Pública (código: EXEC).
*   `01_CDA_e_Peticao_Inicial`
    *   *Finalidade*: Certidão de Dívida Ativa e petição de execução fiscal inicial.
    *   *Palavras-chave*: "CDA", "Certidão de Dívida Ativa", "Execução Fiscal", "Petição Inicial da Fazenda", "Fazenda Nacional".
    *   *Padrão Semântico*: Certidão de Dívida Ativa com discriminação do débito tributário, número de inscrição, leis violadas e petição inicial do Fisco para cobrança judicial.
    *   *Exemplo de Renomeação*: Certidao de Divida Ativa.pdf, Peticao Inicial Execucao Fiscal.pdf
*   `02_Garantias_e_Bens_Penhorados`
    *   *Finalidade*: Cartas de fiança, seguros-garantia ou indicação de bens à penhora.
    *   *Palavras-chave*: "Apólice de Seguro Garantia", "Carta de Fiança Bancária", "Nomeação de Bens à Penhora", "Termo de Garantia".
    *   *Padrão Semântico*: Apólices de seguro-garantia, cartas de fiança bancária e petições de nomeação de bens à penhora com descrição detalhada dos bens oferecidos.
    *   *Exemplo de Renomeação*: Apolice Seguro Garantia.pdf
*   `03_Embargos_ou_Excecao_Pre_Executividade`
    *   *Finalidade*: Embargos à execução fiscal ou exceções de pré-executividade protocoladas.
    *   *Palavras-chave*: "Embargos à Execução Fiscal", "Exceção de Pré-Executividade", "Suspensão de Exigibilidade".
    *   *Padrão Semântico*: Petições incidentais de embargos contendo defesas materiais ou petição simples de exceção de pré-executividade baseada em matérias de ordem pública.
    *   *Exemplo de Renomeação*: Embargos a Execucao Fiscal.pdf
*   `04_Decisoes_e_Recursos`
    *   *Finalidade*: Sentenças dos embargos, apelações fiscais e recursos aos tribunais.
    *   *Palavras-chave*: "Sentença nos Embargos", "Apelação Tributária", "Agravo de Instrumento", "Acórdão Tributário".
    *   *Padrão Semântico*: Sentenças julgando procedentes ou improcedentes os embargos fiscais, recursos de apelação tributária, agravos de instrumento sobre penhoras e acórdãos do TJ, TRF ou STJ.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Recurso de Apelacao.pdf

#### D.2. Tributário - Declaratórias e Anulatórias (`DECL`)
Ações ordinárias para anular débitos ou repetir indébitos tributários (códigos: DECL, ANUL).
*   `01_Lancamento_Tributario_ou_Auto`
    *   *Finalidade*: Autos de infração fiscal e notificações administrativas de lançamento.
    *   *Palavras-chave*: "Auto de Infração", "Notificação de Lançamento", "Processo Administrativo Fiscal", "PAF".
    *   *Padrão Semântico*: Auto de infração lavrado por auditor fiscal, notificações de lançamento de débitos, multas tributárias e relatórios de fiscalização contábil.
    *   *Exemplo de Renomeação*: Auto de Infracao Fiscal.pdf
*   `02_Peticao_Inicial_e_Guias`
    *   *Finalidade*: Petições iniciais tributárias e comprovantes de depósito judicial.
    *   *Palavras-chave*: "Petição Inicial Anulatória", "Guia de Depósito Judicial", "Ação Declaratória Tributária", "Suspensão de Exigibilidade".
    *   *Padrão Semântico*: Petição de ação ordinária contra a Fazenda Pública, pedidos de tutela provisória para suspensão de exigibilidade do tributo e guias de depósitos judiciais integrais.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Guia de Deposito Judicial.pdf
*   `03_Provas_e_Laudos_Contabeis`
    *   *Finalidade*: Auditorias contábeis, memórias de cálculo de créditos e notas fiscais.
    *   *Palavras-chave*: "Laudo Pericial Contábil", "Planilha de Compensação", "Auditoria Fiscal", "Notas Fiscais".
    *   *Padrão Semântico*: Perícias técnicas contábeis, planilhas de compensação de tributos pagos indevidamente, auditorias de crédito fiscal e cópias de notas fiscais de entrada e saída.
    *   *Exemplo de Renomeação*: Laudo Pericial Contabil.pdf
*   `04_Sentenca_e_Recursos`
    *   *Finalidade*: Sentenças, recursos perante o tribunal, agravos e recursos STJ/STF.
    *   *Palavras-chave*: "Sentença Declaratória", "Apelação", "Recurso Especial", "Acórdão".
    *   *Padrão Semântico*: Decisões judiciais de primeiro grau reconhecendo a inexistência de relação jurídico-tributária ou homologando a repetição do indébito, recursos de apelação e acórdãos fiscais.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Acordao.pdf

---
### E. Administrativo (`ADM`)

#### E.1. Administrativo - Licitações (`LIC`)
Certames licitatórios públicos para contratação de bens e serviços (códigos: lic, Preg).
*   `01_Edital_e_Anexos`
    *   *Finalidade*: Edital de licitação, anexos, termo de referência, esclarecimentos e impugnações do edital.
    *   *Palavras-chave*: "Edital de Licitação", "Termo de Referência", "Esclarecimentos", "Impugnação ao Edital", "Pregão Eletrônico".
    *   *Padrão Semântico*: Edital original e anexos do certame público, com regras de habilitação e especificações técnicas de compras públicas.
    *   *Exemplo de Renomeação*: Edital de Licitacao.pdf, Termo de Referencia.pdf
*   `02_Habilitacao_e_Cadastro`
    *   *Finalidade*: Documentos de habilitação (jurídica, fiscal, trabalhista e técnica).
    *   *Palavras-chave*: "Documentos de Habilitação", "Certidão Negativa de Débitos", "CND", "Regularidade Fiscal", "Qualificação Técnica".
    *   *Padrão Semântico*: Certidões de regularidade perante o FGTS, Receita Federal, certidões negativas de falências, contratos sociais e atestados de capacidade técnica.
    *   *Exemplo de Renomeação*: Certidao Negativa de Debitos.pdf
*   `03_Propostas_e_Precos`
    *   *Finalidade*: Proposta de preços comercial, planilhas de custos detalhadas e propostas de concorrentes.
    *   *Palavras-chave*: "Proposta Comercial", "Planilha de Custos", "Quadro de Lances", "Proposta Ajustada".
    *   *Padrão Semântico*: Planilhas orçamentárias detalhando custos e formação de preços, propostas técnicas comerciais assinadas pelo representante legal.
    *   *Exemplo de Renomeação*: Proposta Comercial de Precos.pdf
*   `04_Recursos_e_Atas`
    *   *Finalidade*: Recursos contra habilitação/desclassificação, contrarrazões e atas de sessões.
    *   *Palavras-chave*: "Recurso Administrativo", "Contrarrazões", "Ata da Sessão Pública", "Julgamento da Habilitação".
    *   *Padrão Semântico*: Peça recursal contra decisão da comissão de licitação contestando a habilitação de terceiros, e atas das sessões públicas com lances.
    *   *Exemplo de Renomeação*: Ata da Sessao Publica.pdf, Recurso Administrativo Licitacao.pdf
*   `05_Homologacao_e_Contrato`
    *   *Finalidade*: Termo de homologação/adjudicação e contrato administrativo assinado.
    *   *Palavras-chave*: "Termo de Homologação", "Termo de Adjudicação", "Contrato Administrativo", "Ordem de Serviço", "Ata de Registro de Preços".
    *   *Padrão Semântico*: Termos assinados pelo gestor homologando o vencedor, contratos assinados com a administração pública e ordens de início de serviços.
    *   *Exemplo de Renomeação*: Contrato Administrativo.pdf, Termo de Homologacao.pdf

#### E.2. Administrativo - Disciplinar (`PAD`)
Apuração de infrações funcionais e desvios de servidores ou empregados (códigos: PAD, sindi).
*   `01_Instauracao_e_Portaria`
    *   *Finalidade*: Portaria de instauração do PAD/Sindicância, denúncia inicial e portarias de comissão.
    *   *Palavras-chave*: "Portaria de Instauração", "Instauração de PAD", "Termo de Indiciamento", "Sindicância Administrativa".
    *   *Padrão Semântico*: Portaria publicada no Diário Oficial assinada pelo órgão público instaurando a comissão e descrevendo os fatos investigados contra o servidor.
    *   *Exemplo de Renomeação*: Portaria de Instauracao PAD.pdf
*   `02_Defesa_Previa`
    *   *Finalidade*: Defesa prévia apresentada pelo acusado e rol de testemunhas.
    *   *Palavras-chave*: "Defesa Prévia", "Defesa Escrita", "Rol de Testemunhas", "Defesa Preliminar".
    *   *Padrão Semântico*: Petição do advogado de defesa refutando as acusações preliminares constantes no termo de indiciamento e arrolando testemunhas.
    *   *Exemplo de Renomeação*: Defesa Previa.pdf
*   `03_Oitivas_e_Depoimentos`
    *   *Finalidade*: Atas de depoimentos de testemunhas, termos de oitiva do indiciado e acareações.
    *   *Palavras-chave*: "Termo de Depoimento", "Oitiva de Testemunha", "Interrogatório", "Acareação".
    *   *Padrão Semântico*: Transcrições oficiais das declarações prestadas por testemunhas e indiciado perante a comissão processante do PAD.
    *   *Exemplo de Renomeação*: Termo de Depoimento Testemunha.pdf
*   `04_Relatorio_da_Comissao`
    *   *Finalidade*: Relatório final conclusivo da Comissão Processante.
    *   *Palavras-chave*: "Relatório Final da Comissão", "Parecer Técnico", "Relatório de Sindicância".
    *   *Padrão Semântico*: Peça técnica conclusiva assinada pelos membros da comissão avaliando as provas e sugerindo a punição (demissão, suspensão) ou absolvição do servidor.
    *   *Exemplo de Renomeação*: Relatorio Final da Comissão.pdf
*   `05_Julgamento_e_Recursos`
    *   *Finalidade*: Decisão final da autoridade julgadora, aplicação de sanções e recursos hierárquicos.
    *   *Palavras-chave*: "Decisão da Autoridade Julgadora", "Termo de Julgamento", "Recurso Hierárquico", "Pedido de Reconsideração".
    *   *Padrão Semântico*: Decreto ou decisão formal da autoridade máxima do órgão aplicando a punição ou arquivando o feito, e recursos hierárquicos interpostos pelo réu.
    *   *Exemplo de Renomeação*: Decisao Julgadora.pdf, Recurso Hierarquico.pdf

#### E.3. Administrativo - Controle Externo (`TCE`)
Tomadas de contas especiais, auditorias e fiscalizações orçamentárias (códigos: TCE, TCER, TCU).
*   `01_Notificacoes_e_Relatorios`
    *   *Finalidade*: Ofícios de citação, relatórios preliminares/definitivos da fiscalização técnica.
    *   *Palavras-chave*: "Ofício de Citação", "Relatório de Fiscalização", "Instrução Técnica", "Rejeição de Contas".
    *   *Padrão Semântico*: Relatório técnico de auditoria emitido pelos analistas do tribunal de contas apontando irregularidades na aplicação de recursos ou gestão orçamentária.
    *   *Exemplo de Renomeação*: Oficio de Citação TCU.pdf, Relatorio de Fiscalizacao.pdf
*   `02_Defesa_e_Justificativas`
    *   *Finalidade*: Razões de justificativa apresentadas pelo gestor e documentação probatória.
    *   *Palavras-chave*: "Razões de Justificativa", "Defesa Prévia Tribunal de Contas", "Prestação de Contas Anual", "Documentos Justificativos".
    *   *Padrão Semântico*: Manifestações escritas de defesa do gestor municipal, federal ou estadual perante o tribunal de contas prestando contas ou justificando glosas.
    *   *Exemplo de Renomeação*: Razoes de Justificativa.pdf
*   `03_Julgamento_e_Acordaos`
    *   *Finalidade*: Parecer do MPC (Ministério Público de Contas), acórdãos e resoluções dos conselheiros.
    *   *Palavras-chave*: "Acórdão do TCU", "Acórdão do TCE", "Parecer Prévio", "Julgamento de Contas", "Irregularidade de Contas".
    *   *Padrão Semântico*: Acórdão proferido pelo tribunal colegiado de contas julgando as contas como regulares, regulares com ressalvas ou irregulares.
    *   *Exemplo de Renomeação*: Acordao Tribunal de Contas.pdf
*   `04_Recursos_e_Pedidos`
    *   *Finalidade*: Pedidos de reconsideração, recursos de revisão, agravos e embargos no Tribunal.
    *   *Palavras-chave*: "Pedido de Reconsideração", "Recurso de Revisão", "Recurso de Reconsideração", "Embargos de Declaração".
    *   *Padrão Semântico*: Recursos interpostos contra as multas e sanções pecuniárias aplicadas pelo Tribunal de Contas, como recursos de reconsideração e revisão.
    *   *Exemplo de Renomeação*: Recurso de Reconsideracao.pdf

#### E.4. Administrativo - Sancionadores e Gerais (`SANC`)
Processos de responsabilização de empresas, éticos e apurações (PADM, PAS, PAR, PREL, PEP, PAP).
*   `01_Auto_de_Infracao_ou_Notificacao`
    *   *Finalidade*: Auto de infração, termos de acusação, notificação de abertura do processo.
    *   *Palavras-chave*: "Auto de Infração", "Notificação de Instauração", "Termo de Acusação Fiscal", "Termo de Intimação".
    *   *Padrão Semântico*: Auto de infração lavrado por agências reguladoras (ANATEL, ANVISA) ou vigilância sanitária e notificações de instauração de procedimentos punitivos.
    *   *Exemplo de Renomeação*: Auto de Infracao.pdf
*   `02_Defesa_Administrativa`
    *   *Finalidade*: Defesas administrativas, impugnações, manifestações escritas iniciais.
    *   *Palavras-chave*: "Defesa Administrativa", "Impugnação de Auto de Infração", "Manifestação de Defesa".
    *   *Padrão Semântico*: Defesas administrativas iniciais protocoladas pelas empresas contra a acusação fiscal ou regulatória.
    *   *Exemplo de Renomeação*: Defesa Administrativa.pdf
*   `03_Instrucao_e_Provas`
    *   *Finalidade*: Laudos técnicos, perícias, manifestações de fiscais e relatórios de vistoria.
    *   *Palavras-chave*: "Relatório de Fiscalização", "Laudo Técnico de Vistoria", "Termo de Diligência", "Parecer".
    *   *Padrão Semântico*: Relatórios de vistorias técnicas, manifestações instrutórias dos fiscais públicos e laudos técnicos anexos ao processo regulatório.
    *   *Exemplo de Renomeação*: Laudo Tecnico de Vistoria.pdf
*   `04_Decisao_e_Recursos`
    *   *Finalidade*: Decisão sancionadora, termos de aplicação de multa e recursos às instâncias colegiadas.
    *   *Palavras-chave*: "Decisão Sancionadora", "Recurso Administrativo", "Termo de Aparelho de Multa", "Advertência".
    *   *Padrão Semântico*: Decisões colegiadas ou de diretoria de órgãos reguladores mantendo a autuação, e recursos hierárquicos interpostos.
    *   *Exemplo de Renomeação*: Decisao Administrativa.pdf, Recurso Administrativo.pdf

---
### F. Trabalhista (`TRAB`)

#### F.1. Trabalhista - Reclamação Trabalhista (`RT`)
Ações ordinárias ou sumaríssimas laborais perante a JT (códigos: RT, SUM).
*   `01_Inicial_e_Documentos_Trabalhador`
    *   *Finalidade*: Petições iniciais, cálculos liquidados, carteira de trabalho, TRCT e holerites.
    *   *Palavras-chave*: "Petição Inicial Trabalhista", "TRCT", "Termo de Rescisão", "Extrato do FGTS", "Holerite", "Recibo de Salário", "Convenção Coletiva", "CCT".
    *   *Padrão Semântico*: Petição inicial qualificando empregado e empregador, com pedidos fundamentados em verbas rescisórias, horas extras ou assédio, acompanhada de TRCT e holerites.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Termo de Rescisao TRCT.pdf
*   `02_Defesa_e_Cartoes_Ponto`
    *   *Finalidade*: Contestação da reclamada, cartões de ponto, relatórios de horas e defesas.
    *   *Palavras-chave*: "Contestação Trabalhista", "Cartão de Ponto", "Espelho de Ponto", "Recibo de Entrega de EPI", "Acordo de Compensação de Horas".
    *   *Padrão Semântico*: Contestação patronal rebatendo pedidos do trabalhador, cartões de ponto diários e recibos de EPI.
    *   *Exemplo de Renomeação*: Contestacao.pdf, Cartoes de Ponto.pdf
*   `03_Audiencias_e_Termos_Depoimento`
    *   *Finalidade*: Atas de audiências, acordos protocolados e depoimentos em áudio/vídeo.
    *   *Palavras-chave*: "Ata de Audiência", "Termo de Conciliação", "Ata de Instrução", "Termo de Acordo Trabalhista".
    *   *Padrão Semântico*: Atas de audiências na Justiça do Trabalho e termos de conciliação homologados.
    *   *Exemplo de Renomeação*: Ata de Audiencia.pdf, Termo de Conciliacao.pdf
*   `04_Laudos_Insalubridade_Periciais`
    *   *Finalidade*: Perícias de insalubridade, periculosidade e acidentárias com quesitos.
    *   *Palavras-chave*: "Laudo Pericial de Insalubridade", "Laudo de Periculosidade", "Laudo de Acidente de Trabalho", "Laudo Ergonômico", "Quesitos".
    *   *Padrão Semântico*: Relatórios periciais ambientais ou médicos elaborados por peritos judiciais avaliando condições insalubres ou acidentes de trabalho.
    *   *Exemplo de Renomeação*: Laudo Pericial Insalubridade.pdf
*   `05_Sentenca_e_Recursos`
    *   *Finalidade*: Sentenças trabalhistas, recursos ordinários, agravos de petição e contrarrazões.
    *   *Palavras-chave*: "Sentença Trabalhista", "Recurso Ordinário", "Contrarrazões", "Recurso de Revista", "Agravo de Instrumento".
    *   *Padrão Semântico*: Sentenças trabalhistas de procedência, recursos ordinários (RO) ou recursos de revista (RR), e acórdãos do TRT ou TST.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Recurso Ordinario.pdf
*   `06_Execucao_e_Calculos_Liquidação`
    *   *Finalidade*: Cálculos homologados, acordos judiciais da fase de execução e alvarás.
    *   *Palavras-chave*: "Cálculos de Liquidação Trabalhista", "Laudo Pericial Contábil-Trabalhista", "Homologação de Cálculos", "Alvará Judicial", "Agravo de Petição".
    *   *Padrão Semântico*: Planilhas de liquidação de sentença trabalhista, decisões homologatórias de cálculos, guias de depósito e alvarás judiciais de liberação de valores.
    *   *Exemplo de Renomeação*: Calculos de Liquidacao Homologados.pdf, Alvara Judicial.pdf

---
### G. Família e Sucessões (`FAM`)

#### G.1. Família - Divórcio e Guarda (`DIV`)
Ações litigiosas ou consensuais de família e alimentos (códigos: DIV, ALIM).
*   `01_Inicial_e_Documentos_Pessoais`
    *   *Finalidade*: Certidões pessoais (casamento/nascimento dos filhos), comprovantes de renda.
    *   *Palavras-chave*: "Certidão de Casamento", "Certidão de Nascimento", "Ação de Divórcio", "Petição Inicial de Alimentos", "Comprovante de Renda".
    *   *Padrão Semântico*: Certidões de casamento/nascimento dos filhos, petição de divórcio consensual ou litigioso, ações de alimentos ou guarda com comprovantes de renda.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Certidao de Casamento.pdf
*   `02_Acordos_e_Audiencias_Mediacao`
    *   *Finalidade*: Minutas de acordos, termos de guarda e atas de conciliação do CEJUSC.
    *   *Palavras-chave*: "Minuta de Acordo de Guarda", "Termo de Acordo de Divórcio", "Ata de Mediação do CEJUSC", "Termo de Guarda Provisória".
    *   *Padrão Semântico*: Minutas de acordos de guarda compartilhada, direito de visitas, alimentos e atas de mediação de Centros de Solução de Conflitos (CEJUSC).
    *   *Exemplo de Renomeação*: Minuta de Acordo de Guarda e Alimentos.pdf
*   `03_Estudos_Sociais_e_Laudos_Psicologicos`
    *   *Finalidade*: Laudos do setor psicossocial e pareceres de assistentes sociais do juízo.
    *   *Palavras-chave*: "Estudo Social Judicial", "Relatório Psicológico", "Parecer de Assistente Social", "Avaliação Psicológica".
    *   *Padrão Semântico*: Parecer e relatórios psicossociais elaborados por assistentes sociais e psicólogos forenses credenciados.
    *   *Exemplo de Renomeação*: Laudo do Setor Psicossocial.pdf
*   `04_Sentenca_e_Mandados_Averbacao`
    *   *Finalidade*: Sentença homologatória, mandado de averbação de divórcio e ofício de pensão.
    *   *Palavras-chave*: "Sentença Homologatória", "Mandado de Averbação", "Ofício para Desconto", "Averbador".
    *   *Padrão Semântico*: Sentenças homologatórias de divórcio, mandados direcionados ao Registro Civil para averbação do divórcio e ofícios para desconto de pensão.
    *   *Exemplo de Renomeação*: Sentenca Homologatoria.pdf, Mandado de Averbacao de Divorcio.pdf

#### G.2. Família - Inventário e Partilha (`INV`)
Processos de partilha de herança por inventário judicial ou extrajudicial (código: INV).
*   `01_Obito_e_Certidoes_Herdeiros`
    *   *Finalidade*: Certidão de óbito do autor da herança e documentos pessoais de todos os herdeiros.
    *   *Palavras-chave*: "Certidão de Óbito", "Petição de Abertura de Inventário", "Procuração de Herdeiros", "Nomeação de Inventariante".
    *   *Padrão Semântico*: Certidão de óbito do falecido, petições de abertura de inventário judicial, certidões de herdeiros e termos de nomeação de inventariante.
    *   *Exemplo de Renomeação*: Certidao de Obito.pdf, Termo de Nomeação de Inventariante.pdf
*   `02_Relacao_Bens_e_Impostos_ITCMD`
    *   *Finalidade*: Certidões de matrícula de imóveis, extratos bancários e guias pagas do ITCMD.
    *   *Palavras-chave*: "ITCMD", "Declaração de ITCMD", "Certidão de Matrícula", "Extrato Bancário", "Certidão Negativa".
    *   *Padrão Semântico*: Declarações e guias pagas do imposto de transmissão causa mortis (ITCMD), certidões de matrículas e extratos de contas do falecido.
    *   *Exemplo de Renomeação*: Declaracao de ITCMD.pdf, Extrato Bancario.pdf
*   `03_Esboco_de_Partilha_e_Acordos`
    *   *Finalidade*: Primeiras declarações, partilha amigável proposta e partilha homologada.
    *   *Palavras-chave*: "Primeiras Declarações", "Plano de Partilha", "Esboço de Partilha", "Últimas Declarações".
    *   *Padrão Semântico*: Petições contendo as primeiras declarações, plano ou esboço detalhado de partilha de bens entre os herdeiros.
    *   *Exemplo de Renomeação*: Esboco de Partilha de Bens.pdf
*   `04_Sentenca_e_Formal_Partilha`
    *   *Finalidade*: Sentença do inventário e formal de partilha para registro em cartório.
    *   *Palavras-chave*: "Sentença Homologatória", "Formal de Partilha", "Escritura Pública", "Carta de Adjudicação".
    *   *Padrão Semântico*: Sentença judicial homologando a partilha de bens, formal de partilha expedido pelo juízo ou escritura pública de inventário extrajudicial.
    *   *Exemplo de Renomeação*: Sentenca de Partilha.pdf, Formal de Partilha.pdf

---
### H. Contratos e Societário (`CORP` / `CONT`)

#### H.1. Societário - Atos Corporativos (`SOC`)
Constituição, alteração e deliberação empresarial (código: SOC).
*   `01_Atos_Constitutivos`
    *   *Finalidade*: Contrato social de fundação, estatuto social de S/As e cartão CNPJ.
    *   *Palavras-chave*: "Contrato Social Consolidador", "Estatuto Social", "Ata de Eleição da Diretoria", "Cartão CNPJ", "Requerimento de Empresário".
    *   *Padrão Semântico*: Contratos sociais de fundação, estatutos de sociedades anônimas, cartões de CNPJ e requerimentos de empresário individual.
    *   *Exemplo de Renomeação*: Contrato Social.pdf, Cartao CNPJ.pdf
*   `02_Atas_e_Assembleias`
    *   *Finalidade*: Atas de reuniões de diretoria, atas de assembleias gerais ordinárias/extraordinárias.
    *   *Palavras-chave*: "Ata de Assembleia Geral", "AGO", "AGE", "Ata de Reunião do Conselho", "Edital de Convocação".
    *   *Padrão Semântico*: Atas de assembleias gerais ordinárias ou extraordinárias (AGO/AGE), atas de reuniões do conselho de administração ou editais de convocação.
    *   *Exemplo de Renomeação*: Ata de Assembleia Geral Ordinaria.pdf
*   `03_Acordos_de_Acionistas`
    *   *Finalidade*: Acordo de sócios, acordo de acionistas e regimentos internos.
    *   *Palavras-chave*: "Acordo de Sócios", "Acordo de Quotistas", "Acordo de Acionistas", "Protocolo de Intenções".
    *   *Padrão Semântico*: Instrumentos particulares de acordos de acionistas, quotistas ou sócios, regulamentando o direito de voto e governança.
    *   *Exemplo de Renomeação*: Acordo de Socios.pdf
*   `04_Alteracoes_e_Registros`
    *   *Finalidade*: Alterações contratuais e registros efetuados nas juntas comerciais.
    *   *Palavras-chave*: "Alteração Contratual Registrada", "Distrato Social", "Ficha Cadastral", "NIRE".
    *   *Padrão Semântico*: Alterações de contratos sociais registradas na Junta Comercial correspondente, distratos sociais e fichas cadastrais simplificadas.
    *   *Exemplo de Renomeação*: Alteracao Contratual.pdf

#### H.2. Societário - Contratos Comerciais (`CONT`)
Gestão, elaboração e revisão de contratos mercantis e civis (código: CONT).
*   `01_Minutas_e_Negociacoes`
    *   *Finalidade*: Minutas em execução, revisões com marcas e e-mails de negociação.
    *   *Palavras-chave*: "Minuta de Contrato", "Draft de Contrato", "Versão com Marcas", "Proposta de Cláusula".
    *   *Padrão Semântico*: Rascunhos de minutas contratuais com marcações de alteração e termos de confidencialidade (NDA) preliminares.
    *   *Exemplo de Renomeação*: Minuta de Contrato.pdf
*   `02_Contratos_Assinados`
    *   *Finalidade*: Contratos comerciais definitivos assinados física ou digitalmente.
    *   *Palavras-chave*: "Instrumento Particular de Prestação", "Contrato de Locação Comercial", "Contrato de Parceria", "Assinatura Digital".
    *   *Padrão Semântico*: Contratos comerciais definitivos assinados pelas partes e testemunhas, com assinaturas físicas ou digitais.
    *   *Exemplo de Renomeação*: Contrato de Prestacao de Servicos.pdf
*   `03_Aditivos_e_Termos_Rescisao`
    *   *Finalidade*: Termos aditivos contratuais, termos de rescisão e distratos.
    *   *Palavras-chave*: "Termo Aditivo ao Contrato", "Primeiro Aditivo", "Distrato de Contrato", "Notificação de Rescisão", "Termo de Quitação".
    *   *Padrão Semântico*: Termos aditivos alterando prazos ou valores de contratos existentes, notificações de rescisão contratual e termos de quitação recíproca (distrato).
    *   *Exemplo de Renomeação*: Termo Aditivo.pdf, Distrato Contratual.pdf

---
### I. Imobiliário (`IMOB`)

#### I.1. Imobiliário - Transações e Regularização (`REG`)
Regularização fundiária, escrituras e transações imobiliárias (código: REG).
*   `01_Matriculas_e_Escrituras`
    *   *Finalidade*: Matrículas atualizadas dos imóveis, escrituras públicas e certidões de ônus.
    *   *Palavras-chave*: "Matrícula de Imóvel", "Certidão de Ônus Reais", "Escritura Pública", "Escritura de Doação".
    *   *Padrão Semântico*: Certidões de inteiro teor de matrícula de imóveis com registros e averbações, certidão de ônus reais e escrituras de compra, venda ou doação.
    *   *Exemplo de Renomeação*: Matricula de Imovel.pdf, Escritura Publica.pdf
*   `02_Promessas_Compra_Venda`
    *   *Finalidade*: Contratos de promessas de compra e venda e contratos de cessão de direitos.
    *   *Palavras-chave*: "Contrato de Gaveta", "Promessa de Compra e Venda", "Cessão de Direitos Aquisitivos".
    *   *Padrão Semântico*: Instrumentos particulares de promessa de compra e venda de imóvel, contratos de cessão de direitos aquisitivos e recibos de sinal.
    *   *Exemplo de Renomeação*: Promessa de Compra e Venda.pdf
*   `03_Certidoes_e_Impostos`
    *   *Finalidade*: Carnês de IPTU, certidões negativas de tributos municipais do imóvel.
    *   *Palavras-chave*: "Certidão de Débitos Municipais", "Carnê de IPTU", "Guia de ITBI", "Declaração de IPTU".
    *   *Padrão Semântico*: Guias de pagamento de ITBI, carnês de IPTU, certidões negativas de débitos tributários municipais incidentes sobre o imóvel.
    *   *Exemplo de Renomeação*: Certidao Negativa de IPTU.pdf
*   `04_Projetos_Alvaras_Habitese`
    *   *Finalidade*: Projetos de construção aprovados, alvarás e habite-se concedidos.
    *   *Palavras-chave*: "Alvará de Construção", "Projeto Arquitetônico Aprovado", "Certidão de Habite-se", "Habite-se", "Laudo de Vistoria".
    *   *Padrão Semântico*: Alvarás de construção civil emitidos por prefeituras, projetos arquitetônicos aprovados, certidões de Habite-se concedidas e laudos de vistoria.
    *   *Exemplo de Renomeação*: Certidao de Habite-se.pdf, Alvara de Construcao.pdf

#### I.2. Imobiliário - Contencioso (`LIT`)
Ações judiciais possessórias, despejos e usucapião (código: LIT).
*   `01_Inicial_Despejo_Usucapiao_Possessoria`
    *   *Finalidade*: Petições iniciais de ações imobiliárias e documentos da lide.
    *   *Palavras-chave*: "Petição Inicial de Despejo", "Ação de Usucapião", "Reintegração de Posse", "Petição Inicial Imobiliária", "Ação Demarcatória".
    *   *Padrão Semântico*: Petição inicial de ações possessórias, usucapião ordinário ou extrajudicial, despejo por falta de pagamento com qualificações das partes.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf
*   `02_Contratos_Locacao_e_Notificacoes`
    *   *Finalidade*: Contratos de locação, notificações de despejo extrajudiciais.
    *   *Palavras-chave*: "Contrato de Locação de Imóvel", "Notificação Extrajudicial de Despejo", "Notificação de Quitação", "Recibo de Chaves".
    *   *Padrão Semântico*: Contratos de locação residencial ou comercial e notificações extrajudiciais para desocupação voluntária de imóvel.
    *   *Exemplo de Renomeação*: Contrato de Locacao.pdf, Notificacao Extrajudicial.pdf
*   `03_Sentenca_e_Mandados_Reintegracao`
    *   *Finalidade*: Sentenças imobiliárias e mandados expedidos (despejo/reintegração).
    *   *Palavras-chave*: "Sentença de Despejo", "Mandado de Reintegração", "Sentença de Usucapião", "Mandado de Imissão".
    *   *Padrão Semântico*: Sentenças judiciais de mérito determinando o despejo ou a usucapião, mandados de reintegração de posse ou despejo coercitivo.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Mandado de Reintegracao.pdf

---
### J. Direito do Consumidor (`CONS`)

#### J.1. Consumidor - Juizado Especial (`JEC`)
Ações de consumo no rito especial dos juizados (código: JEC).
*   `01_Inicial_e_Provas_Consumo`
    *   *Finalidade*: Petições iniciais, notas fiscais de compra, prints de chats e faturas.
    *   *Palavras-chave*: "Danos Morais", "Petição Inicial JEC", "Nota Fiscal de Compra", "Protocolo de Atendimento", "WhatsApp".
    *   *Padrão Semântico*: Petição inicial simplificada do JEC detalhando falha na prestação do serviço ou produto, notas fiscais, faturas de cobrança e números de protocolos do SAC.
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Nota Fiscal de Compra.pdf
*   `02_Defesa_e_Contestacao`
    *   *Finalidade*: Contestações de empresas fornecedoras e manifestações do autor.
    *   *Palavras-chave*: "Contestação JEC", "Defesa da Requerida", "Réplica do Requerente", "Manifestação à Contestação".
    *   *Padrão Semântico*: Contestas da ré ou prestadora, réplicas do consumidor contendo contestações às preliminares de defesa e documentos anexos do réu.
    *   *Exemplo de Renomeação*: Contestacao.pdf
*   `03_Atas_Conciliacao_Audiencias`
    *   *Finalidade*: Atas de audiências conciliatórias e termos de instrução.
    *   *Palavras-chave*: "Ata de Audiência de Conciliação", "Ata de Instrução", "Termo de Homologação de Acordo".
    *   *Padrão Semântico*: Atas de audiências de conciliação ou instrução do JEC, termos de acordo assinados perante o conciliador e decisões de homologação.
    *   *Exemplo de Renomeação*: Ata de Audiencia Conciliacao.pdf
*   `04_Sentenca_e_Recursos`
    *   *Finalidade*: Sentenças cíveis dos JECs, recursos inominados e acórdãos.
    *   *Palavras-chave*: "Sentença JEC", "Recurso Inominado", "Contrarrazões ao Recurso Inominado", "Acórdão da Turma Recursal".
    *   *Padrão Semântico*: Sentenças proferidas por juízes leigos ou togados do JEC, recursos inominados apresentados às Turmas Recursais e acórdãos.
    *   *Exemplo de Renomeação*: Sentenca.pdf, Recurso Inominado.pdf

#### J.2. Consumidor - PROCON (`ADM`)
Reclamações e defesas administrativas de consumo (código: ADM).
*   `01_Reclamacao_e_Notificacao`
    *   *Finalidade*: Notificações do PROCON e reclamação cadastrada pelo consumidor.
    *   *Palavras-chave*: "Abertura de Reclamação PROCON", "Notificação Administrativa PROCON", "Auto de Notificação", "F.A.T.".
    *   *Padrão Semântico*: Fichas de atendimento inicial do PROCON (F.A.T.), notificações administrativas direcionadas às empresas reclamadas e prints de portais como Consumidor.gov.
    *   *Exemplo de Renomeação*: Ficha de Reclamacao PROCON.pdf
*   `02_Defesa_da_Empresa_Fornecedora`
    *   *Finalidade*: Defesa e manifestação administrativa protocolada pela empresa.
    *   *Palavras-chave*: "Defesa Administrativa PROCON", "Resposta à Reclamação", "Manifestação da Empresa".
    *   *Padrão Semântico*: Manifestações formais e defesas administrativas protocoladas por empresas de telefonia, bancos ou comércio perante o PROCON.
    *   *Exemplo de Renomeação*: Defesa Administrativa Empresa.pdf
*   `03_Decisao_Procon_e_Termo_Acordo`
    *   *Finalidade*: Ata de audiência administrativa no PROCON e decisões de multas.
    *   *Palavras-chave*: "Ata de Audiência Administrativa", "Termo de Acordo PROCON", "Decisão Administrativa de Multa".
    *   *Padrão Semântico*: Atas de audiências de conciliação administrativa do PROCON, decisões sancionadoras aplicando multas administrativas e termos de acordo firmados.
    *   *Exemplo de Renomeação*: Termo de Acordo PROCON.pdf

---
### K. Propriedade Intelectual e Marcas (`MARCA`)

#### K.1. Marcas e Patentes - Registro (`REG`)
Acompanhamento administrativo de registro no INPI (código: REG).
*   `01_Pesquisas_Viabilidade_Marcas`
    *   *Finalidade*: Relatórios de buscas e pesquisas prévias de viabilidade de marca.
    *   *Palavras-chave*: "Pesquisa de Anterioridade de Marca", "Relatório de Viabilidade", "Pesquisa no Banco do INPI".
    *   *Padrão Semântico*: Relatórios de buscas e pesquisas prévias de anterioridade efetuadas no banco de dados do INPI.
    *   *Exemplo de Renomeação*: Relatorio de Viabilidade de Marca.pdf
*   `02_Pedidos_Deposito_e_Guias`
    *   *Finalidade*: Formulários de depósito de marcas/patentes e recolhimento de GRUs.
    *   *Palavras-chave*: "Pedido de Registro de Marca", "Formulário de Depósito", "Guia de Recolhimento da União", "GRU do INPI".
    *   *Padrão Semântico*: Formulários de depósitos de pedidos de registro de marcas, patentes ou desenhos industriais no INPI e guias GRU pagas.
    *   *Exemplo de Renomeação*: Formulario de Deposito de Marca.pdf
*   `03_Oposicoes_Defesas_Recursos_INPI`
    *   *Finalidade*: Oposições de terceiros e defesas e recursos administrativos no INPI.
    *   *Palavras-chave*: "Oposição ao Registro de Marca", "Manifestação à Oposição", "Recurso Contra Indeferimento", "Réplica do INPI".
    *   *Padrão Semântico*: Petições administrativas de oposição de terceiros, manifestações a oposições, recursos contra indeferimentos de marcas e contrarrazões.
    *   *Exemplo de Renomeação*: Oposicao de Terceiro.pdf
*   `04_Certificados_Registro_INPI`
    *   *Finalidade*: Certificados definitivos de registro de marca e cartas-patentes concedidas.
    *   *Palavras-chave*: "Certificado de Registro", "Carta Patente", "Concessão do Registro".
    *   *Padrão Semântico*: Certificados definitivos de concessão de registros de marcas, patentes industriais emitidos pelo INPI com prazo de vigência.
    *   *Exemplo de Renomeação*: Certificado de Registro de Marca.pdf

#### K.2. Marcas e Patentes - Contencioso (`LIT`)
Litígios judiciais de infrações de marcas e patentes (código: LIT).
*   `01_Notificacoes_Abstencao_Uso_Marca`
    *   *Finalidade*: Notificações de uso indevido e contranotificações trocadas pelas partes.
    *   *Palavras-chave*: "Notificação de Infração de Marca", "Notificação de Abstenção de Uso", "Contra-Notificação".
    *   *Padrão Semântico*: Notificações extrajudiciais exigindo a abstenção imediata de uso de marca ou trade dress semelhante, e contra-notificações enviadas.
    *   *Exemplo de Renomeação*: Notificacao de Abstencao de Uso de Marca.pdf
*   `02_Inicial_e_Provas_Contrafação`
    *   *Finalidade*: Petições iniciais, amostras de produtos contrafeitos e perícias de marca.
    *   *Palavras-chave*: "Ação Inibitória de Uso", "Petição Inicial", "Laudo Pericial de Contrafação", "Auto de Constatação de Pirataria".
    *   *Padrão Semântico*: Petição inicial de ação inibitória e indenizatória por uso indevido de marca, laudos periciais criminais ou cíveis atestando falsificação (contrafação).
    *   *Exemplo de Renomeação*: Peticao Inicial.pdf, Laudo Pericial de Contrafacao.pdf
*   `03_Sentenca_e_Recursos`
    *   *Finalidade*: Sentença de abstenção de uso e condenação a perdas/danos e recursos cíveis.
    *   *Palavras-chave*: "Sentença Inibitória", "Condenação por Perdas e Danos", "Apelação".
    *   *Padrão Semântico*: Sentenças determinando a busca e apreensão de produtos piratas e proibindo o uso da marca sob pena de multa, e recursos de apelação.
    *   *Exemplo de Renomeação*: Sentenca.pdf

---
### L. Direito Ambiental (`AMB`)

#### L.1. Ambiental - Licenciamento (`LIC`)
Licenciamentos e relatórios ambientais industriais (código: LIC).
*   `01_Estudos_Ambientais_EIA_RIMA`
    *   *Finalidade*: Estudos de impacto ambiental (EIA), relatórios de impacto (RIMA) e plantas.
    *   *Palavras-chave*: "Estudo de Impacto Ambiental", "EIA/RIMA", "Relatório de Impacto Ambiental", "Mapa Temático", "Poligonal".
    *   *Padrão Semântico*: Relatórios técnicos de Estudo de Impacto Ambiental e Relatório de Impacto Ambiental (EIA/RIMA), mapas topográficos e relatórios ecológicos de fauna e flora.
    *   *Exemplo de Renomeação*: Relatorio de Impacto Ambiental EIA RIMA.pdf
*   `02_Outorgas_e_Licencas`
    *   *Finalidade*: Licenças de operação/instalação emitidas e outorgas de recursos hídricos.
    *   *Palavras-chave*: "Licença Prévia", "LP", "Licença de Instalação", "LI", "Licença de Operação", "LO", "Outorga".
    *   *Padrão Semântico*: Portarias de licenças prévias (LP), licenças de instalação (LI), licenças de operação (LO) e portarias de outorga de uso de recursos hídricos.
    *   *Exemplo de Renomeação*: Licenca de Operacao LO.pdf
*   `03_Auditorias_e_Certificados`
    *   *Finalidade*: Relatórios de auditoria ambiental e certificados de conformidade ecológica.
    *   *Palavras-chave*: "Relatório de Auditoria Ambiental", "Certificado de Regularidade", "Reserva Legal".
    *   *Padrão Semântico*: Relatórios de auditorias ecológicas independentes, certificados de regularidade ambiental e termos de averbação de reserva legal florestal.
    *   *Exemplo de Renomeação*: Relatorio de Auditoria Ambiental.pdf

#### L.2. Ambiental - Defesa de Multas (`DEF`)
Processos contra autos de infrações e multas ecológicas (código: DEF).
*   `01_Autos_Infracao_Ambiental`
    *   *Finalidade*: Autos de infração expedidos por órgãos ambientais (IBAMA, etc.) e relatórios fiscais.
    *   *Palavras-chave*: "Auto de Infração Ambiental", "Relatório de Fiscalização", "Notificação de Embargo".
    *   *Padrão Semântico*: Autos de infração ambiental lavrados por fiscais do IBAMA, ICMBio ou secretarias estaduais e municipais, com detalhamento das multas e embargos de área.
    *   *Exemplo de Renomeação*: Auto de Infracao Ambiental.pdf
*   `02_Defesas_Administrativas_Multas`
    *   *Finalidade*: Defesas administrativas e recursos protocolados em instâncias ambientais.
    *   *Palavras-chave*: "Defesa Administrativa de Auto", "Recurso Administrativo Ambiental", "Impugnação de Multa".
    *   *Padrão Semântico*: Defesas e impugnações administrativas contra multas e sanções ambientais e recursos direcionados a conselhos ecológicos (CONAMA, etc.).
    *   *Exemplo de Renomeação*: Defesa Administrativa de Multa.pdf
*   `03_Termos_Compromisso_TAC`
    *   *Finalidade*: Termos de Ajustamento de Conduta (TAC) e planos de recuperação de área (PRADA).
    *   *Palavras-chave*: "Termo de Ajustamento de Conduta", "TAC", "Projeto de Recuperação de Área Degradada", "PRADA".
    *   *Padrão Semântico*: Termos de Ajustamento de Conduta (TAC) assinados com o Ministério Público, projetos de recuperação de áreas degradadas (PRADA) e cronogramas de reflorestamento.
    *   *Exemplo de Renomeação*: Termo de Ajustamento de Conduta TAC.pdf

---
### M. Direito Eleitoral (`ELEI`)

#### M.1. Eleitoral - Campanhas (`CAMP`)
Acompanhamento de candidaturas e prestação de contas (código: CAMP).
*   `01_Candidaturas_e_Certidoes`
    *   *Finalidade*: Certidões de candidatos, registros de candidaturas e certidão de quitação.
    *   *Palavras-chave*: "Registro de Candidatura", "RRC", "Certidão de Quitação Eleitoral", "Certidão Criminal".
    *   *Padrão Semântico*: Formulários de requerimento de registro de candidatura (RRC), certidões criminais eleitorais negativas do candidato e declarações de bens patrimoniais.
    *   *Exemplo de Renomeação*: Registro de Candidatura RRC.pdf
*   `02_Prestacoes_Contas_e_Extratos_Bancarios`
    *   *Finalidade*: Extratos bancários da conta da campanha e notas fiscais de gastos.
    *   *Palavras-chave*: "Prestação de Contas de Campanha", "Extrato Bancário de Campanha", "Nota Fiscal Eletrônica", "Recibo de Doação Eleitoral".
    *   *Padrão Semântico*: Relatórios parciais e finais de prestação de contas eleitorais, extratos de contas correntes bancárias de campanha (Fundo Partidário/Especial) e notas fiscais de gastos.
    *   *Exemplo de Renomeação*: Extrato Bancario de Campanha.pdf
*   `03_Julgamento_Contas_e_Diplomação`
    *   *Finalidade*: Sentença do juiz eleitoral sobre as contas e diploma do candidato eleito.
    *   *Palavras-chave*: "Sentença de Prestação de Contas", "Parecer Técnico de Exame", "Diploma de Eleito", "Ata de Diplomação".
    *   *Padrão Semântico*: Sentenças de aprovação ou rejeição de contas partidárias/eleitorais, pareceres técnicos de analistas de contas e diplomas de eleitos.
    *   *Exemplo de Renomeação*: Sentenca Prestacao de Contas.pdf, Diploma de Eleito.pdf

#### M.2. Eleitoral - Contencioso (`LIT`)
Ações judiciais de fiscalização e punição eleitoral (código: LIT).
*   `01_Representacoes_Propaganda`
    *   *Finalidade*: Representações por propaganda irregular e pedidos de direito de resposta.
    *   *Palavras-chave*: "Representação por Propaganda", "Direito de Resposta Eleitoral", "Petição Inicial Eleitoral", "Liminar".
    *   *Padrão Semântico*: Representações judiciais por propaganda eleitoral antecipada ou irregular na internet/rua, direito de resposta eleitoral e decisões de liminares.
    *   *Exemplo de Renomeação*: Representacao Propaganda Eleitoral.pdf
*   `02_Acoes_Cassacao_Mandato`
    *   *Finalidade*: Ações de Investigação Judicial Eleitoral (AIJE) e recursos eleitorais.
    *   *Palavras-chave*: "Ação de Investigação Judicial", "AIJE", "Ação de Impugnação de Mandato", "AIME", "Recurso Contra Expedição".
    *   *Padrão Semântico*: Petição inicial de AIJE (Ação de Investigação Judicial Eleitoral) ou AIME (Ação de Impugnação de Mandato Eletivo) por abuso de poder.
    *   *Exemplo de Renomeação*: Acao de Investigacao Judicial AIJE.pdf
*   `03_Defesas_Recursos_TSE`
    *   *Finalidade*: Defesas processuais, agravos de instrumento e recursos perante o TSE.
    *   *Palavras-chave*: "Contestação Eleitoral", "Recurso Eleitoral Ordinário", "Recurso Especial Eleitoral", "Acórdão do TSE".
    *   *Padrão Semântico*: Contestações de candidatos, recursos eleitorais ordinários direcionados aos Tribunais Regionais Eleitorais (TRE) ou recursos especiais ao Tribunal Superior Eleitoral (TSE).
    *   *Exemplo de Renomeação*: Recurso Especial Eleitoral TSE.pdf

---
### N. Direito Digital e LGPD (`DIGITAL`)

#### N.1. Direito Digital - Adequação LGPD (`ADEQ`)
Conformidade e governança de dados pessoais (código: ADEQ).
*   `01_Mapeamento_Dados_Inventarios`
    *   *Finalidade*: Mapeamento de fluxos de dados, relatórios de impacto (RIPD) e planilhas.
    *   *Palavras-chave*: "Relatório de Impacto à Proteção", "RIPD", "Inventário de Dados Pessoais", "Data Mapping".
    *   *Padrão Semântico*: Planilhas de mapeamento de dados (data mapping), relatórios de impacto à proteção de dados pessoais (RIPD) e relatórios de conformidade.
    *   *Exemplo de Renomeação*: Relatorio de Impacto a Protecao de Dados RIPD.pdf
*   `02_Politicas_Privacidade_Termos`
    *   *Finalidade*: Políticas de privacidade, termos de uso do site/plataforma e termos de cookies.
    *   *Palavras-chave*: "Política de Privacidade", "Termos de Uso", "Política de Cookies", "Termo de Consentimento LGPD".
    *   *Padrão Semântico*: Políticas de privacidade e proteção de dados de sites, termos de uso de softwares ou aplicativos móveis e termos de consentimento expresso.
    *   *Exemplo de Renomeação*: Politica de Privacidade.pdf
*   `03_Aditivos_LGPD_Contratos_Internos`
    *   *Finalidade*: Termos aditivos de proteção de dados com fornecedores e contratos de trabalho.
    *   *Palavras-chave*: "Termo Aditivo de Proteção", "DPA", "Acordo de Processamento de Dados", "Cláusula LGPD".
    *   *Padrão Semântico*: Acordos de processamento de dados (DPA) celebrados com parceiros, aditivos contratuais de LGPD para colaboradores e cláusulas de privacidade.
    *   *Exemplo de Renomeação*: Termo Aditivo Protecao de Dados LGPD.pdf

#### N.2. Direito Digital - Incidentes (`INCID`)
Gestão de brechas de segurança e vazamentos de dados (código: INCID).
*   `01_Relatorios_Vulnerabilidade`
    *   *Finalidade*: Auditorias de segurança da informação, testes de invasão e relatórios técnicos.
    *   *Palavras-chave*: "Relatório de Teste de Invasão", "Pentest", "Análise de Vulnerabilidade", "Auditoria de TI".
    *   *Padrão Semântico*: Relatórios técnicos de testes de intrusão (pentest), varreduras de vulnerabilidades de TI, auditorias de segurança de redes e logs de incidentes cibernéticos.
    *   *Exemplo de Renomeação*: Relatorio de Teste de Invasao Pentest.pdf
*   `02_Notificacoes_Vazamento_ANPD`
    *   *Finalidade*: Notificação e comunicações formais enviadas à ANPD e aos titulares dos dados.
    *   *Palavras-chave*: "Notificação de Incidente", "Comunicação de Vazamento à ANPD", "Notificação de Vazamento aos Titulares".
    *   *Padrão Semântico*: Ofícios formais de comunicações de incidentes de segurança cibernética (vazamentos) enviados à ANPD e cartas de avisos enviadas aos titulares de dados.
    *   *Exemplo de Renomeação*: Comunicacao de Vazamento ANPD.pdf
*   `03_Planos_Contingencia`
    *   *Finalidade*: Planos de ação pós-incidente e medidas técnicas corretivas adotadas.
    *   *Palavras-chave*: "Plano de Resposta a Incidentes", "Ações Corretivas Pós-Vazamento", "Plano de Continuidade".
    *   *Padrão Semântico*: Documentos internos detalhando planos de resposta a incidentes de segurança de TI, planos de continuidade de negócios e relatórios de lições aprendidas.
    *   *Exemplo de Renomeação*: Plano de Resposta a Incidentes.pdf

## 8. Estrutura de Subpastas para Relação Jurídica (`01_RELAÇÃO_JURÍDICA`)

As 3 subpastas desta seção são estáticas. O agente utilizará RAG para classificar e mover os arquivos a estes destinos:

### `01 PROPOSTA E CONTRATO`
*   *Finalidade*: Armazenar os instrumentos de acordos de serviços.
*   *Palavras-chave*: "Contrato de Prestação de Serviços", "Contrato de Honorários Advocatícios", "Termo Aditivo", "Proposta Comercial", "Termo de Distrato".
*   *Padrão Semântico*: Cláusulas contratuais de foro, termos e valores de pagamentos e assinaturas de testemunhas/partes.
*   *Exemplo de Renomeação*: `Contrato de Honorarios.pdf`.

### `02 PROCURAÇÃO E SUBSTABELECIMENTO`
*   *Finalidade*: Documentos de delegações de poderes.
*   *Palavras-chave*: "Procuração Ad Judicia", "Procuração Extrajudicial", "Substabelecimento", "Substabelece", "Com Reserva", "Sem Reserva".
*   *Padrão Semântico*: Cláusula outorgando poderes de representação judicial para o advogado.
*   *Exemplo de Renomeação*: `Procuracao.pdf`, `Substabelecimento.pdf`.

### `03 DOCUMENTOS DE IDENTIFICAÇÃO`
*   *Finalidade*: Identificações pessoais e residenciais.
*   *Palavras-chave*: "RG", "CPF", "CNH", "Carteira de Identidade", "Comprovante de Residência", "Ficha Cadastral", "Contrato Social".
*   *Padrão Semântico*: Imagens e dados pessoais, comprovantes de contas de água, luz ou telefone no nome do cliente.
*   *Exemplo de Renomeação*: `RG.pdf`, `Comprovante de Residencia.pdf`, `Contrato Social.pdf`.

---

## 9. Estrutura da Pasta Financeiro (`02_FINANCEIRO`)

A pasta `02_FINANCEIRO` não possui nenhuma subpasta. Todos os arquivos de teor financeiro devem ser depositados diretamente nela pelo agente.

*   *Finalidade*: Guardar as transações, cobranças e notas fiscais.
*   *Palavras-chave*: "Comprovante de Depósito", "Comprovante de Transferência", "TED", "PIX", "Recibo de Pagamento", "Nota Fiscal", "NFS-e", "Boleto Bancário", "Fatura".
*   *Padrão Semântico*: Comprovantes de quitação de transações bancárias e notas de emissão fiscal de prestadores de serviços.
*   *Exemplo de Renomeação*: `Comprovante Pix.pdf`, `Nota Fiscal.pdf`, `Boleto Bancario.pdf`.

---

## 10. Casos de Borda e Regras de Fallback

Para assegurar o funcionamento ininterrupto do sistema de arquivos e integridade de documentos:

### A. Regra de Ilegibilidade (Fallback)
Sempre que a extração de texto (NLP/OCR) falhar ou retornar confiança abaixo de 75% na classificação, o agente **não tentará adivinhar**. Ele moverá o arquivo intacto para a **raiz do cliente** (ao lado de `01_RELAÇÃO_JURÍDICA`, `02_FINANCEIRO` e `03_CASO`).

### B. Arquivos Compostos (Multi-Documentos)
Na advocacia, é comum digitalizar uma Petição Inicial junto com a Procuração e os Documentos Pessoais em um único PDF de várias páginas.
*   *Regra de Decisão do Agente*: O agente lerá as primeiras 2 páginas. Se detectar o cabeçalho de Petição Inicial, o arquivo inteiro será mantido intacto e movido para a pasta de Petições Iniciais correspondente. O agente **não fatiará/desmembrará** o PDF para evitar perda de anexos, exceto se houver uma diretiva explícita de split configurada pelo usuário.

### C. Documentos Criptografados e Protegidos por Senha
Se o agente identificar que o PDF está criptografado ou requer senha para extração de texto:
*   *Ação*: Mover o arquivo para a **raiz do cliente** adicionando o sufixo `_CRIPTOGRAFADO` no nome original.

### D. Tabela de Formatos de Extensões de Arquivos

| Extensão | Processamento | Ação do Agente |
| :--- | :--- | :--- |
| `.pdf` | Leitura Completa / OCR | Indexação via RAG, classificação e renomeação. |
| `.docx` | Leitura Completa | Indexação via RAG, classificação e renomeação. |
| `.jpg` / `.png` | OCR (Imagem) | Tenta ler texto. Se falhar, move para a raiz (Fallback). |
| `.zip` / `.rar` | Apenas Nomenclatura | Mantém na raiz (Fallback) para classificação manual humana. |
| `.xlsx` / `.csv` | Apenas Nomenclatura | Move para `02_FINANCEIRO` se possuir palavras fiscais no nome, senão raiz. |
| `.mp4` / `.mp3` | Apenas Nomenclatura | Move para `03_Atas_e_Midias_Audiencia` do respectivo processo. |

---

## 11. Especificação de Prompt do Sistema (RAG LLM System Prompt)

Para colocar o agente em pleno funcionamento, o desenvolvedor deve configurar a LLM com o seguinte prompt de sistema. Este prompt define o papel do modelo de linguagem em ler o documento e consultar esta taxonomia para classificar e nomear o arquivo.

```text
Você é um agente classificador de documentos jurídicos altamente preciso. Seu papel é analisar o texto extraído de um documento (incluindo possíveis erros de OCR) e decidir em qual pasta ele deve ser roteado e qual deve ser o seu nome higienizado.

Para classificar, você DEVE consultar a taxonomia de matérias, subpastas, finalidades e palavras-chave descrita no Glossário do Sistema.

Regras Estritas de Decisão:
1. Analise o cabeçalho, qualificações, pedidos e termos do texto.
2. Compare semanticamente com as matérias (ex: IP, RT, SAUDE).
3. Selecione a subpasta destino correta (ex: "01_Boletim_e_Portaria", "02 PROCURAÇÃO E SUBSTABELECIMENTO").
4. Defina o nome do arquivo final de forma limpa, apenas com o tipo de documento (ex: "RG.pdf", "Peticao Inicial.pdf"), sem redundâncias de nome de cliente ou datas.
5. Se não tiver certeza absoluta (confiança inferior a 75%), ou se o arquivo for ilegível/criptografado, defina a pasta como "raiz" e o nome como o original.

Você deve responder ESTRITAMENTE em formato JSON com o seguinte esquema:
{
  "classificado": true,
  "codigo_materia": "CÓDIGO (ex: RT, SAUDE, ou null se for Relação Jurídica ou Financeiro)",
  "caminho_pasta_destino": "Caminho relativo da pasta (ex: 01_RELAÇÃO_JURÍDICA/01 PROPOSTA E CONTRATO ou 03_CASO/01_Boletim_e_Portaria)",
  "nome_arquivo_higienizado": "Nome limpo (ex: Procuracao.pdf)",
  "confianca_percentual": 95,
  "justificativa_semantica": "Breve justificativa baseada nos termos encontrados (ex: Presença de 'Outorgante' e poderes para o foro em geral)."
}
```
```

## 12. Guia de Desambiguação de Documentos Homônimos (Disambiguation Rules)

Para evitar que o agente classifique arquivos em pastas incorretas devido a termos sobrepostos (como contratos, procurações ou sentenças em diferentes matérias), o agente deve aplicar as seguintes regras de distinção estritas:

| Nome do Documento | Se contiver as características... | Destino Correto | Pasta de Destino |
| :--- | :--- | :--- | :--- |
| **Contrato** | Firmado entre o **nosso escritório** e o **cliente** (ex: honorários advocatícios). | Relação Jurídica | `01_RELAÇÃO_JURÍDICA/01 PROPOSTA E CONTRATO` |
| **Contrato** | Cédula de Crédito Bancário, Financiamento, Leasing ou Empréstimo com Banco. | Cível - Direito Bancário | `03_CASO/[Código]/01_Contrato_e_Planilha_Revisional` |
| **Contrato** | Assinado com Órgão Público, Prefeitura, Estado ou União (Contrato Administrativo). | Administrativo - Licitações | `03_CASO/[Código]/05_Homologacao_e_Contrato` |
| **Contrato** | Contrato de Trabalho, admissão de funcionários, acordo de compensação de horas. | Trabalhista - Reclamação | `03_CASO/[Código]/02_Defesa_e_Cartoes_Ponto` |
| **Procuração** | Procuração outorgando poderes aos **advogados do nosso escritório** pelo cliente. | Relação Jurídica | `01_RELAÇÃO_JURÍDICA/02 PROCURAÇÃO E SUBSTABELECIMENTO` |
| **Procuração** | Procuração outorgada a **terceiros** (ex: procurações de sócios, representações antigas). | Relação Jurídica (como Documento do Cliente) | `01_RELAÇÃO_JURÍDICA/03 DOCUMENTOS DE IDENTIFICAÇÃO` |
| **Nota Fiscal / Boleto** | Relativo a despesas de custas do processo judicial ou pagamento do cliente ao escritório. | Financeiro Geral | `02_FINANCEIRO` |
| **Nota Fiscal / Boleto** | Servindo de prova em processo de cobrança ou liquidação contra o réu. | Cível - Execução / Cobrança | `03_CASO/[Código]/01_Titulo_e_Demonstrativo_Debito` |

---

## 13. Diretrizes de Indexação e Chunking para Engenharia de RAG

Ao processar este glossário em um banco de dados vetorial para consulta do agente:
1. **Injeção de Metadados Hierárquicos**: Cada bloco de texto (chunk) correspondente a uma subpasta deve herdar os metadados do seu pai direto. Exemplo: Um chunk contendo as regras de `01_Boletim_e_Portaria` deve vir indexado com a tag de metadado `{ "materia": "Criminal", "codigo": "IP" }`.
2. **Contexto Prependido**: Ao enviar o trecho recuperado (retrieved context) para o prompt da LLM, o sistema RAG deve formatar o trecho incluindo a hierarquia, por exemplo: `[Matéria: Criminal -> Subtipo: IP] Pasta: 01_Boletim_e_Portaria - Palavras-chave: ...`. Isso impede que a LLM perca a noção de onde aquela subpasta reside na árvore de diretórios.
3. **Mapeamento de Sinônimos Comuns (Dicionário do Agente)**:
   * "P.I." ou "Peça Exordial" ➔ `Peticao_Inicial`
   * "B.O." ou "T.C." ➔ `Boletim_de_Ocorrencia` / `Termo_Circunstanciado`
   * "R.O." ➔ `Recurso_Ordinario`
   * "C.D.A." ➔ `Certidao_de_Divida_Ativa`
   * "CCB" ➔ `Cedula_de_Credito_Bancario`

