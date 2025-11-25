# Contract Analysis Agent Implementation Plan

## Goal

Implement a new AI agent that analyzes construction contracts and compares them with project schedules (MS Project XML). The agent will provide:

1. **Delayed Activities**: Identify tasks that are past their deadline
2. **Missing Activities**: Find activities mentioned in the contract but absent from the schedule
3. **Resource Analysis**: Analyze resource loading and productivity indices based on task progress
4. **Descriptive Analysis**: Generate a comprehensive comparison report

## User Review Required

> [!IMPORTANT]
> **Contract File Format**: What format will the contract be in? 
> - PDF (requires OCR/text extraction library like `PyPDF2` or `pdfplumber`)
> - Word/DOCX (requires `python-docx`)
> - Plain text/TXT
> 
> Please specify the expected contract format so I can add the appropriate parsing library.

> [!NOTE]
> **Analysis Approach**: The contract analysis will use keyword/pattern matching to identify activities, deadlines, and resource requirements. For more sophisticated analysis, we could integrate an LLM API (OpenAI, Google AI, etc.). Please let me know if you want basic pattern matching or AI-powered analysis.

## Proposed Changes

### Backend Components

#### [NEW] [contract_analyst.py](file:///home/kid/Documents/mcp/backend/app/agents/contract_analyst.py)

Create a new agent that:
- Parses contract documents to extract:
  - Activity/task names and descriptions
  - Deadlines and milestones
  - Resource requirements
  - Deliverables
- Compares contract activities with schedule tasks
- Identifies discrepancies (missing, delayed, mismatched)
- Calculates productivity indices based on progress vs. expected completion

**Key Methods**:
- `parse_contract(content: str) -> Dict`: Extract structured data from contract
- `compare_with_schedule(contract_data: Dict, tasks: List[Task]) -> Dict`: Perform comparison
- `calculate_productivity_indices(tasks: List[Task]) -> Dict`: Analyze resource productivity

---

#### [MODIFY] [models.py](file:///home/kid/Documents/mcp/backend/app/models.py)

Add new Pydantic models:
- `ContractActivity`: Represents an activity extracted from contract
- `ContractComparison`: Results of contract vs schedule comparison
- `ProductivityIndex`: Resource productivity metrics

---

#### [MODIFY] [project.py](file:///home/kid/Documents/mcp/backend/app/routers/project.py)

Add new endpoint:
```python
@router.post("/analyze-contract")
async def analyze_contract(
    contract_file: UploadFile,
    schedule_file: UploadFile
)
```

This endpoint will:
1. Parse both the contract and schedule XML
2. Run the ContractAnalyst agent
3. Return comprehensive comparison analysis

---

### Frontend Components

#### [MODIFY] [app.py](file:///home/kid/Documents/mcp/frontend/app.py)

Add new section in sidebar:
- **Contract Analysis Section**: New file uploaders for contract + schedule
- **"Analyze Contract vs Schedule" Button**: Triggers the comparison
- **Results Display**: Shows analysis including:
  - Delayed activities summary
  - Missing activities list
  - Resource productivity metrics
  - Detailed comparison table

Add new visualization tabs:
- **Contract Compliance**: Chart showing schedule adherence to contract
- **Productivity Dashboard**: Visual representation of resource efficiency

---

### Dependencies

#### [MODIFY] [requirements.txt](file:///home/kid/Documents/mcp/backend/requirements.txt)

Add document parsing library based on contract format:
- For PDF: `pdfplumber==0.10.3` (recommended for better text extraction)
- For DOCX: `python-docx==1.1.0`
- For advanced NLP: `spacy==3.7.2` (optional, for better text analysis)

## Verification Plan

### Automated Tests

1. **Contract Parsing Test**:
   ```bash
   # Test with sample contract document
   pytest backend/tests/test_contract_analyst.py
   ```

2. **Integration Test**:
   - Upload sample contract and schedule XML to API endpoint
   - Verify response contains all expected fields
   - Check for delayed tasks identification
   - Validate missing activities detection

### Manual Verification

1. **Frontend Testing**:
   - Open Streamlit app at http://localhost:8502
   - Upload a sample contract file
   - Upload a corresponding MS Project XML file
   - Click "Analyze Contract vs Schedule"
   - Verify results display includes:
     - ✅ Delayed activities with dates
     - ✅ Missing activities list
     - ✅ Resource productivity indices
     - ✅ Charts and visualizations

2. **Edge Cases**:
   - Empty contract file
   - Contract with no matching activities
   - Schedule with all on-time tasks
   - Contract with malformed dates
