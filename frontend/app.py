import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import io
import base64

def create_chart_img(fig):
    """Convert Plotly fig to base64 image"""
    # Force colorful template
    fig.update_layout(template="plotly_white")
    img_bytes = fig.to_image(format="png", width=800, height=400, scale=2)
    return base64.b64encode(img_bytes).decode('utf-8')

def create_pdf(analysis_data, text_report, charts=[], language="pt"):
    # CSS Styles - Modern and Colorful
    css = """
    <style>
        @page { size: A4; margin: 2cm; }
        body { 
            font-family: 'Helvetica', 'Arial', sans-serif; 
            color: #31333F; 
            line-height: 1.6; 
            font-size: 12px;
        }
        h1 { 
            color: #0e1117; 
            border-bottom: 2px solid #ff4b4b; 
            padding-bottom: 15px; 
            font-size: 24px; 
            margin-bottom: 30px; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        h2 { 
            color: #0e1117; 
            margin-top: 30px; 
            background-color: #f0f2f6; 
            padding: 12px; 
            border-radius: 8px; 
            font-size: 16px; 
            border-left: 5px solid #ff4b4b;
        }
        h3 { 
            color: #31333F; 
            font-size: 14px; 
            margin-top: 20px; 
            border-bottom: 1px solid #e6e9ef;
            padding-bottom: 5px;
        }
        
        /* Chart Container */
        .chart-container { 
            margin: 25px 0; 
            text-align: center; 
            page-break-inside: avoid; 
            border: 1px solid #e6e9ef; 
            padding: 20px; 
            border-radius: 8px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .chart-title { 
            font-weight: bold; 
            color: #31333F; 
            margin-bottom: 15px; 
            font-size: 14px; 
            text-transform: uppercase;
        }
        .chart-img { width: 100%; max-width: 100%; }

        /* Badge Styles - Mimic Streamlit */
        .risk-badge { 
            padding: 4px 8px; 
            border-radius: 4px; 
            color: white; 
            font-weight: bold; 
            font-size: 0.85em; 
            display: inline-block; 
            vertical-align: middle;
        }
        .risk-high { background-color: #ff4b4b; }
        .risk-medium { background-color: #ffa421; }
        .risk-low { background-color: #21c354; }
        
        /* Lists */
        ul { padding-left: 20px; margin-bottom: 15px; }
        li { margin-bottom: 8px; }
        
        /* Strong text */
        b, strong { color: #0e1117; font-weight: 600; }
        
        /* Header/Footer */
        .header { text-align: center; margin-bottom: 40px; }
        .footer { 
            position: fixed; 
            bottom: 0; 
            left: 0; 
            right: 0; 
            text-align: center; 
            font-size: 10px; 
            color: #808495; 
            border-top: 1px solid #e6e9ef; 
            padding-top: 10px;
        }
    </style>
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        {css}
    </head>
    <body>
        <div class="header">
            <h1>Planus - Project Manager AI</h1>
            <p style="color: #808495; font-size: 12px;">Report Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
    """
    
    # Map charts by title for easy access
    chart_map = {title: fig for title, fig in charts}
    inserted_charts = set()
    
    # Split text report by sections (assuming markdown headers)
    sections = text_report.split('## ')
    
    for section in sections:
        if not section.strip(): continue
        
        # Re-add the header tag
        if not section.startswith('# '):
            title_line = section.split('\n')[0]
            body = '\n'.join(section.split('\n')[1:])
            html_content += f"<h2>{title_line}</h2>"
            
            # Convert body markdown to HTML (basic)
            body_html = body.replace('\n', '<br/>')
            body_html = body_html.replace('**', '<b>').replace('**', '</b>')
            
            # Colorize risk levels with Badges
            body_html = body_html.replace('[ALTO]', '<span class="risk-badge risk-high">ALTO</span>')
            body_html = body_html.replace('[CRITICO]', '<span class="risk-badge risk-high">CRÍTICO</span>')
            body_html = body_html.replace('[MEDIO]', '<span class="risk-badge risk-medium">MÉDIO</span>')
            body_html = body_html.replace('[BAIXO]', '<span class="risk-badge risk-low">BAIXO</span>')
            
            html_content += f"<div style='margin-bottom: 20px;'>{body_html}</div>"
            
            # Logic to insert specific charts based on section title
            section_upper = title_line.upper()
            
            # Helper to add chart
            def add_chart_html(t, fig):
                return f'''
                <div class="chart-container">
                    <div class="chart-title">{t}</div>
                    <img src="data:image/png;base64,{create_chart_img(fig)}" class="chart-img"/>
                </div>
                '''

            # 1. Risk Analysis Section
            if "RISCO" in section_upper or "RISK" in section_upper or "RIESGO" in section_upper:
                for t, fig in charts:
                    if t not in inserted_charts and ("DIST" in t.upper() and ("RISK" in t.upper() or "RISCO" in t.upper() or "RIESGO" in t.upper())):
                        html_content += add_chart_html(t, fig)
                        inserted_charts.add(t)

            # 2. Delayed Tasks Section
            elif "ATRASADA" in section_upper or "DELAYED" in section_upper or "RETRASADA" in section_upper:
                 for t, fig in charts:
                    if t not in inserted_charts and ("DELAY" in t.upper() or "ATRASO" in t.upper()):
                        html_content += add_chart_html(t, fig)
                        inserted_charts.add(t)

            # 3. Schedule/Executive Summary Section
            elif "CRONOGRAMA" in section_upper or "SCHEDULE" in section_upper or "RESUMO" in section_upper or "SUMMARY" in section_upper or "RESUMEN" in section_upper:
                 for t, fig in charts:
                    if t not in inserted_charts and ("SCHEDULE" in t.upper() or "CRONOGRAMA" in t.upper() or "DURATION" in t.upper() or "DURAÇÃO" in t.upper()):
                        html_content += add_chart_html(t, fig)
                        inserted_charts.add(t)
            
            # 4. Resource Analysis Section
            elif "RECURSO" in section_upper or "RESOURCE" in section_upper:
                for t, fig in charts:
                    if t not in inserted_charts and ("RESOURCE" in t.upper() or "RECURSO" in t.upper()):
                        html_content += add_chart_html(t, fig)
                        inserted_charts.add(t)

        else:
            # Main title
            html_content += f"<h1>{section.replace('# ', '')}</h1>"

    html_content += """
        <div class="footer">
            Generated by Planus - Project Manager AI
        </div>
    </body></html>
    """
    
    # Generate PDF using WeasyPrint
    font_config = FontConfiguration()
    pdf_bytes = HTML(string=html_content).write_pdf(font_config=font_config)
        
    return pdf_bytes

# Configuration
import os
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8001")

# Internationalization
TRANSLATIONS = {
    "pt": {
        "app_title": "Planus - Project Manager AI",
        "app_subtitle": "Seu agente inteligente para análises de Cronograma",
        "sidebar_header": "Ações do Projeto",
        "upload_files": "📁 Carregar Arquivos",
        "upload_schedule": "Carregar Cronograma (MS Project XML)",
        "upload_contract": "Carregar Contrato (PDF/DOCX) - Opcional",
        "schedule_uploaded": "✅ Cronograma carregado!",
        "contract_uploaded": "✅ Contrato carregado!",
        "analyze_schedule_only": "🔍 Analisar Apenas Cronograma",
        "analyze_contract_schedule": "📊 Analisar Contrato vs Cronograma",
        "analyzing": "Agentes analisando o cronograma...",
        "analyzing_contract": "Analisando contrato e comparando com cronograma...",
        "analysis_complete": "✅ Análise do cronograma completa!",
        "contract_analysis_complete": "✅ Análise do contrato completa!",
        "upload_contract_hint": "💡 Carregue um contrato para habilitar análise comparativa",
        "start_upload": "👆 Comece carregando um cronograma (arquivo XML)",
        "total_tasks": "Total de Tarefas",
        "overall_progress": "Progresso Geral",
        "agent_insights": "🤖 Insights dos Agentes",
        "schedule_analyst": "Analista de Cronograma",
        "resource_manager": "Gerente de Recursos",
        "identified_risks": "⚠️ **Riscos Identificados**",
        "delayed_tasks": "tarefas atrasadas",
        "overloaded_resources": "⚠️ **Recursos Sobrecarregados**",
        "resource_utilization": "**Utilização de Recursos (Tarefas):**",
        "visualizations": "📊 Visualizações do Projeto",
        "gantt_chart": "Gráfico de Gantt",
        "task_duration": "Duração das Tarefas",
        "resource_load": "Carga de Recursos",
        "risk_analysis": "🎯 Análise de Risco",
        "view_raw_data": "Ver Dados Brutos das Tarefas",
        "no_valid_dates": "Nenhuma data válida encontrada para o gráfico de Gantt.",
        "no_resource_data": "Nenhum dado de recursos disponível.",
        "contract_comparison": "📋 Análise Contrato vs Cronograma",
        "compliance_score": "Score de Conformidade",
        "delayed_activities": "Atividades Atrasadas",
        "missing_activities": "Atividades Faltantes",
        "contract_activities": "Atividades no Contrato",
        "delayed_tab": "🚨 Atividades Atrasadas",
        "missing_tab": "❌ Atividades Faltantes",
        "productivity_tab": "📈 Métricas de Produtividade",
        "recommendations_tab": "💡 Recomendações",
        "delay_risk_assessment": "🎯 Avaliação de Risco de Atraso",
        "project_risk_level": "Nível de Risco do Projeto",
        "high_risk_tasks": "Tarefas de Alto Risco",
        "total_analyzed": "Total de Tarefas Analisadas",
        "risk_distribution": "Distribuição de Risco",
        "high_risk_detail": "⚠️ Tarefas de Alto Risco (Nível 4-5)",
        "all_tasks_by_risk": "📋 Todas as Tarefas Classificadas por Risco",
        "upload_to_begin": "Por favor, carregue um arquivo XML do Microsoft Project para começar a análise.",
        "good": "Bom",
        "needs_attention": "Precisa Atenção",
        "critical": "Crítico",
        "on_track": "No Prazo",
        "action_required": "Ação Necessária",
        "complete": "Completo",
        "found": "Encontrado",
        "all_clear": "Tudo Certo",
        "project_schedule": "Cronograma do Projeto",
        "task_duration_dist": "Distribuição de Duração das Tarefas",
        "tasks_per_resource": "Tarefas por Recurso",
        "task_dist_by_risk": "Distribuição de Tarefas por Nível de Risco",
        "level_1_very_low": "Nível 1\n(Muito Baixo)",
        "level_2_low": "Nível 2\n(Baixo)",
        "level_3_medium": "Nível 3\n(Médio)",
        "level_4_high": "Nível 4\n(Alto)",
        "level_5_critical": "Nível 5\n(Crítico)",
        "risk_level": "Nível de Risco",
        "task": "Tarefa",
        "description": "Descrição",
        "progress": "Progresso",
        "resources": "Recursos",
        "risk_factors": "Fatores de Risco",
        "deadline": "Prazo",
        "start_date": "Data de Início",
        "none": "Nenhum",
        "no_summary": "Nenhum resumo disponível",
        "risk_not_available": "Análise de risco não disponível. Por favor, analise o projeto primeiro.",
        "recommended_actions": "Ações Recomendadas",
        "no_actions_needed": "✅ Nenhuma ação imediata necessária. Projeto no prazo!",
        "resources_attention": "⚠️ **Recursos que precisam de atenção:**",
        "analysis_failed": "Falha na análise do agente.",
        "upload_failed": "Falha no upload",
        "connection_error": "Erro de conexão",
        "resource": "Recurso",
        "task_count": "Contagem de Tarefas",
        "text_report": "📝 Relatório em Texto",
    },
    "es": {
        "app_title": "Planus - Project Manager AI",
        "app_subtitle": "Su agente inteligente para análisis de Cronograma",
        "sidebar_header": "Acciones del Proyecto",
        "upload_files": "📁 Cargar Archivos",
        "upload_schedule": "Cargar Cronograma (MS Project XML)",
        "upload_contract": "Cargar Contrato (PDF/DOCX) - Opcional",
        "schedule_uploaded": "✅ ¡Cronograma cargado!",
        "contract_uploaded": "✅ ¡Contrato cargado!",
        "analyze_schedule_only": "🔍 Analizar Solo Cronograma",
        "analyze_contract_schedule": "📊 Analizar Contrato vs Cronograma",
        "analyzing": "Agentes analizando el cronograma...",
        "analyzing_contract": "Analizando contrato y comparando con cronograma...",
        "analysis_complete": "✅ ¡Análisis del cronograma completo!",
        "contract_analysis_complete": "✅ ¡Análisis del contrato completo!",
        "upload_contract_hint": "💡 Cargue un contrato para habilitar análisis comparativo",
        "start_upload": "👆 Comience cargando un cronograma (archivo XML)",
        "total_tasks": "Total de Tareas",
        "overall_progress": "Progreso General",
        "agent_insights": "🤖 Insights de los Agentes",
        "schedule_analyst": "Analista de Cronograma",
        "resource_manager": "Gestor de Recursos",
        "identified_risks": "⚠️ **Riesgos Identificados**",
        "delayed_tasks": "tareas retrasadas",
        "overloaded_resources": "⚠️ **Recursos Sobrecargados**",
        "resource_utilization": "**Utilización de Recursos (Tareas):**",
        "visualizations": "📊 Visualizaciones del Proyecto",
        "gantt_chart": "Diagrama de Gantt",
        "task_duration": "Duración de Tareas",
        "resource_load": "Carga de Recursos",
        "risk_analysis": "🎯 Análisis de Riesgo",
        "view_raw_data": "Ver Datos Brutos de Tareas",
        "no_valid_dates": "No se encontraron fechas válidas para el diagrama de Gantt.",
        "no_resource_data": "No hay datos de recursos disponibles.",
        "contract_comparison": "📋 Análisis Contrato vs Cronograma",
        "compliance_score": "Puntuación de Cumplimiento",
        "delayed_activities": "Actividades Retrasadas",
        "missing_activities": "Actividades Faltantes",
        "contract_activities": "Actividades en Contrato",
        "delayed_tab": "🚨 Actividades Retrasadas",
        "missing_tab": "❌ Actividades Faltantes",
        "productivity_tab": "📈 Métricas de Productividad",
        "recommendations_tab": "💡 Recomendaciones",
        "delay_risk_assessment": "� Evaluación de Riesgo de Retraso",
        "project_risk_level": "Nivel de Riesgo del Proyecto",
        "high_risk_tasks": "Tareas de Alto Riesgo",
        "total_analyzed": "Total de Tareas Analizadas",
        "risk_distribution": "Distribución de Riesgo",
        "high_risk_detail": "⚠️ Tareas de Alto Riesgo (Nivel 4-5)",
        "all_tasks_by_risk": "📋 Todas las Tareas Clasificadas por Riesgo",
        "upload_to_begin": "Por favor, cargue un archivo XML de Microsoft Project para comenzar el análisis.",
        "good": "Bueno",
        "needs_attention": "Necesita Atención",
        "critical": "Crítico",
        "on_track": "En Tiempo",
        "action_required": "Acción Requerida",
        "complete": "Completo",
        "text_report": "📝 Informe en Texto",
    },
    "en": {
        "app_title": "Planus - Project Manager AI",
        "app_subtitle": "Your intelligent agent for Schedule analysis",
        "sidebar_header": "Project Actions",
        "upload_files": "📁 Upload Files",
        "upload_schedule": "Upload Schedule (MS Project XML)",
        "upload_contract": "Upload Contract (PDF/DOCX) - Optional",
        "schedule_uploaded": "✅ Schedule uploaded!",
        "contract_uploaded": "✅ Contract uploaded!",
        "analyze_schedule_only": "🔍 Analyze Schedule Only",
        "analyze_contract_schedule": "📊 Analyze Contract vs Schedule",
        "analyzing": "Agents are analyzing the schedule...",
        "analyzing_contract": "Analyzing contract and comparing with schedule...",
        "analysis_complete": "✅ Schedule analysis complete!",
        "contract_analysis_complete": "✅ Contract analysis complete!",
        "upload_contract_hint": "💡 Upload a contract to enable comparison analysis",
        "start_upload": "👆 Start by uploading a schedule (XML file)",
        "total_tasks": "Total Tasks",
        "overall_progress": "Overall Progress",
        "agent_insights": "🤖 Agent Insights",
        "schedule_analyst": "Schedule Analyst",
        "resource_manager": "Resource Manager",
        "identified_risks": "⚠️ **Identified Risks**",
        "delayed_tasks": "delayed tasks",
        "overloaded_resources": "⚠️ **Overloaded Resources**",
        "resource_utilization": "**Resource Utilization (Tasks):**",
        "visualizations": "📊 Project Visualizations",
        "gantt_chart": "Gantt Chart",
        "task_duration": "Task Duration",
        "resource_load": "Resource Load",
        "risk_analysis": "🎯 Risk Analysis",
        "view_raw_data": "View Raw Task Data",
        "no_valid_dates": "No valid dates found for Gantt chart.",
        "no_resource_data": "No resource data available.",
        "contract_comparison": "📋 Contract vs Schedule Analysis",
        "compliance_score": "Compliance Score",
        "delayed_activities": "Delayed Activities",
        "missing_activities": "Missing Activities",
        "contract_activities": "Contract Activities",
        "delayed_tab": "🚨 Delayed Activities",
        "missing_tab": "❌ Missing Activities",
        "productivity_tab": "📈 Productivity Metrics",
        "recommendations_tab": "💡 Recommendations",
        "delay_risk_assessment": "🎯 Delay Risk Assessment",
        "project_risk_level": "Project Risk Level",
        "high_risk_tasks": "High Risk Tasks",
        "total_analyzed": "Total Tasks Analyzed",
        "risk_distribution": "Risk Distribution",
        "high_risk_detail": "⚠️ High Risk Tasks (Level 4-5)",
        "all_tasks_by_risk": "📋 All Tasks Ranked by Risk",
        "upload_to_begin": "Please upload a Microsoft Project XML file to begin analysis.",
        "good": "Good",
        "needs_attention": "Needs Attention",
        "critical": "Critical",
        "on_track": "On Track",
        "action_required": "Action Required",
        "complete": "Complete",
        "text_report": "📝 Text Report",
    }
}

def t(key):
    """Get translation for current language"""
    lang = st.session_state.get('language', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

st.set_page_config(
    page_title="Planus - Project Manager AI",
    page_icon="🏗️",
    layout="wide"
)

# Language selector in top right
col1, col2 = st.columns([6, 1])
with col1:
    st.title(t("app_title"))
    st.markdown(f"### {t('app_subtitle')}")
with col2:
    st.write("")  # spacing
    selected_lang = st.radio(
        "🌐",
        options=["pt", "es", "en"],
        format_func=lambda x: {"pt": "🇧🇷", "es": "🇪🇸", "en": "🇬🇧"}[x],
        horizontal=True,
        key="language",
        label_visibility="collapsed"
    )


# Sidebar for actions
st.sidebar.header(t("sidebar_header"))

# Single XML upload for both analyses
st.sidebar.subheader(t("upload_files"))
schedule_file = st.sidebar.file_uploader(t("upload_schedule"), type=["xml"], key="schedule_xml")
contract_file = st.sidebar.file_uploader(t("upload_contract"), type=["pdf", "docx", "doc"], key="contract_file")

st.sidebar.divider()

# Analysis buttons
if schedule_file:
    st.sidebar.success(t("schedule_uploaded"))
    
    # Button 1: Analyze Schedule Only
    if st.sidebar.button(t("analyze_schedule_only"), key="analyze_schedule", use_container_width=True):
        with st.spinner(t("analyzing")):
            try:
                # 1. Upload File
                files = {"file": (schedule_file.name, schedule_file.getvalue(), "text/xml")}
                response = requests.post(f"{API_URL}/projects/upload", files=files)
                
                if response.status_code == 200:
                    tasks_data = response.json()
                    st.session_state['tasks'] = tasks_data
                    
                    # 2. Run Analysis Agent
                    analysis_response = requests.post(f"{API_URL}/projects/analyze", json=tasks_data)
                    if analysis_response.status_code == 200:
                        st.session_state['analysis'] = analysis_response.json()
                        st.session_state['contract_analysis'] = None  # Clear contract analysis
                        st.sidebar.success(t("analysis_complete"))
                        st.rerun()
                    else:
                        st.error(t('analysis_failed'))
                else:
                    st.error(f"{t('upload_failed')}: {response.text}")
            except Exception as e:
                st.error(f"{t('connection_error')}: {e}")
    
    # Button 2: Analyze Contract vs Schedule (only if contract is uploaded)
    if contract_file:
        st.sidebar.success(t("contract_uploaded"))
        
        if st.sidebar.button(t("analyze_contract_schedule"), key="analyze_contract", use_container_width=True):
            with st.spinner(t("analyzing_contract")):
                try:
                    # Send both files to contract analysis endpoint
                    files = {
                        "contract_file": (contract_file.name, contract_file.getvalue(), 
                                         "application/pdf" if contract_file.name.endswith('.pdf') else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                        "schedule_file": (schedule_file.name, schedule_file.getvalue(), "text/xml")
                    }
                    current_lang = st.session_state.get('language', 'pt')
                    response = requests.post(
                        f"{API_URL}/projects/analyze-contract", 
                        files=files,
                        params={"language": current_lang}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state['contract_analysis'] = result
                        st.session_state['analysis'] = result # Now contains full analysis including risk
                        
                        # Also parse schedule for display
                        schedule_response = requests.post(
                            f"{API_URL}/projects/upload",
                            files={"file": (schedule_file.name, schedule_file.getvalue(), "text/xml")}
                        )
                        if schedule_response.status_code == 200:
                            st.session_state['tasks'] = schedule_response.json()
                        
                        st.sidebar.success(t("contract_analysis_complete"))
                        st.rerun()
                    else:
                        st.error(f"{t('upload_failed')}: {response.text}")
                except Exception as e:
                    st.error(f"{t('connection_error')}: {e}")
    else:
        st.sidebar.info(t("upload_contract_hint"))
else:
    st.sidebar.info(t("start_upload"))


# Main Dashboard
if 'tasks' in st.session_state:
    tasks = st.session_state['tasks']
    analysis = st.session_state.get('analysis', {})
    
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(tasks)
    
    # Format list columns for display
    if 'resource_names' in df.columns:
        df['resource_names'] = df['resource_names'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
    if 'predecessors' in df.columns:
        df['predecessors'] = df['predecessors'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
    if not df.empty:
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t("total_tasks"), len(df))
        
        # Calculate completion
        avg_complete = df['percent_complete'].mean()
        col2.metric(t("overall_progress"), f"{avg_complete:.1f}%")
        
        # Agent Insights
        st.divider()
        st.subheader(t("agent_insights"))
        
        if analysis:
            # Schedule Analyst
            sched = analysis.get('schedule_analysis', {})
            res = analysis.get('resource_analysis', {})
            chart = analysis.get('chart_data', {})

            col_sched, col_res = st.columns(2)
            
            with col_sched:
                sched_summary = sched.get('summary', {})
                current_lang = st.session_state.get('language', 'pt')
                if isinstance(sched_summary, dict):
                    display_sched = sched_summary.get(current_lang, sched_summary.get('en', ''))
                    st.info(f"**{t('schedule_analyst')}**: {display_sched}")
                else:
                    st.info(f"**{t('schedule_analyst')}**: {sched_summary}")

                if 'risks' in sched:
                    st.warning(t("identified_risks"))
                    for risk in sched['risks']:
                        st.write(f"- {risk}")
                if 'delayed_tasks' in sched and sched['delayed_tasks']:
                    st.error(f"{t('found')} {len(sched['delayed_tasks'])} {t('delayed_tasks')}.")

            with col_res:
                res_summary = res.get('summary', {})
                if isinstance(res_summary, dict):
                    display_res = res_summary.get(current_lang, res_summary.get('en', ''))
                    st.info(f"**{t('resource_manager')}**: {display_res}")
                else:
                    st.info(f"**{t('resource_manager')}**: {res_summary}")

                if 'overloaded_resources' in res and res['overloaded_resources']:
                    st.warning(f"{t('overloaded_resources')}: {', '.join(res['overloaded_resources'])}")
                
                st.write(t("resource_utilization"))
                st.json(res.get('utilization', {}))

        # Visualizations
        st.divider()
        st.subheader(t("visualizations"))
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([t("gantt_chart"), t("task_duration"), t("resource_load"), t("risk_analysis"), t("text_report")])
        
        with tab1:
            # Simple Gantt using Plotly Timeline
            valid_dates = df.dropna(subset=['start_date', 'finish_date'])
            if not valid_dates.empty:
                fig_gantt = px.timeline(
                    valid_dates, 
                    x_start="start_date", 
                    x_end="finish_date", 
                    y="name",
                    color="percent_complete",
                    title=t("project_schedule")
                )
                fig_gantt.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_gantt, use_container_width=True)
                if 'charts' not in st.session_state: st.session_state['charts'] = []
                # Avoid duplicates
                if not any(c[0] == t("project_schedule") for c in st.session_state['charts']):
                    st.session_state['charts'].append((t("project_schedule"), fig_gantt))
            else:
                st.warning(t("no_valid_dates"))
                
        with tab2:
            fig_hist = px.histogram(df, x="duration", title=t("task_duration_dist"))
            st.plotly_chart(fig_hist, use_container_width=True)
            if 'charts' not in st.session_state: st.session_state['charts'] = []
            if not any(c[0] == t("task_duration_dist") for c in st.session_state['charts']):
                st.session_state['charts'].append((t("task_duration_dist"), fig_hist))

        with tab3:
            if analysis and 'chart_data' in analysis:
                res_dist = analysis['chart_data'].get('resource_distribution', {})
                if res_dist:
                    res_df = pd.DataFrame(list(res_dist.items()), columns=[t('resource'), t('task_count')])
                    fig_res = px.bar(res_df, x=t('resource'), y=t('task_count'), title=t("tasks_per_resource"))
                    st.plotly_chart(fig_res, use_container_width=True)
                else:
                    st.info(t("no_resource_data"))
        
        with tab4:
            # Risk Analysis Tab
            if analysis and 'risk_analysis' in analysis:
                risk_data = analysis['risk_analysis']
                
                st.subheader(t("delay_risk_assessment"))
                # Summary
                summary = risk_data.get('summary', {})
                current_lang = st.session_state.get('language', 'pt')
                if isinstance(summary, dict):
                    display_summary = summary.get(current_lang, summary.get('en', ''))
                    st.info(f"**{display_summary if display_summary else t('no_summary')}**")
                else:
                    st.info(f"**{summary if summary else t('no_summary')}**")
                
                # Risk Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(t("project_risk_level"), 
                             f"Level {risk_data.get('project_risk_level', 'N/A')}",
                             delta=f"Avg: {risk_data.get('average_risk_score', 0):.2f}")
                with col2:
                    high_risk_count = len(risk_data.get('high_risk_tasks', []))
                    st.metric(t("high_risk_tasks"), high_risk_count,
                             delta=t("needs_attention") if high_risk_count > 0 else t("all_clear"),
                             delta_color="inverse" if high_risk_count > 0 else "normal")
                with col3:
                    st.metric(t("total_analyzed"), risk_data.get('total_tasks_analyzed', 0))
                
                # Risk Distribution Chart
                st.subheader(t("risk_distribution"))
                risk_dist = risk_data.get('risk_distribution', {})
                if risk_dist:
                    dist_data = {
                        t('risk_level'): [t('level_1_very_low'), t('level_2_low'), t('level_3_medium'), 
                                      t('level_4_high'), t('level_5_critical')],
                        'Count': [
                            risk_dist.get('level_1', 0),
                            risk_dist.get('level_2', 0),
                            risk_dist.get('level_3', 0),
                            risk_dist.get('level_4', 0),
                            risk_dist.get('level_5', 0)
                        ],
                        'Color': ['green', 'lightgreen', 'orange', 'orangered', 'red']
                    }
                    dist_df = pd.DataFrame(dist_data)
                    
                    fig_risk_dist = px.bar(
                        dist_df, 
                        x=t('risk_level'), 
                        y='Count',
                        color=t('risk_level'),
                        title=t("task_dist_by_risk"),
                        color_discrete_map={
                            t('level_1_very_low'): 'green',
                            t('level_2_low'): 'lightgreen',
                            t('level_3_medium'): 'orange',
                            t('level_4_high'): 'orangered',
                            t('level_5_critical'): 'red'
                        }
                    )
                    st.plotly_chart(fig_risk_dist, use_container_width=True)
                    if 'charts' not in st.session_state: st.session_state['charts'] = []
                    if not any(c[0] == t("task_dist_by_risk") for c in st.session_state['charts']):
                        st.session_state['charts'].append((t("task_dist_by_risk"), fig_risk_dist))
                
                # High Risk Tasks Detail
                high_risk_tasks = risk_data.get('high_risk_tasks', [])
                if high_risk_tasks:
                    st.subheader("⚠️ High Risk Tasks (Level 4-5)")
                    for task in high_risk_tasks:
                        risk_desc = task.get('risk_description', {})
                        desc_text = risk_desc.get(current_lang, risk_desc.get('en', '')) if isinstance(risk_desc, dict) else str(risk_desc)
                        
                        with st.expander(f"🔴 {task['task_name']} - {desc_text}", expanded=True):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write(f"**{t('risk_level')}:** {task['risk_level']}/5")
                                st.write(f"**{t('progress')}:** {task['percent_complete']}%")
                                if task['resources']:
                                    st.write(f"**{t('resources')}:** {', '.join(task['resources'])}")
                            with col_b:
                                if task.get('finish_date'):
                                    st.write(f"**{t('deadline')}:** {task['finish_date'][:10]}")
                                if task.get('start_date'):
                                    st.write(f"**{t('start_date')}:** {task['start_date'][:10]}")
                            
                            if task.get('risk_factors'):
                                st.write(f"**{t('risk_factors')}:**")
                                for factor in task['risk_factors']:
                                    st.write(f"- {factor}")
                
                # All Tasks by Risk
                st.subheader("📋 All Tasks Ranked by Risk")
                tasks_by_risk = risk_data.get('tasks_by_risk', [])
                
                if tasks_by_risk:
                    # Create DataFrame for display
                    risk_table_data = []
                    for task in tasks_by_risk:
                        risk_table_data.append({
                            t('task'): task['task_name'],
                            t('risk_level'): task['risk_level'],
                            t('description'): task['risk_description'],
                            t('progress'): f"{task['percent_complete']}%",
                            t('resources'): ', '.join(task['resources']) if task['resources'] else t('none')
                        })
                    
                    risk_table_df = pd.DataFrame(risk_table_data)
                    
                    # Color code by risk level
                    def color_risk_level(val):
                        if val == 5:
                            return 'background-color: #ff4444; color: white'
                        elif val == 4:
                            return 'background-color: #ff8844; color: white'
                        elif val == 3:
                            return 'background-color: #ffaa44'
                        elif val == 2:
                            return 'background-color: #88ff88'
                        else:
                            return 'background-color: #44ff44'
                    
                    styled_df = risk_table_df.style.applymap(
                        color_risk_level, 
                        subset=[t('risk_level')]
                    )
                    
                    st.dataframe(styled_df, use_container_width=True, height=400)
            else:
                st.info(t("risk_not_available"))
        
        with tab5:
            # Text Report Tab
            if analysis and 'text_reports' in analysis:
                text_reports = analysis['text_reports']
                current_lang = st.session_state.get('language', 'pt')
                
                # Get report for current language
                report_text = text_reports.get(current_lang, text_reports.get('pt', ''))
                
                if report_text:
                    # Display the markdown report
                    st.markdown(report_text)
                    
                    st.download_button(
                        label="📥 " + ("Baixar Relatório PDF" if current_lang == "pt" else "Descargar Informe PDF" if current_lang == "es" else "Download PDF Report"),
                        data=create_pdf(analysis, report_text, st.session_state.get('charts', [])),
                        file_name=f"relatorio_cronograma_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.info(t("risk_not_available"))
            else:
                st.info(t("risk_not_available"))

        # Data Table
        with st.expander(t("view_raw_data")):
            st.dataframe(df)


# Contract Analysis Results
if 'contract_analysis' in st.session_state and st.session_state['contract_analysis']:
    st.divider()
    st.header(t("contract_comparison"))
    
    contract_result = st.session_state['contract_analysis']
    comparison = contract_result.get('comparison', {})
    
    # Summary
    st.info(f"**📊 {comparison.get('summary', t('no_summary'))}**")
    
    # Compliance Score
    compliance_score = comparison.get('compliance_score', 0)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(t("compliance_score"), f"{compliance_score:.1f}%", 
                 delta=t("good") if compliance_score >= 80 else t("needs_attention"),
                 delta_color="normal" if compliance_score >= 80 else "inverse")
    
    with col2:
        delayed_count = len(comparison.get('delayed_activities', []))
        st.metric(t("delayed_activities"), delayed_count,
                 delta=t("critical") if delayed_count > 0 else t("on_track"),
                 delta_color="inverse" if delayed_count > 0 else "normal")
    
    with col3:
        missing_count = len(comparison.get('missing_activities', []))
        st.metric(t("missing_activities"), missing_count,
                 delta=t("action_required") if missing_count > 0 else t("complete"),
                 delta_color="inverse" if missing_count > 0 else "normal")
    
    with col4:
        contract_data = contract_result.get('contract_data', {})
        st.metric(t("contract_activities"), contract_data.get('activities_found', 0))
    
    # Detailed Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        t("delayed_tab"), 
        t("missing_tab"), 
        t("productivity_tab"),
        t("recommendations_tab")
    ])
    
    with tab1:
        delayed = comparison.get('delayed_activities', [])
        if delayed:
            st.warning(f"**{len(delayed)} activities are behind schedule:**")
            
            # Create DataFrame for better display
            delayed_df = pd.DataFrame(delayed)
            if not delayed_df.empty:
                delayed_df['finish_date'] = pd.to_datetime(delayed_df['finish_date']).dt.strftime('%Y-%m-%d')
                st.dataframe(
                    delayed_df[['name', 'finish_date', 'percent_complete', 'days_delayed', 'resources']],
                    use_container_width=True
                )
                
                # Chart of delayed activities
                fig = px.bar(
                    delayed_df, 
                    x='days_delayed', 
                    y='name',
                    color='percent_complete',
                    title="Days Delayed by Activity",
                    labels={'days_delayed': 'Days Overdue', 'name': 'Activity'},
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
                if 'charts' not in st.session_state: st.session_state['charts'] = []
                if not any(c[0] == "Days Delayed" for c in st.session_state['charts']):
                    st.session_state['charts'].append(("Days Delayed", fig))
        else:
            st.success("✅ No delayed activities! All tasks are on schedule.")
    
    with tab2:
        missing = comparison.get('missing_activities', [])
        extra = comparison.get('extra_activities', [])
        
        if missing:
            st.error(f"**{len(missing)} activities mentioned in contract but missing from schedule:**")
            for i, activity in enumerate(missing, 1):
                st.write(f"{i}. {activity}")
        else:
            st.success("✅ All contract activities are present in the schedule.")
        
        if extra:
            st.info(f"**{len(extra)} activities in schedule not explicitly mentioned in contract:**")
            with st.expander("View extra activities"):
                for i, activity in enumerate(extra, 1):
                    st.write(f"{i}. {activity}")
    
    with tab3:
        productivity = comparison.get('productivity_metrics', [])
        if productivity:
            st.write("**Resource Productivity Analysis:**")
            
            # Create DataFrame
            prod_df = pd.DataFrame(productivity)
            
            # Display table
            st.dataframe(
                prod_df[[
                    'resource_name', 'assigned_tasks', 'completed_tasks',
                    'productivity_index', 'status'
                ]].style.format({
                    'productivity_index': '{:.2%}'
                }).background_gradient(subset=['productivity_index'], cmap='RdYlGn'),
                use_container_width=True
            )
            
            # Productivity chart
            fig_prod = px.bar(
                prod_df,
                x='resource_name',
                y='productivity_index',
                color='status',
                title="Resource Productivity Index",
                labels={'productivity_index': 'Productivity Index', 'resource_name': 'Resource'},
                color_discrete_map={'efficient': 'green', 'normal': 'orange', 'delayed': 'red'}
            )
            fig_prod.update_layout(yaxis_tickformat='.0%')
            st.plotly_chart(fig_prod, use_container_width=True)
            
            # Highlight underperforming resources
            underperforming = prod_df[prod_df['status'] == 'delayed']
            if not underperforming.empty:
                st.warning(t("resources_attention"))
                for _, resource in underperforming.iterrows():
                    st.write(
                        f"- **{resource['resource_name']}**: "
                        f"{resource['productivity_index']:.1%} productivity "
                        f"({resource['completed_tasks']}/{resource['assigned_tasks']} tasks completed)"
                    )
        else:
            st.info("No productivity metrics available.")
    
    with tab4:
        recommendations = comparison.get('recommendations', [])
        if recommendations:
            st.write(f"**{t('recommended_actions')}:**")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        else:
            st.success(t("no_actions_needed"))

# Show upload message only if no tasks are loaded
if 'tasks' not in st.session_state:
    st.info(t("upload_to_begin"))
