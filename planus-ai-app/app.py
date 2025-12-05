import streamlit as st
import pandas as pd
import base64
import google.generativeai as genai

from modules.xml_tools import XMLScheduleReader
from modules.pdf_tools import PDFContractReader
from modules.agents import EngineeringAgent, RiskAgent, ReportAgent

st.set_page_config(page_title="Planus AI", page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

# --- Estado ---
if 'tasks_df' not in st.session_state: st.session_state.tasks_df = pd.DataFrame()
if 'contract_text' not in st.session_state: st.session_state.contract_text = ""
if 'risk_json' not in st.session_state: st.session_state.risk_json = None

# Inicializa Agentes
if 'engineering_agent' not in st.session_state: st.session_state.engineering_agent = EngineeringAgent()
if 'risk_agent' not in st.session_state: st.session_state.risk_agent = RiskAgent()
if 'report_agent' not in st.session_state: st.session_state.report_agent = ReportAgent()

# --- Sidebar ---
st.sidebar.title("Planus AI 🏗️")
st.session_state.language = st.sidebar.selectbox("Idioma / Language", ["pt", "es", "en"])

api_key = st.sidebar.text_input("Chave API Gemini", type="password")

# Detecção de Modelos
models = ["gemini-1.5-flash", "gemini-1.5-pro"]
if api_key and 'cached_models' not in st.session_state:
    try:
        genai.configure(api_key=api_key)
        m = [x.name.replace("models/","") for x in genai.list_models() if 'generateContent' in x.supported_generation_methods]
        if m: st.session_state.cached_models = sorted(m, key=lambda x: "flash" not in x)
    except: pass
model_name = st.sidebar.selectbox("Modelo", st.session_state.get('cached_models', models))

if api_key:
    st.session_state.risk_agent.set_api_key(api_key)
    st.session_state.risk_agent.set_model(model_name)
    st.session_state.report_agent.set_api_key(api_key)
    st.session_state.report_agent.set_model(model_name)

# --- BOTÃO DE CONEXÃO (Visual Ajustado) ---
if st.sidebar.button("Testar Conexão", use_container_width=True):
    if not api_key:
        st.session_state.api_key_valid = False
        st.sidebar.error("Insira a chave.")
    else:
        try:
            res = st.session_state.risk_agent.generate_content("Ping")
            if "Error" in res: raise Exception(res)
            st.session_state.api_key_valid = True
        except:
            st.session_state.api_key_valid = False

# Status Centralizado
status = "🟢 Conectado" if st.session_state.get('api_key_valid') else "🔴 Desconectado"
st.sidebar.markdown(f"<div style='text-align:center; margin-top:5px; font-weight:bold;'>{status}</div>", unsafe_allow_html=True)

# --- ABAS (NOVA ORDEM) ---
tabs = st.tabs(["📂 Ingestão", "⚙️ Engenharia", "📅 Cronograma", "📈 Curva S", "⚠️ Riscos", "📄 Relatório"])

# 1. Ingestão
with tabs[0]:
    st.header("Ingestão de Dados")
    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("Cronograma (.xml)", type=['xml'])
        if f1:
            df = XMLScheduleReader.parse_xml(f1)
            if not df.empty:
                st.session_state.tasks_df = df
                st.success(f"Carregado: {len(df)} tarefas")
    with c2:
        f2 = st.file_uploader("Contrato (.pdf)", type=['pdf'])
        if f2:
            txt = PDFContractReader.extract_text(f2)
            if txt:
                st.session_state.contract_text = txt
                st.success("Contrato lido com sucesso.")

# 2. Engenharia
with tabs[1]:
    st.header("Engenharia & Caminho Crítico")
    if not st.session_state.tasks_df.empty:
        cp = st.session_state.engineering_agent.calculate_critical_path(st.session_state.tasks_df)
        st.metric("Total de Tarefas Críticas", len(cp))
        st.dataframe(cp, use_container_width=True)
        st.session_state.critical_path = cp
    else: st.info("Aguardando upload do XML.")

# 3. Cronograma (Gantt)
with tabs[2]:
    st.header("Gantt Interativo")
    if not st.session_state.tasks_df.empty:
        fig = st.session_state.engineering_agent.calculate_gantt_chart(st.session_state.tasks_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.session_state.fig_gantt = fig # Salva para o relatório
    else: st.info("Sem dados.")

# 4. Curva S (Com Tendência)
with tabs[3]:
    st.header("Curva S Integrada")
    if not st.session_state.tasks_df.empty:
        fig = st.session_state.engineering_agent.calculate_s_curve(st.session_state.tasks_df, st.session_state.language)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.session_state.fig_scurve = fig # Salva para o relatório
            st.caption("Linha Vermelha: Tendência Linear | Barras Verdes: Avanço Semanal")
    else: st.info("Sem dados.")

# 5. Riscos (Aninhado e Colorido - LÓGICA CORRIGIDA)
with tabs[4]:
    st.header("Análise de Riscos")
    if st.button("🔍 Analisar Riscos (IA)"):
        if api_key and not st.session_state.tasks_df.empty:
            with st.spinner("Analisando..."):
                cp = st.session_state.engineering_agent.calculate_critical_path(st.session_state.tasks_df)
                rj = st.session_state.risk_agent.analyze_risks(st.session_state.contract_text, cp, st.session_state.language)
                st.session_state.risk_json = rj

    # Exibição Aninhada por Nível
    if st.session_state.risk_json:
        rj = st.session_state.risk_json
        # Categorização
        high = [r for r in rj if "alto" in r.get('probability','').lower() or "high" in r.get('probability','').lower()]
        medium = [r for r in rj if "médio" in r.get('probability','').lower() or "medium" in r.get('probability','').lower()]
        low = [r for r in rj if "baixo" in r.get('probability','').lower() or "low" in r.get('probability','').lower()]
        none = [r for r in rj if "nenhum" in r.get('probability','').lower() or "none" in r.get('probability','').lower()]

        # 1. Risco Alto (Vermelho)
        if high:
            with st.expander(f"🔴 Risco Alto ({len(high)})", expanded=True):
                for r in high:
                    st.markdown(f"**{r.get('title')}**")
                    st.write(r.get('description'))
                    st.info(f"Mitigação: {r.get('mitigation')}")
                    st.divider()

        # 2. Risco Médio (Laranja)
        if medium:
            with st.expander(f"🟠 Risco Médio ({len(medium)})", expanded=True):
                for r in medium:
                    st.markdown(f"**{r.get('title')}**")
                    st.write(r.get('description'))
                    st.caption(f"Mitigação: {r.get('mitigation')}")
                    st.divider()

        # 3. Risco Baixo (Amarelo)
        if low:
            with st.expander(f"🟡 Risco Baixo ({len(low)})", expanded=False):
                for r in low:
                    st.markdown(f"**{r.get('title')}**")
                    st.write(r.get('description'))

        # 4. Sem Risco (Verde)
        if none:
            with st.expander(f"🟢 Sem Risco Aparente ({len(none)})", expanded=False):
                for r in none:
                    st.markdown(f"**{r.get('title')}**")
                    st.write(r.get('description'))

# 6. Relatório (Rápido + Estiloso)
with tabs[5]:
    st.header("Relatório Final")
    if st.button("📄 Gerar PDF"):
        if st.session_state.risk_json:
            with st.spinner("Compilando..."):
                summ = st.session_state.report_agent.generate_executive_summary(st.session_state.risk_json, None, st.session_state.language)

                charts = []
                # Reduz escala para 1.5 para gerar muito mais rápido
                for k in ['fig_gantt', 'fig_scurve']:
                    if k in st.session_state:
                        charts.append(base64.b64encode(st.session_state[k].to_image(format="png", width=1000, height=500, scale=1.5)).decode())

                pdf = st.session_state.report_agent.generate_pdf({'summary': summ, 'risk_analysis_json': st.session_state.risk_json, 'charts': charts}, st.session_state.language)

                if isinstance(pdf, bytes):
                    st.download_button("Baixar PDF", pdf, "Relatorio_Planus.pdf", "application/pdf")
                else: st.error(f"Erro: {pdf}")
        else: st.warning("Gere os riscos primeiro.")
