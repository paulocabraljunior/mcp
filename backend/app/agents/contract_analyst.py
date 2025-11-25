from typing import List, Dict, Any
from app.models import Task, ContractActivity, ProductivityMetric, ContractComparison
from datetime import datetime
import re
import pdfplumber
from docx import Document

class ContractAnalyst:
    """
    Agent responsible for analyzing contracts and comparing them with project schedules.
    Identifies delayed activities, missing tasks, and calculates productivity metrics.
    """
    
    def parse_contract_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """Extract structured data from PDF contract."""
        contract_data = {
            "activities": [],
            "raw_text": ""
        }
        
        try:
            import io
            pdf_file = io.BytesIO(pdf_content)
            
            with pdfplumber.open(pdf_file) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                contract_data["raw_text"] = full_text
                
                # Extract activities using pattern matching
                # Look for common patterns like:
                # - "Activity: <name>" or "Task: <name>"
                # - "Deadline: <date>" or "Due date: <date>"
                # - "Deliverable: <item>"
                
                activity_pattern = r'(?:Activity|Task|Item)\s*[:\-]\s*([^\n]+)'
                deadline_pattern = r'(?:Deadline|Due\s*date|Completion\s*date)\s*[:\-]\s*([^\n]+)'
                deliverable_pattern = r'(?:Deliverable|Output)\s*[:\-]\s*([^\n]+)'
                
                activities = re.findall(activity_pattern, full_text, re.IGNORECASE)
                deadlines = re.findall(deadline_pattern, full_text, re.IGNORECASE)
                deliverables = re.findall(deliverable_pattern, full_text, re.IGNORECASE)
                
                contract_data["activities"] = activities
                contract_data["deadlines"] = deadlines
                contract_data["deliverables"] = deliverables
                
        except Exception as e:
            contract_data["error"] = str(e)
        
        return contract_data
    
    def parse_contract_docx(self, docx_content: bytes) -> Dict[str, Any]:
        """Extract structured data from DOCX contract."""
        contract_data = {
            "activities": [],
            "raw_text": ""
        }
        
        try:
            import io
            docx_file = io.BytesIO(docx_content)
            doc = Document(docx_file)
            
            full_text = ""
            for paragraph in doc.paragraphs:
                full_text += paragraph.text + "\n"
            
            contract_data["raw_text"] = full_text
            
            # Same pattern matching as PDF
            activity_pattern = r'(?:Activity|Task|Item)\s*[:\-]\s*([^\n]+)'
            deadline_pattern = r'(?:Deadline|Due\s*date|Completion\s*date)\s*[:\-]\s*([^\n]+)'
            deliverable_pattern = r'(?:Deliverable|Output)\s*[:\-]\s*([^\n]+)'
            
            activities = re.findall(activity_pattern, full_text, re.IGNORECASE)
            deadlines = re.findall(deadline_pattern, full_text, re.IGNORECASE)
            deliverables = re.findall(deliverable_pattern, full_text, re.IGNORECASE)
            
            contract_data["activities"] = activities
            contract_data["deadlines"] = deadlines
            contract_data["deliverables"] = deliverables
            
        except Exception as e:
            contract_data["error"] = str(e)
        
        return contract_data
    
    def compare_with_schedule(self, contract_data: Dict, tasks: List[Task], language: str = "en") -> ContractComparison:
        """
        Compare contract activities with schedule tasks.
        Returns comprehensive comparison analysis.
        """
        now = datetime.now()
        
        # Localization dictionary
        translations = {
            "pt": {
                "add_missing": "Adicionar {} atividades faltantes ao cronograma para cumprir os requisitos do contrato.",
                "expedite_delayed": "Acelerar {} atividades atrasadas para cumprir os prazos.",
                "review_resources": "Revisar alocação de recursos para recursos com baixo desempenho.",
                "low_compliance": "Conformidade do cronograma está abaixo do limite aceitável. Ação imediata necessária.",
                "summary": "Analisadas {} tarefas do cronograma contra {} atividades do contrato. Encontradas {} tarefas atrasadas e {} atividades faltantes. Conformidade geral: {:.1f}%"
            },
            "es": {
                "add_missing": "Agregar {} actividades faltantes al cronograma para cumplir con los requisitos del contrato.",
                "expedite_delayed": "Acelerar {} actividades retrasadas para cumplir con los plazos.",
                "review_resources": "Revisar asignación de recursos para recursos con bajo rendimiento.",
                "low_compliance": "El cumplimiento del cronograma está por debajo del umbral aceptable. Se requiere acción inmediata.",
                "summary": "Analizadas {} tareas del cronograma contra {} actividades del contrato. Encontradas {} tareas retrasadas y {} actividades faltantes. Cumplimiento general: {:.1f}%"
            },
            "en": {
                "add_missing": "Add {} missing activities to the schedule to comply with contract requirements.",
                "expedite_delayed": "Expedite {} delayed activities to meet deadlines.",
                "review_resources": "Review resource allocation for underperforming resources.",
                "low_compliance": "Schedule compliance is below acceptable threshold. Immediate action required.",
                "summary": "Analyzed {} schedule tasks against {} contract activities. Found {} delayed tasks and {} missing activities. Overall compliance: {:.1f}%"
            }
        }
        
        t = translations.get(language, translations["en"])
        
        # Extract task names from schedule
        schedule_task_names = [task.name.lower() for task in tasks]
        contract_activities = [act.lower() for act in contract_data.get("activities", [])]
        
        # Find missing activities (in contract but not in schedule)
        missing_activities = []
        for contract_activity in contract_activities:
            # Use fuzzy matching - check if any schedule task contains the contract activity
            found = any(contract_activity in task_name or task_name in contract_activity 
                       for task_name in schedule_task_names)
            if not found:
                missing_activities.append(contract_activity)
        
        # Find extra activities (in schedule but not mentioned in contract)
        extra_activities = []
        for task in tasks:
            task_name_lower = task.name.lower()
            found = any(act in task_name_lower or task_name_lower in act 
                       for act in contract_activities)
            if not found and len(contract_activities) > 0:  # Only if we have contract data
                extra_activities.append(task.name)
        
        # Find delayed activities
        delayed_activities = []
        for task in tasks:
            if task.finish_date and task.finish_date < now and task.percent_complete < 100:
                days_delayed = (now - task.finish_date).days
                delayed_activities.append({
                    "name": task.name,
                    "finish_date": task.finish_date.isoformat(),
                    "percent_complete": task.percent_complete,
                    "days_delayed": days_delayed,
                    "resources": task.resource_names
                })
        
        # Calculate productivity metrics by resource
        productivity_metrics = self.calculate_productivity_metrics(tasks)
        
        # Calculate compliance score (0-100)
        total_metrics = len(contract_activities) + len(tasks)
        if total_metrics > 0:
            issues = len(missing_activities) + len(delayed_activities)
            compliance_score = max(0, 100 - (issues / total_metrics * 100))
        else:
            compliance_score = 100.0
        
        # Generate recommendations
        recommendations = []
        if missing_activities:
            recommendations.append(t["add_missing"].format(len(missing_activities)))
        if delayed_activities:
            recommendations.append(t["expedite_delayed"].format(len(delayed_activities)))
        if any(metric.productivity_index < 0.5 for metric in productivity_metrics):
            recommendations.append(t["review_resources"])
        if compliance_score < 80:
            recommendations.append(t["low_compliance"])
        
        summary = t["summary"].format(
            len(tasks), len(contract_activities), len(delayed_activities), len(missing_activities), compliance_score
        )
        
        return ContractComparison(
            summary=summary,
            delayed_activities=delayed_activities,
            missing_activities=missing_activities,
            extra_activities=extra_activities[:10],  # Limit to top 10
            productivity_metrics=productivity_metrics,
            compliance_score=compliance_score,
            recommendations=recommendations
        )
    
    def calculate_productivity_metrics(self, tasks: List[Task]) -> List[ProductivityMetric]:
        """Calculate productivity indices for each resource."""
        resource_stats = {}
        
        for task in tasks:
            for resource in task.resource_names:
                if resource not in resource_stats:
                    resource_stats[resource] = {
                        "assigned_tasks": 0,
                        "completed_tasks": 0,
                        "total_duration": 0.0,
                        "completed_duration": 0.0
                    }
                
                resource_stats[resource]["assigned_tasks"] += 1
                resource_stats[resource]["total_duration"] += task.duration
                
                if task.percent_complete == 100:
                    resource_stats[resource]["completed_tasks"] += 1
                    resource_stats[resource]["completed_duration"] += task.duration
                elif task.percent_complete > 0:
                    # Partial completion
                    resource_stats[resource]["completed_duration"] += task.duration * (task.percent_complete / 100)
        
        # Convert to ProductivityMetric objects
        metrics = []
        for resource_name, stats in resource_stats.items():
            # Productivity index: ratio of completed duration to total duration
            if stats["total_duration"] > 0:
                productivity_index = stats["completed_duration"] / stats["total_duration"]
            else:
                productivity_index = 0.0
            
            # Determine status
            if productivity_index >= 0.8:
                status = "efficient"
            elif productivity_index >= 0.5:
                status = "normal"
            else:
                status = "delayed"
            
            metrics.append(ProductivityMetric(
                resource_name=resource_name,
                assigned_tasks=stats["assigned_tasks"],
                completed_tasks=stats["completed_tasks"],
                total_duration=stats["total_duration"],
                completed_duration=stats["completed_duration"],
                productivity_index=productivity_index,
                status=status
            ))
        
        # Sort by productivity index (lowest first to highlight issues)
        metrics.sort(key=lambda m: m.productivity_index)
        
        return metrics
