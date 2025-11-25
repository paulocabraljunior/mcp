# Planus - Project Manager AI

**Planus** é uma ferramenta de análise de projetos de engenharia, impulsionada por IA, projetada para fornecer insights inteligentes sobre cronogramas, identificar riscos e garantir a conformidade com os contratos.

## Visão Geral

Este projeto utiliza uma arquitetura de frontend e backend desacoplados:
-   **Frontend:** Uma aplicação interativa construída com [Streamlit](https://streamlit.io/) que serve como dashboard para visualização de dados e interação do usuário.
-   **Backend:** Uma API robusta construída com [FastAPI](https://fastapi.tiangolo.com/) que lida com a lógica de negócio, processamento de arquivos e a análise de IA.

## Funcionalidades

-   **Análise de Cronograma:** Faça o upload de um arquivo XML do MS Project para receber uma análise detalhada sobre o progresso geral do projeto e o total de tarefas.
-   **Comparação com Contrato:** Faça o upload de um contrato (PDF/DOCX) juntamente com o cronograma para que a IA possa comparar as atividades planejadas com as cláusulas contratuais.
-   **Identificação de Riscos:** Agentes de IA analisam o cronograma para identificar riscos potenciais, tarefas atrasadas e recursos sobrecarregados.
-   **Visualizações Interativas:** Explore os dados do seu projeto através de gráficos de Gantt, histogramas de duração de tarefas e gráficos de distribuição de riscos.
-   **Relatórios em PDF:** Gere e baixe relatórios em PDF com um resumo completo da análise, incluindo gráficos e insights.
-   **Suporte a Múltiplos Idiomas:** A interface está disponível em Português, Espanhol e Inglês.

## Estrutura do Projeto

```
.
├── backend/
│   ├── app/
│   │   ├── agents/      # Lógica para os agentes de IA
│   │   ├── routers/     # Endpoints da API (ex: upload, análise)
│   │   ├── utils/       # Funções de utilidade
│   │   └── main.py      # Ponto de entrada da aplicação FastAPI
│   └── requirements.txt # Dependências Python do backend
├── frontend/
│   ├── app.py           # Código da aplicação Streamlit
│   └── requirements.txt # Dependências Python do frontend
├── packages.txt         # Dependências do sistema (ex: para gerar PDFs)
├── README.md            # Este arquivo
└── .gitignore           # Arquivos ignorados pelo Git
```

## Como Executar a Aplicação

Siga estes passos para configurar e executar o projeto localmente.

### 1. Instalar Dependências do Sistema

Esta aplicação usa a biblioteca `WeasyPrint` para gerar PDFs, que requer algumas dependências do sistema.

```bash
# Para sistemas baseados em Debian/Ubuntu
sudo apt-get update && sudo apt-get install -y $(cat packages.txt)
```

### 2. Instalar Dependências Python

O frontend e o backend têm suas próprias dependências. Instale ambas.

```bash
# Instalar dependências do frontend
pip install -r frontend/requirements.txt

# Instalar dependências do backend
pip install -r backend/requirements.txt
```

### 3. Iniciar o Servidor Backend

O frontend precisa se conectar ao backend. Inicie o servidor FastAPI em um terminal.

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
```
O servidor estará disponível em `http://localhost:8000`.

### 4. Iniciar a Aplicação Frontend

Com o backend em execução, abra um **novo terminal** e inicie a aplicação Streamlit.

```bash
streamlit run frontend/app.py
```

A aplicação estará acessível em seu navegador no endereço fornecido pelo Streamlit.
