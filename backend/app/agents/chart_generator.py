from typing import List, Dict, Any
from app.models import Task
import pandas as pd

class ChartGenerator:
    def generate_charts(self, tasks: List[Task], resource_analysis: Dict[str, Any], risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        # Convert to simple list of dicts for frontend consumption
        # Streamlit can handle lists of dicts or pandas DataFrames directly, 
        # but this agent can pre-calculate some aggregations.
        
        task_data = [t.dict() for t in tasks]
        df = pd.DataFrame(task_data)
        
        # 1. Cumulative Progress
        # Simple average progress? Or weighted by duration?
        # Let's do weighted progress
        total_duration = df['duration'].sum()
        if total_duration > 0:
            weighted_progress = (df['percent_complete'] * df['duration']).sum() / total_duration
        else:
            weighted_progress = 0

        # 2. Tasks per Resource
        # Flatten resource list
        all_resources = []
        for t in tasks:
            all_resources.extend(t.resource_names)
        
        res_counts = pd.Series(all_resources).value_counts().to_dict()

        return {
            "agent": "Chart Generator",
            "summary": "Prepared visualization data.",
            "weighted_progress": weighted_progress,
            "resource_distribution": res_counts
        }
