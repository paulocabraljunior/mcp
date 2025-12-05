import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

class XMLScheduleReader:
    @staticmethod
    def parse_xml(file_obj) -> pd.DataFrame:
        """
        Parses MS Project XML file and returns a pandas DataFrame with tasks.
        """
        try:
            content = file_obj.read()
            # If bytes, decode
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            root = ET.fromstring(content)

            # Namespace handling
            ns = ''
            if root.tag.startswith('{'):
                ns = root.tag.split('}')[0] + '}'

            # 1. Parse Resources
            resources = {} # UID -> Name
            res_wrapper = root.find(f"{ns}Resources")
            if res_wrapper is not None:
                for r in res_wrapper.findall(f"{ns}Resource"):
                    uid = r.find(f"{ns}UID")
                    name = r.find(f"{ns}Name")
                    if uid is not None and name is not None and name.text:
                        resources[uid.text] = name.text

            # 2. Parse Assignments
            task_resources = {} # TaskUID -> List[ResourceName]
            assign_wrapper = root.find(f"{ns}Assignments")
            if assign_wrapper is not None:
                for a in assign_wrapper.findall(f"{ns}Assignment"):
                    task_uid = a.find(f"{ns}TaskUID")
                    res_uid = a.find(f"{ns}ResourceUID")
                    if task_uid is not None and res_uid is not None:
                        r_name = resources.get(res_uid.text)
                        if r_name:
                            if task_uid.text not in task_resources:
                                task_resources[task_uid.text] = []
                            task_resources[task_uid.text].append(r_name)

            # 3. Parse Tasks
            tasks_data = []
            tasks_wrapper = root.find(f"{ns}Tasks")

            if tasks_wrapper is None:
                # Try finding all tasks if wrapper not found (flat structure or different schema)
                all_tasks_iter = root.findall(f".//{ns}Task")
            else:
                all_tasks_iter = tasks_wrapper.findall(f"{ns}Task")

            for t in all_tasks_iter:
                uid = t.find(f"{ns}UID")
                name = t.find(f"{ns}Name")
                if uid is None or name is None:
                    continue

                # Skip summary tasks if needed, or keep them.
                # Usually we want all tasks.

                start = t.find(f"{ns}Start")
                finish = t.find(f"{ns}Finish")
                duration_elem = t.find(f"{ns}Duration")
                pct = t.find(f"{ns}PercentComplete")

                start_date = None
                if start is not None and start.text:
                    try: start_date = datetime.fromisoformat(start.text)
                    except: pass

                finish_date = None
                if finish is not None and finish.text:
                    try: finish_date = datetime.fromisoformat(finish.text)
                    except: pass

                # Duration Parsing (PT8H0M0S)
                duration_days = 0.0
                if duration_elem is not None and duration_elem.text:
                    d_str = duration_elem.text
                    if d_str.startswith("PT"):
                        try:
                            val = d_str[2:]
                            hours = 0.0
                            if 'H' in val:
                                parts = val.split('H')
                                hours += float(parts[0])
                                val = parts[1] if len(parts) > 1 else ""
                            if 'M' in val:
                                parts = val.split('M')
                                hours += float(parts[0]) / 60.0

                            # Standard 8h day
                            duration_days = hours / 8.0
                        except: pass

                percent_complete = 0
                if pct is not None and pct.text:
                    percent_complete = int(pct.text)

                # Get Predecessors
                preds = []
                for link in t.findall(f"{ns}PredecessorLink"):
                    p_uid = link.find(f"{ns}PredecessorUID")
                    if p_uid is not None:
                        preds.append(p_uid.text)

                tasks_data.append({
                    "UID": uid.text,
                    "Name": name.text,
                    "Start": start_date,
                    "Finish": finish_date,
                    "Duration": duration_days,
                    "PercentComplete": percent_complete,
                    "Resources": task_resources.get(uid.text, []),
                    "Predecessors": preds
                })

            return pd.DataFrame(tasks_data)

        except Exception as e:
            print(f"Error parsing XML: {e}")
            return pd.DataFrame()
