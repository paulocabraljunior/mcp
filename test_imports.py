
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("Importing agents...")
try:
    from app.agents.contract_analyst import ContractAnalyst
    print("ContractAnalyst imported")
    from app.agents.schedule_analyst import ScheduleAnalyst
    print("ScheduleAnalyst imported")
    from app.agents.resource_manager import ResourceManager
    print("ResourceManager imported")
    from app.agents.risk_analyst import RiskAnalyst
    print("RiskAnalyst imported")
    from app.agents.chart_generator import ChartGenerator
    print("ChartGenerator imported")
    from app.agents.text_report_generator import TextReportGenerator
    print("TextReportGenerator imported")
    
    print("All imports successful")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
