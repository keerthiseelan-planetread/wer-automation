from pydantic import BaseModel
from typing import List, Dict, Any

class WERResult(BaseModel):
    file_name: str
    ai_tool: str
    wer_score: float

class ToolMetrics(BaseModel):
    ai_tool: str
    average_wer: float
    best_wer: float
    worst_wer: float

class WERReport(BaseModel):
    language: str
    year: str
    month: str
    detailed_results: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]
    tool_wise_metrics: List[Dict[str, Any]]