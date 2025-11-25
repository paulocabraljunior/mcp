from typing import List, Dict, Any
from app.models import Task
from datetime import datetime

class TextReportGenerator:
    """
    Agent responsible for generating comprehensive text-based status reports
    of the project schedule in natural language.
    """
    
    def generate_report(self, tasks: List[Task], analysis: Dict[str, Any], language: str = "pt") -> str:
        """
        Generate a comprehensive text report of the schedule status.
        
        Args:
            tasks: List of project tasks
            analysis: Analysis data from other agents (schedule, resource, risk)
            language: Report language (pt, es, en)
        
        Returns:
            Formatted text report
        """
        now = datetime.now()
        
        # Extract data from analysis
        schedule_analysis = analysis.get('schedule_analysis', {})
        resource_analysis = analysis.get('resource_analysis', {})
        risk_analysis = analysis.get('risk_analysis', {})
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.percent_complete == 100)
        in_progress_tasks = sum(1 for t in tasks if 0 < t.percent_complete < 100)
        not_started_tasks = sum(1 for t in tasks if t.percent_complete == 0)
        
        avg_completion = sum(t.percent_complete for t in tasks) / total_tasks if total_tasks > 0 else 0
        
        delayed_tasks = schedule_analysis.get('delayed_tasks', [])
        risks = schedule_analysis.get('risks', [])
        
        project_risk_level = risk_analysis.get('project_risk_level', 1)
        high_risk_tasks = risk_analysis.get('high_risk_tasks', [])
        
        # Generate report based on language
        if language == "pt":
            return self._generate_pt_report(
                total_tasks, completed_tasks, in_progress_tasks, not_started_tasks,
                avg_completion, delayed_tasks, risks, project_risk_level, high_risk_tasks,
                resource_analysis
            )
        elif language == "es":
            return self._generate_es_report(
                total_tasks, completed_tasks, in_progress_tasks, not_started_tasks,
                avg_completion, delayed_tasks, risks, project_risk_level, high_risk_tasks,
                resource_analysis
            )
        else:  # en
            return self._generate_en_report(
                total_tasks, completed_tasks, in_progress_tasks, not_started_tasks,
                avg_completion, delayed_tasks, risks, project_risk_level, high_risk_tasks,
                resource_analysis
            )
    
    def _generate_pt_report(self, total, completed, in_progress, not_started, avg_completion,
                           delayed, risks, risk_level, high_risk, resources):
        """Generate Portuguese report"""
        report = f"""
# 📊 RELATÓRIO DE STATUS DO CRONOGRAMA

**Data do Relatório:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}

---

## 📈 RESUMO EXECUTIVO

O projeto possui **{total} tarefas** no total, com um progresso médio de **{avg_completion:.1f}%**.

### Distribuição das Tarefas:
- ✅ **Concluídas:** {completed} tarefas ({completed/total*100:.1f}%)
- 🔄 **Em Andamento:** {in_progress} tarefas ({in_progress/total*100:.1f}%)
- ⏸️ **Não Iniciadas:** {not_started} tarefas ({not_started/total*100:.1f}%)

---

## ⚠️ ANÁLISE DE RISCOS

**Nível de Risco do Projeto:** Nível {risk_level}/5

"""
        if risk_level >= 4:
            report += "🔴 **ATENÇÃO CRÍTICA:** O projeto apresenta alto risco de atrasos!\n\n"
        elif risk_level >= 3:
            report += "🟡 **ATENÇÃO:** O projeto requer monitoramento próximo.\n\n"
        else:
            report += "🟢 **SITUAÇÃO FAVORÁVEL:** O projeto está sob controle.\n\n"
        
        if high_risk:
            report += f"### Tarefas de Alto Risco ({len(high_risk)}):\n"
            for task in high_risk:
                report += f"- **{task['task_name']}** (Risco Nível {task['risk_level']}/5) - {task['percent_complete']}% concluído\n"
            report += "\n"
        
        if delayed:
            report += f"## 🚨 TAREFAS ATRASADAS ({len(delayed)})\n\n"
            for task in delayed:
                report += f"- **{task['name']}**: {task['days_delayed']} dias de atraso ({task['percent_complete']}% concluído)\n"
            report += "\n"
        
        if risks:
            report += "## ⚠️ RISCOS IDENTIFICADOS\n\n"
            for risk in risks:
                report += f"- {risk}\n"
            report += "\n"
        
        # Resource analysis
        utilization = resources.get('utilization', {})
        if utilization:
            report += "## 👥 ANÁLISE DE RECURSOS\n\n"
            report += f"**Total de Recursos:** {len(utilization)}\n\n"
            
            overloaded = resources.get('overloaded_resources', [])
            if overloaded:
                report += f"**Recursos Sobrecarregados:** {', '.join(overloaded)}\n\n"
        
        # Recommendations
        report += "## 💡 RECOMENDAÇÕES\n\n"
        
        if risk_level >= 4:
            report += "1. **URGENTE:** Revisar cronograma e realocar recursos para tarefas críticas\n"
            report += "2. Realizar reunião de emergência com stakeholders\n"
            report += "3. Considerar horas extras ou recursos adicionais\n"
        elif risk_level >= 3:
            report += "1. Monitorar diariamente as tarefas de alto risco\n"
            report += "2. Antecipar possíveis gargalos e preparar planos de contingência\n"
            report += "3. Aumentar frequência de comunicação com a equipe\n"
        else:
            report += "1. Manter o ritmo atual de trabalho\n"
            report += "2. Continuar monitoramento semanal\n"
            report += "3. Preparar para próximas fases do projeto\n"
        
        if delayed:
            report += f"4. Priorizar a conclusão das {len(delayed)} tarefas atrasadas\n"
        
        report += "\n---\n\n"
        report += "*Relatório gerado automaticamente pelo Planus - Project Manager AI*\n"
        
        return report
    
    def _generate_es_report(self, total, completed, in_progress, not_started, avg_completion,
                           delayed, risks, risk_level, high_risk, resources):
        """Generate Spanish report"""
        report = f"""
# 📊 INFORME DE ESTADO DEL CRONOGRAMA

**Fecha del Informe:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}

---

## 📈 RESUMEN EJECUTIVO

El proyecto tiene **{total} tareas** en total, con un progreso promedio de **{avg_completion:.1f}%**.

### Distribución de Tareas:
- ✅ **Completadas:** {completed} tareas ({completed/total*100:.1f}%)
- 🔄 **En Progreso:** {in_progress} tareas ({in_progress/total*100:.1f}%)
- ⏸️ **No Iniciadas:** {not_started} tareas ({not_started/total*100:.1f}%)

---

## ⚠️ ANÁLISIS DE RIESGOS

**Nivel de Riesgo del Proyecto:** Nivel {risk_level}/5

"""
        if risk_level >= 4:
            report += "🔴 **ATENCIÓN CRÍTICA:** ¡El proyecto presenta alto riesgo de retrasos!\n\n"
        elif risk_level >= 3:
            report += "🟡 **ATENCIÓN:** El proyecto requiere monitoreo cercano.\n\n"
        else:
            report += "🟢 **SITUACIÓN FAVORABLE:** El proyecto está bajo control.\n\n"
        
        if high_risk:
            report += f"### Tareas de Alto Riesgo ({len(high_risk)}):\n"
            for task in high_risk:
                report += f"- **{task['task_name']}** (Riesgo Nivel {task['risk_level']}/5) - {task['percent_complete']}% completado\n"
            report += "\n"
        
        if delayed:
            report += f"## 🚨 TAREAS RETRASADAS ({len(delayed)})\n\n"
            for task in delayed:
                report += f"- **{task['name']}**: {task['days_delayed']} días de retraso ({task['percent_complete']}% completado)\n"
            report += "\n"
        
        report += "\n---\n\n"
        report += "*Informe generado automáticamente por Planus - Project Manager AI*\n"
        
        return report
    
    def _generate_en_report(self, total, completed, in_progress, not_started, avg_completion,
                           delayed, risks, risk_level, high_risk, resources):
        """Generate English report"""
        report = f"""
# 📊 SCHEDULE STATUS REPORT

**Report Date:** {datetime.now().strftime('%m/%d/%Y at %H:%M')}

---

## 📈 EXECUTIVE SUMMARY

The project has **{total} tasks** in total, with an average progress of **{avg_completion:.1f}%**.

### Task Distribution:
- ✅ **Completed:** {completed} tasks ({completed/total*100:.1f}%)
- 🔄 **In Progress:** {in_progress} tasks ({in_progress/total*100:.1f}%)
- ⏸️ **Not Started:** {not_started} tasks ({not_started/total*100:.1f}%)

---

## ⚠️ RISK ANALYSIS

**Project Risk Level:** Level {risk_level}/5

"""
        if risk_level >= 4:
            report += "🔴 **CRITICAL ATTENTION:** Project presents high risk of delays!\n\n"
        elif risk_level >= 3:
            report += "🟡 **ATTENTION:** Project requires close monitoring.\n\n"
        else:
            report += "🟢 **FAVORABLE SITUATION:** Project is under control.\n\n"
        
        if high_risk:
            report += f"### High Risk Tasks ({len(high_risk)}):\n"
            for task in high_risk:
                report += f"- **{task['task_name']}** (Risk Level {task['risk_level']}/5) - {task['percent_complete']}% complete\n"
            report += "\n"
        
        if delayed:
            report += f"## 🚨 DELAYED TASKS ({len(delayed)})\n\n"
            for task in delayed:
                report += f"- **{task['name']}**: {task['days_delayed']} days delayed ({task['percent_complete']}% complete)\n"
            report += "\n"
        
        report += "\n---\n\n"
        report += "*Report automatically generated by Planus - Project Manager AI*\n"
        
        return report
