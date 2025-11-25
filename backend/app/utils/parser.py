import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any
from app.models import Task

class MSProjectParser:
    def __init__(self, xml_content: str):
        self.root = ET.fromstring(xml_content)
        # Handle namespaces if necessary, for now assuming simple XML or stripping NS
        self.ns = self._get_namespace(self.root)

    def _get_namespace(self, element):
        if element.tag.startswith('{'):
            return element.tag.split('}')[0] + '}'
        return ''

    def parse_tasks(self) -> List[Task]:
        # 1. Parse Resources
        resources = {} # UID -> Name
        res_wrapper = self.root.find(f"{self.ns}Resources") if self.ns else self.root.find("Resources")
        if res_wrapper:
            for r in res_wrapper.findall(f"{self.ns}Resource"):
                uid = r.find(f"{self.ns}UID")
                name = r.find(f"{self.ns}Name")
                if uid is not None and name is not None:
                    resources[uid.text] = name.text

        # 2. Parse Assignments
        task_resources = {} # TaskUID -> List[ResourceName]
        assign_wrapper = self.root.find(f"{self.ns}Assignments") if self.ns else self.root.find("Assignments")
        if assign_wrapper:
            for a in assign_wrapper.findall(f"{self.ns}Assignment"):
                task_uid = a.find(f"{self.ns}TaskUID")
                res_uid = a.find(f"{self.ns}ResourceUID")
                if task_uid is not None and res_uid is not None:
                    r_name = resources.get(res_uid.text)
                    if r_name:
                        if task_uid.text not in task_resources:
                            task_resources[task_uid.text] = []
                        task_resources[task_uid.text].append(r_name)

        # 3. Parse Tasks
        tasks = []
        task_tag = f"{self.ns}Task" if self.ns else "Task"
        tasks_wrapper_tag = f"{self.ns}Tasks" if self.ns else "Tasks"
        
        tasks_wrapper = self.root.find(tasks_wrapper_tag)
        if tasks_wrapper is None:
            all_tasks = self.root.findall(f".//{task_tag}")
        else:
            all_tasks = tasks_wrapper.findall(task_tag)

        for t in all_tasks:
            uid = t.find(f"{self.ns}UID")
            name = t.find(f"{self.ns}Name")
            start = t.find(f"{self.ns}Start")
            finish = t.find(f"{self.ns}Finish")
            duration_str = t.find(f"{self.ns}Duration")
            percent_complete = t.find(f"{self.ns}PercentComplete")
            
            if uid is None or name is None:
                continue

            start_date = self._parse_date(start.text) if start is not None and start.text else None
            finish_date = self._parse_date(finish.text) if finish is not None and finish.text else None
            duration = self._parse_duration(duration_str.text) if duration_str is not None and duration_str.text else 0.0
            
            # Get resources for this task
            t_res = task_resources.get(uid.text, [])

            # Get predecessors
            predecessors = []
            pred_link_tag = f"{self.ns}PredecessorLink" if self.ns else "PredecessorLink"
            for link in t.findall(pred_link_tag):
                pred_uid = link.find(f"{self.ns}PredecessorUID")
                if pred_uid is not None:
                    predecessors.append(pred_uid.text)

            tasks.append(Task(
                id=uid.text,
                name=name.text,
                start_date=start_date,
                finish_date=finish_date,
                duration=duration,
                percent_complete=int(percent_complete.text) if percent_complete is not None and percent_complete.text else 0,
                resource_names=t_res,
                predecessors=predecessors
            ))
        
        return tasks

    def _parse_date(self, date_str: str) -> datetime:
        try:
            # MS Project XML dates are usually ISO 8601
            return datetime.fromisoformat(date_str)
        except ValueError:
            return None

    def _parse_duration(self, duration_str: str) -> float:
        # Format PT8H0M0S
        # Very basic parsing, assuming hours
        if not duration_str.startswith("PT"):
            return 0.0
        
        try:
            # Remove PT
            val = duration_str[2:]
            hours = 0.0
            if 'H' in val:
                parts = val.split('H')
                hours += float(parts[0])
                val = parts[1]
            if 'M' in val:
                parts = val.split('M')
                hours += float(parts[0]) / 60.0
            return hours
        except:
            return 0.0
