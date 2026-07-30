from typing import Dict, Any
from app.tools.budget_tool import calculate_budget_breakdown

from app.utils.logger import logger

class BudgetAgent:
    def __init__(self):
        self.name = "Budget Agent"

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.run(state)
        except Exception as e:
            logger.error(f"[BudgetAgent] Error in run_async: {e}", exc_info=True)
            return {"budget_breakdown": {}, "estimated_total": 0}

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            budget = state.get("budget", 20000)
            days = state.get("duration_days", 4)
            breakdown = calculate_budget_breakdown(budget, days)
            return {
                "budget_breakdown": breakdown,
                "estimated_total": breakdown["total"]
            }
        except Exception as e:
            logger.error(f"[BudgetAgent] Exception in run: {e}", exc_info=True)
            return {"budget_breakdown": {}, "estimated_total": 0}

budget_agent = BudgetAgent()

