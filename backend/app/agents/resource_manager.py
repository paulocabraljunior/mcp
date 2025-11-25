from typing import List, Dict, Any
from app.models import Task

class ResourceManager:
    def analyze(self, tasks: List[Task], language: str = "en") -> Dict[str, Any]:
        resource_counts = {}
        resource_hours = {}
        
        for task in tasks:
            for res in task.resource_names:
                # Count tasks per resource
                resource_counts[res] = resource_counts.get(res, 0) + 1
                
                # Estimate hours (Duration is in hours)
                # If multiple resources, split duration? Or assume full effort?
                # MS Project is complex, but let's assume full duration for now per resource assignment
                resource_hours[res] = resource_hours.get(res, 0.0) + task.duration

        # Identify over-allocation (simple heuristic: > 5 tasks or > 40 hours?)
        # This is just a demo heuristic.
        overloaded = [r for r, count in resource_counts.items() if count > 5]
        
        translations = {
            "pt": "Analisados {} recursos.",
            "es": "Analizados {} recursos.",
            "en": "Analyzed {} resources."
        }
        summaries = {}
        for lang in ["pt", "es", "en"]:
            summary_tmpl = translations.get(lang)
            summaries[lang] = summary_tmpl.format(len(resource_counts))

        return {
            "agent": "Resource Manager",
            "summary": summaries,
            "utilization": resource_counts,
            "total_hours": resource_hours,
            "overloaded_resources": overloaded
        }
