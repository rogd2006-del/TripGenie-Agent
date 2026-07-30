import pytest
from app.services.langgraph_workflow import langgraph_planner_workflow

def test_langgraph_execution():
    req = {
        "prompt": "4-day trip to Goa under 20000",
        "destination": "Goa, India",
        "budget": 20000,
        "duration_days": 4,
        "food_preference": "Vegetarian"
    }
    result = langgraph_planner_workflow.execute_sync(req)
    assert result is not None
    assert result.get("destination") == "Goa, India"
    assert len(result.get("itinerary", [])) == 4
    assert "budget_breakdown" in result
