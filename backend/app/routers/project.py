from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.parser import MSProjectParser
from app.models import ProjectAnalysis, Task
from typing import List

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.post("/upload", response_model=List[Task])
async def upload_project_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="Only .xml files are supported")
    
    content = await file.read()
    try:
        parser = MSProjectParser(content.decode('utf-8'))
        tasks = parser.parse_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")




@router.post("/analyze")
async def analyze_project(tasks: List[Task]):
    from app.agents.schedule_analyst import ScheduleAnalyst
    from app.agents.resource_manager import ResourceManager
    from app.agents.risk_analyst import RiskAnalyst
    from app.agents.chart_generator import ChartGenerator
    from app.agents.text_report_generator import TextReportGenerator

    try:
        # 1. Schedule Analysis
        schedule_analyst = ScheduleAnalyst()
        schedule_analysis = schedule_analyst.analyze(tasks)
        
        # 2. Resource Analysis
        resource_manager = ResourceManager()
        resource_analysis = resource_manager.analyze(tasks)
        
        # 3. Risk Analysis
        risk_analyst = RiskAnalyst()
        risk_analysis = risk_analyst.analyze(tasks, resource_analysis)
        
        # 4. Generate Charts Data
        chart_generator = ChartGenerator()
        chart_data = chart_generator.generate_charts(tasks, resource_analysis, risk_analysis)
        
        # 5. Generate Text Reports (for all languages)
        text_generator = TextReportGenerator()
        
        # Create a comprehensive analysis object for the text generator
        full_analysis = {
            "schedule_analysis": schedule_analysis,
            "resource_analysis": resource_analysis,
            "risk_analysis": risk_analysis
        }
        
        text_reports = {
            "pt": text_generator.generate_report(tasks, full_analysis, "pt"),
            "en": text_generator.generate_report(tasks, full_analysis, "en"),
            "es": text_generator.generate_report(tasks, full_analysis, "es")
        }
        
        return {
            "schedule_analysis": schedule_analysis,
            "resource_analysis": resource_analysis,
            "risk_analysis": risk_analysis,
            "chart_data": chart_data,
            "text_reports": text_reports
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze-contract")
async def analyze_contract(
    contract_file: UploadFile = File(...),
    schedule_file: UploadFile = File(...),
    language: str = "en"
):
    """
    Analyze contract vs schedule.
    Accepts contract (PDF/DOCX) and schedule (XML).
    Returns comprehensive comparison analysis + standard analysis.
    """
    from app.agents.contract_analyst import ContractAnalyst
    from app.agents.schedule_analyst import ScheduleAnalyst
    from app.agents.resource_manager import ResourceManager
    from app.agents.risk_analyst import RiskAnalyst
    from app.agents.chart_generator import ChartGenerator
    from app.agents.text_report_generator import TextReportGenerator
    
    # Validate file types
    if not schedule_file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="Schedule must be .xml file")
    
    allowed_contract_extensions = ['.pdf', '.docx', '.doc']
    if not any(contract_file.filename.endswith(ext) for ext in allowed_contract_extensions):
        raise HTTPException(
            status_code=400, 
            detail="Contract must be PDF or DOCX file"
        )
    
    try:
        # Parse schedule
        schedule_content = await schedule_file.read()
        parser = MSProjectParser(schedule_content.decode('utf-8'))
        tasks = parser.parse_tasks()
        
        # Parse contract
        contract_content = await contract_file.read()
        analyst = ContractAnalyst()
        
        if contract_file.filename.endswith('.pdf'):
            contract_data = analyst.parse_contract_pdf(contract_content)
        else:
            contract_data = analyst.parse_contract_docx(contract_content)
        
        # Compare and analyze (Contract)
        comparison = analyst.compare_with_schedule(contract_data, tasks, language)
        
        # Run Standard Analysis (Schedule, Resource, Risk)
        # 1. Schedule Analysis
        schedule_analyst = ScheduleAnalyst()
        schedule_analysis = schedule_analyst.analyze(tasks, language)
        
        # 2. Resource Analysis
        resource_manager = ResourceManager()
        resource_analysis = resource_manager.analyze(tasks, language)
        
        # 3. Risk Analysis
        risk_analyst = RiskAnalyst()
        risk_analysis = risk_analyst.analyze(tasks, resource_analysis, language)
        
        # 4. Generate Charts Data
        chart_generator = ChartGenerator()
        chart_data = chart_generator.generate_charts(tasks, resource_analysis, risk_analysis)
        
        # 5. Generate Text Reports
        text_generator = TextReportGenerator()
        full_analysis = {
            "schedule_analysis": schedule_analysis,
            "resource_analysis": resource_analysis,
            "risk_analysis": risk_analysis,
            "contract_analysis": comparison.dict()
        }
        
        text_reports = {
            "pt": text_generator.generate_report(tasks, full_analysis, "pt"),
            "en": text_generator.generate_report(tasks, full_analysis, "en"),
            "es": text_generator.generate_report(tasks, full_analysis, "es")
        }
        
        return {
            "agent": "Contract Analyst",
            "comparison": comparison.dict(),
            "contract_data": {
                "activities_found": len(contract_data.get("activities", [])),
                "deadlines_found": len(contract_data.get("deadlines", [])),
                "deliverables_found": len(contract_data.get("deliverables", []))
            },
            # Include standard analysis results
            "schedule_analysis": schedule_analysis,
            "resource_analysis": resource_analysis,
            "risk_analysis": risk_analysis,
            "chart_data": chart_data,
            "text_reports": text_reports
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to analyze contract: {str(e)}"
        )
