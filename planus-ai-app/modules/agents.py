import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from datetime import datetime, timedelta
import json
import base64

class EngineeringAgent:
    def calculate_critical_path(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates or estimates the critical path.
        Since we might not have full dependency graph logic easily,
        we filter for tasks with 0 float if available, or just Longest Path.

        For this implementation, let's assume 'Critical' if no float info
        is simple estimation (e.g. 0 slack).
        But XML often doesn't have Slack/Float computed.

        We will return tasks that are likely critical based on longest path
        or simply return the input for now if complex logic isn't possible
        without a full graph library.

        However, a simple heuristic: Sort by Finish Date desc?
        Or just return all tasks if we can't determine.

        Let's try to filter by "Critical" column if it existed, but it doesn't.
        We will return the dataframe sorted by Duration descending as a placeholder
        for "Critical Path" focus, or filter tasks with no slack if we could calculate it.

        Better: Return tasks that determine the project finish date.
        """
        if df.empty:
            return df

        # Simplified: Filter tasks with > 0 duration
        # And maybe sort by Finish date?
        # Ideally we'd build a graph.

        # For this demo, let's return the top 20% longest tasks or tasks ending last.
        # Let's return tasks that end within the last 10% of the project timeline.

        try:
            max_finish = df['Finish'].max()
            min_start = df['Start'].min()
            total_duration = (max_finish - min_start).days

            # Tasks ending in the last 20% of the timeline
            threshold = max_finish - timedelta(days=total_duration * 0.2)
            cp = df[df['Finish'] >= threshold].copy()
            return cp.sort_values('Finish', ascending=False)
        except:
            return df

    def calculate_gantt_chart(self, df: pd.DataFrame):
        if df.empty: return None

        # Clean data for Gantt
        gantt_df = df.dropna(subset=['Start', 'Finish']).copy()
        if gantt_df.empty: return None

        fig = px.timeline(
            gantt_df,
            x_start="Start",
            x_end="Finish",
            y="Name",
            color="PercentComplete",
            title="Gantt Chart",
            labels={"Name": "Task", "Start": "Start Date", "Finish": "End Date"}
        )
        fig.update_yaxes(autorange="reversed")
        return fig

    def calculate_s_curve(self, df: pd.DataFrame, language="pt"):
        if df.empty: return None

        # Simple S-Curve based on accumulated cost or count or duration over time.
        # We will use accumulated "planned value" (Duration) vs "Actual" (Duration * %Complete)

        try:
            df = df.dropna(subset=['Start', 'Finish', 'Duration']).copy()
            if df.empty: return None

            # Generate a timeline
            min_date = df['Start'].min()
            max_date = df['Finish'].max()

            dates = pd.date_range(start=min_date, end=max_date, freq='W')

            planned_cumulative = []
            actual_cumulative = []

            total_duration = df['Duration'].sum()

            for d in dates:
                # Planned: Tasks that should be finished by date d
                # Simple weight: Duration

                # Pro-rata for tasks in progress? Simplified:
                # Value = Duration * fraction of time passed for that task relative to its start/finish

                # Planned %
                planned_val = 0
                actual_val = 0

                for _, task in df.iterrows():
                    # Planned
                    if task['Finish'] <= d:
                        planned_val += task['Duration']
                    elif task['Start'] < d < task['Finish']:
                        total_days = (task['Finish'] - task['Start']).days
                        if total_days > 0:
                            days_passed = (d - task['Start']).days
                            planned_val += task['Duration'] * (days_passed / total_days)

                    # Actual (Simplified: assumes actual follows planned timeline but scaled by %Complete)
                    # Real S-curve needs "Actual Start/Finish", but we assume XML has current status.
                    pct = task['PercentComplete'] / 100.0
                    if task['Start'] <= d:
                         # This is tricky without Actual Start.
                         # We'll just use the PercentComplete as a proxy for value earned IF the task has started in the plan.
                         if task['Finish'] <= d:
                             actual_val += task['Duration'] * pct
                         elif task['Start'] < d < task['Finish']:
                             # E.g. if we are 50% through time, and 50% complete, we earn 50% of value.
                             # If we are 50% through time, and 20% complete, we earn 20%.
                             # But we need to know WHEN the % completion happened. S-curve is usually "Total Progress over Time".
                             # Current snapshot only gives ONE % complete point.
                             # So we can't draw the PAST actual curve accurately without history.
                             # We can only draw the PLANNED curve and ONE point for current status?
                             # Or we assume "Actual" means "Earned Value" at this date?
                             pass

                planned_cumulative.append(planned_val / total_duration if total_duration else 0)
                # Actual cumulative is hard to reconstruct history for.
                # Let's do a simple "Planned Progress" curve (S-Curve) only.

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=[p*100 for p in planned_cumulative], mode='lines', name='Planned Progress'))

            fig.update_layout(title="S-Curve (Planned)", xaxis_title="Date", yaxis_title="Cumulative Progress (%)")
            return fig

        except Exception as e:
            print(f"Error S-Curve: {e}")
            return None


class RiskAgent:
    def __init__(self):
        self.api_key = None
        self.model_name = "gemini-1.5-flash"
        self.model = None

    def set_api_key(self, key):
        self.api_key = key
        genai.configure(api_key=key)

    def set_model(self, name):
        self.model_name = name
        self.model = genai.GenerativeModel(name)

    def generate_content(self, prompt):
        if not self.model:
            self.model = genai.GenerativeModel(self.model_name)
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_risks(self, contract_text, tasks_df, language="pt"):
        if not self.api_key or tasks_df.empty:
            return []

        # Prepare context
        tasks_summary = tasks_df[['Name', 'Start', 'Finish', 'Duration', 'PercentComplete']].head(20).to_string() # Limit to top 20 for context window efficiency or prioritize critical path

        prompt = f"""
        Analyze the following Project Schedule (Critical Tasks) and Contract snippet (if any) to identify risks.

        Language: {language}

        Contract Snippet:
        {contract_text[:2000] if contract_text else "No contract provided."}

        Schedule Tasks (Sample):
        {tasks_summary}

        Please generate a JSON list of risks. Each risk should have:
        - title
        - description
        - probability (High, Medium, Low, None)
        - mitigation

        Return ONLY valid JSON.
        """

        try:
            response = self.generate_content(prompt)
            # Cleanup JSON
            txt = response
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0]
            elif "```" in txt:
                txt = txt.split("```")[1].split("```")[0]

            return json.loads(txt)
        except Exception as e:
            return [{"title": "Error", "description": str(e), "probability": "High", "mitigation": "Check API"}]


class ReportAgent:
    def __init__(self):
        self.api_key = None
        self.model_name = "gemini-1.5-flash"

    def set_api_key(self, key):
        self.api_key = key
        genai.configure(api_key=key)

    def set_model(self, name):
        self.model_name = name

    def generate_executive_summary(self, risk_json, other_data, language="pt"):
        if not self.api_key: return "API Key missing."

        model = genai.GenerativeModel(self.model_name)
        prompt = f"""
        Write an Executive Summary for a Project Report based on these risks:
        {json.dumps(risk_json)}

        Language: {language}
        Style: Professional, concise.
        """
        try:
            res = model.generate_content(prompt)
            return res.text
        except Exception as e:
            return f"Error generating summary: {e}"

    def generate_pdf(self, data, language="pt"):
        """
        data: {
            'summary': str,
            'risk_analysis_json': list,
            'charts': [base64_str, ...]
        }
        """
        summary = data.get('summary', '')
        risks = data.get('risk_analysis_json', [])
        charts = data.get('charts', [])

        # HTML Template
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Helvetica, sans-serif; color: #333; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #e74c3c; padding-bottom: 10px; }}
                h2 {{ color: #e67e22; margin-top: 20px; }}
                .risk-item {{ background: #f9f9f9; padding: 10px; margin-bottom: 10px; border-left: 5px solid #bdc3c7; }}
                .risk-high {{ border-left-color: #e74c3c; }}
                .risk-medium {{ border-left-color: #f39c12; }}
                .risk-low {{ border-left-color: #27ae60; }}
                .chart {{ margin: 20px 0; text-align: center; }}
                img {{ max-width: 100%; }}
            </style>
        </head>
        <body>
            <h1>Planus AI - Project Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

            <h2>Executive Summary</h2>
            <div>{summary.replace(chr(10), '<br>')}</div>

            <h2>Risk Analysis</h2>
            {''.join([self._format_risk(r) for r in risks])}

            <h2>Visualizations</h2>
            {''.join([f'<div class="chart"><img src="data:image/png;base64,{c}"></div>' for c in charts])}

        </body>
        </html>
        """

        # Generate PDF
        try:
            font_config = FontConfiguration()
            pdf_bytes = HTML(string=html_content).write_pdf(font_config=font_config)
            return pdf_bytes
        except Exception as e:
            return str(e)

    def _format_risk(self, r):
        prob = r.get('probability', '').lower()
        cls = 'risk-item'
        if 'high' in prob or 'alto' in prob: cls += ' risk-high'
        elif 'medium' in prob or 'medio' in prob: cls += ' risk-medium'
        elif 'low' in prob or 'baixo' in prob: cls += ' risk-low'

        return f"""
        <div class="{cls}">
            <h3>{r.get('title')} ({r.get('probability')})</h3>
            <p>{r.get('description')}</p>
            <small>Mitigation: {r.get('mitigation')}</small>
        </div>
        """
