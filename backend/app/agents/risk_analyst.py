from typing import List, Dict, Any
from app.models import Task
from datetime import datetime, timedelta

class RiskAnalyst:
    """
    Agent responsible for analyzing delay risks for project activities.
    Assigns risk levels from 1-5 where:
    - Level 1: Very Low Risk (on track, good progress)
    - Level 2: Low Risk (minor concerns)
    - Level 3: Medium Risk (needs monitoring)
    - Level 4: High Risk (likely to delay)
    - Level 5: Critical Risk (certain to delay)
    """
    
    def analyze(self, tasks: List[Task], resource_analysis: Dict[str, Any] = None, language: str = "en") -> Dict[str, Any]:
        """
        Analyze delay risk for each task and generate overall risk assessment.
        """
        now = datetime.now()
        risk_analysis = []
        
        for task in tasks:
            risk_level, risk_factors = self._calculate_risk_level(task, now, language)
            
            # Get descriptions for all languages
            descriptions = {}
            for lang in ["pt", "es", "en"]:
                descriptions[lang] = self._get_risk_description(risk_level, lang)

            risk_analysis.append({
                "task_id": task.id,
                "task_name": task.name,
                "risk_level": risk_level,
                "risk_description": descriptions, # Dict with all languages
                "risk_factors": risk_factors,
                "percent_complete": task.percent_complete,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "finish_date": task.finish_date.isoformat() if task.finish_date else None,
                "resources": task.resource_names
            })
        
        # Calculate risk distribution
        risk_distribution = {
            "level_1": sum(1 for r in risk_analysis if r["risk_level"] == 1),
            "level_2": sum(1 for r in risk_analysis if r["risk_level"] == 2),
            "level_3": sum(1 for r in risk_analysis if r["risk_level"] == 3),
            "level_4": sum(1 for r in risk_analysis if r["risk_level"] == 4),
            "level_5": sum(1 for r in risk_analysis if r["risk_level"] == 5)
        }
        
        # Get high-risk tasks (level 4 and 5)
        high_risk_tasks = [r for r in risk_analysis if r["risk_level"] >= 4]
        
        # Calculate overall project risk score (weighted average)
        total_tasks = len(risk_analysis)
        if total_tasks > 0:
            avg_risk = sum(r["risk_level"] for r in risk_analysis) / total_tasks
            project_risk_level = round(avg_risk)
        else:
            avg_risk = 0
            project_risk_level = 1
        
        # Generate summary
        critical_count = risk_distribution["level_5"]
        high_count = risk_distribution["level_4"]
        
        translations = {
            "pt": {
                "critical": "⚠️ CRÍTICO: {} atividades com atraso certo. Intervenção imediata necessária!",
                "high": "⚠️ ALTO RISCO: {} atividades com provável atraso. Monitoramento próximo necessário.",
                "medium": "⚡ RISCO MÉDIO: {} atividades precisam de monitoramento.",
                "low": "✅ BAIXO RISCO: Projeto no prazo com risco mínimo de atraso."
            },
            "es": {
                "critical": "⚠️ CRÍTICO: {} actividades con retraso seguro. ¡Se requiere intervención inmediata!",
                "high": "⚠️ ALTO RIESGO: {} actividades con probable retraso. Se necesita monitoreo cercano.",
                "medium": "⚡ RIESGO MEDIO: {} actividades necesitan monitoreo.",
                "low": "✅ BAJO RIESGO: Proyecto a tiempo con riesgo mínimo de retraso."
            },
            "en": {
                "critical": "⚠️ CRITICAL: {} activities certain to delay. Immediate intervention required!",
                "high": "⚠️ HIGH RISK: {} activities likely to delay. Close monitoring needed.",
                "medium": "⚡ MEDIUM RISK: {} activities need monitoring.",
                "low": "✅ LOW RISK: Project is on track with minimal delay risk."
            }
        }
        t = translations.get(language, translations["en"])
        
        # Generate summaries for all languages
        summaries = {}
        for lang in ["pt", "es", "en"]:
            t = translations.get(lang)
            if critical_count > 0:
                summaries[lang] = t["critical"].format(critical_count)
            elif high_count > 0:
                summaries[lang] = t["high"].format(high_count)
            elif risk_distribution["level_3"] > 0:
                summaries[lang] = t["medium"].format(risk_distribution["level_3"])
            else:
                summaries[lang] = t["low"]

        return {
            "agent": "Risk Analyst",
            "summary": summaries, # Returns dict with all languages
            "project_risk_level": project_risk_level,
            "average_risk_score": round(avg_risk, 2),
            "risk_distribution": risk_distribution,
            "tasks_by_risk": sorted(risk_analysis, key=lambda x: x["risk_level"], reverse=True),
            "high_risk_tasks": high_risk_tasks,
            "total_tasks_analyzed": total_tasks
        }
    
    def _calculate_risk_level(self, task: Task, now: datetime, language: str = "en") -> tuple[int, List[str]]:
        """
        Calculate risk level (1-5) for a single task.
        Returns: (risk_level, list_of_risk_factors)
        """
        risk_score = 0
        risk_factors = []
        
        translations = {
            "pt": {
                "overdue": "Já atrasado {} dias",
                "recent_overdue": "Atrasado recentemente ({} dias)",
                "behind_schedule": "Progresso do trabalho ({}%) significativamente atrás do tempo ({}%)",
                "lagging": "Progresso do trabalho atrasado em relação ao cronograma",
                "long_duration": "Tarefa de longa duração ({} dias)",
                "no_resources": "Sem recursos atribuídos",
                "should_start": "Deveria ter iniciado há {} dias",
                "start_passed": "Data de início passou sem progresso",
                "approaching_deadline": "Apenas {} dias restantes com {}% concluído",
                "approaching_low": "Aproximando-se do prazo com baixa taxa de conclusão",
                "completed": "Tarefa concluída",
                "ample_time": "Tempo restante amplo",
                "good_progress": "Bom progresso mantido"
            },
            "es": {
                "overdue": "Ya retrasado {} días",
                "recent_overdue": "Retrasado recientemente ({} días)",
                "behind_schedule": "Progreso del trabajo ({}%) significativamente detrás del tiempo ({}%)",
                "lagging": "Progreso del trabajo rezagado respecto al cronograma",
                "long_duration": "Tarea de larga duración ({} días)",
                "no_resources": "Sin recursos asignados",
                "should_start": "Debería haber comenzado hace {} días",
                "start_passed": "La fecha de inicio pasó sin progreso",
                "approaching_deadline": "Solo quedan {} días con {}% completado",
                "approaching_low": "Acercándose a la fecha límite con baja tasa de finalización",
                "completed": "Tarea completada",
                "ample_time": "Tiempo restante amplio",
                "good_progress": "Buen progreso mantenido"
            },
            "en": {
                "overdue": "Already {} days overdue",
                "recent_overdue": "Recently became overdue ({} days)",
                "behind_schedule": "Work progress ({}%) significantly behind time progress ({}%)",
                "lagging": "Work progress lagging behind schedule",
                "long_duration": "Long duration task ({} days)",
                "no_resources": "No resources assigned",
                "should_start": "Should have started {} days ago",
                "start_passed": "Start date passed without progress",
                "approaching_deadline": "Only {} days left with {}% complete",
                "approaching_low": "Approaching deadline with low completion rate",
                "completed": "Task completed",
                "ample_time": "Ample time remaining",
                "good_progress": "Good progress maintained"
            }
        }
        t = translations.get(language, translations["en"])
        
        # Factor 1: Already delayed?
        if task.finish_date and task.finish_date < now and task.percent_complete < 100:
            days_delayed = (now - task.finish_date).days
            if days_delayed > 30:
                risk_score += 3
                risk_factors.append(t["overdue"].format(days_delayed))
            elif days_delayed > 7:
                risk_score += 2
                risk_factors.append(t["overdue"].format(days_delayed))
            else:
                risk_score += 1
                risk_factors.append(t["recent_overdue"].format(days_delayed))
        
        # Factor 2: Progress vs Time Elapsed
        if task.start_date and task.finish_date and task.start_date <= now:
            total_duration = (task.finish_date - task.start_date).total_seconds()
            elapsed_duration = (now - task.start_date).total_seconds()
            
            if total_duration > 0:
                time_progress_ratio = min(elapsed_duration / total_duration, 1.0)
                work_progress_ratio = task.percent_complete / 100.0
                
                # If time progress > work progress, we're falling behind
                if time_progress_ratio > 0.1:  # Only check if some time has passed
                    progress_gap = time_progress_ratio - work_progress_ratio
                    
                    if progress_gap > 0.4:  # More than 40% behind schedule
                        risk_score += 2
                        risk_factors.append(t["behind_schedule"].format(task.percent_complete, int(time_progress_ratio*100)))
                    elif progress_gap > 0.2:  # More than 20% behind
                        risk_score += 1
                        risk_factors.append(t["lagging"])
        
        # Factor 3: Task duration (longer tasks = higher risk)
        if task.duration > 60:  # More than 60 days
            risk_score += 1
            risk_factors.append(t["long_duration"].format(int(task.duration)))
        
        # Factor 4: No resources assigned
        if not task.resource_names or len(task.resource_names) == 0:
            risk_score += 1
            risk_factors.append(t["no_resources"])
        
        # Factor 5: Not started but should have started
        if task.start_date and task.start_date < now and task.percent_complete == 0:
            days_behind_start = (now - task.start_date).days
            if days_behind_start > 7:
                risk_score += 2
                risk_factors.append(t["should_start"].format(days_behind_start))
            else:
                risk_score += 1
                risk_factors.append(t["start_passed"])
        
        # Factor 6: Approaching deadline with low completion
        if task.finish_date and task.finish_date > now:
            days_remaining = (task.finish_date - now).days
            if days_remaining <= 7 and task.percent_complete < 80:
                risk_score += 2
                risk_factors.append(t["approaching_deadline"].format(days_remaining, task.percent_complete))
            elif days_remaining <= 14 and task.percent_complete < 50:
                risk_score += 1
                risk_factors.append(t["approaching_low"])
        
        # Convert risk_score to 1-5 level
        if risk_score >= 6:
            risk_level = 5  # Critical - certain to delay
        elif risk_score >= 4:
            risk_level = 4  # High - likely to delay
        elif risk_score >= 2:
            risk_level = 3  # Medium - needs monitoring
        elif risk_score >= 1:
            risk_level = 2  # Low - minor concerns
        else:
            risk_level = 1  # Very low - on track
        
        # Override: If task is completed, risk is always 1
        if task.percent_complete >= 100:
            risk_level = 1
            risk_factors = [t["completed"]]
        
        # Add positive factors for low risk
        if risk_level <= 2 and task.percent_complete > 0:
            if task.finish_date and task.finish_date > now:
                days_remaining = (task.finish_date - now).days
                if days_remaining > 30:
                    risk_factors.append(t["ample_time"])
            if task.percent_complete >= 50:
                risk_factors.append(t["good_progress"])
        
        return risk_level, risk_factors
    
    def _get_risk_description(self, risk_level: int, language: str = "en") -> str:
        """Get human-readable risk description."""
        translations = {
            "pt": {
                1: "Risco Muito Baixo - No Prazo",
                2: "Risco Baixo - Preocupações Menores",
                3: "Risco Médio - Precisa Monitoramento",
                4: "Risco Alto - Provável Atraso",
                5: "Risco Crítico - Atraso Certo"
            },
            "es": {
                1: "Riesgo Muy Bajo - A Tiempo",
                2: "Riesgo Bajo - Preocupaciones Menores",
                3: "Riesgo Medio - Necesita Monitoreo",
                4: "Riesgo Alto - Probable Retraso",
                5: "Riesgo Crítico - Retraso Seguro"
            },
            "en": {
                1: "Very Low Risk - On Track",
                2: "Low Risk - Minor Concerns",
                3: "Medium Risk - Needs Monitoring",
                4: "High Risk - Likely to Delay",
                5: "Critical Risk - Certain to Delay"
            }
        }
        t = translations.get(language, translations["en"])
        return t.get(risk_level, "Unknown Risk")
