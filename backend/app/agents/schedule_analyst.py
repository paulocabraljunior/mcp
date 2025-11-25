from typing import List, Dict, Any
from app.models import Task
from datetime import datetime

class ScheduleAnalyst:
    def analyze(self, tasks: List[Task], language: str = "en") -> Dict[str, Any]:
        risks = []
        delayed_tasks = []
        
        now = datetime.now()
        
        translations = {
            "pt": {
                "overdue": "Tarefa '{}' está atrasada.",
                "summary": "Encontradas {} tarefas atrasadas."
            },
            "es": {
                "overdue": "La tarea '{}' está retrasada.",
                "summary": "Encontradas {} tareas retrasadas."
            },
            "en": {
                "overdue": "Task '{}' is overdue.",
                "summary": "Found {} delayed tasks."
            }
        }
        t = translations.get(language, translations["en"])

        for task in tasks:
            # Check for delayed tasks (past finish date and not complete)
            if task.finish_date and task.finish_date < now and task.percent_complete < 100:
                delayed_tasks.append({
                    "id": task.id,
                    "name": task.name,
                    "finish_date": task.finish_date,
                    "percent_complete": task.percent_complete,
                    "days_delayed": (now - task.finish_date).days
                })
                risks.append(t["overdue"].format(task.name))

        # Simple critical path estimation (longest duration tasks? or just list top 5 longest)
        # Real critical path requires dependency graph traversal.
        # For now, let's sort by duration.
        sorted_by_duration = sorted(tasks, key=lambda x: x.duration, reverse=True)
        top_long_tasks = sorted_by_duration[:5]

        summaries = {}
        for lang in ["pt", "es", "en"]:
            summary_tmpl = translations.get(lang)
            summaries[lang] = summary_tmpl["summary"].format(len(delayed_tasks))

        return {
            "agent": "Schedule Analyst",
            "summary": summaries,
            "risks": risks,
            "delayed_tasks": delayed_tasks,
            "longest_tasks": [t.name for t in top_long_tasks]
        }
