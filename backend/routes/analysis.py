from fastapi import APIRouter
from typing import Dict, Any
import json
import os

router = APIRouter(prefix="/analysis", tags=["Analysis & Findings"])

@router.get("/findings")
def get_historical_findings() -> Dict[str, Any]:
    """
    Returns empirical analysis findings, data distributions, and backtest results
    derived from the 1,988 historical COD orders.
    """
    findings_file = "analysis/findings.json"
    if os.path.exists(findings_file):
        try:
            with open(findings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to read findings: {e}"}

    return {"error": "Findings file not generated yet."}
