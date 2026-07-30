import asyncio
from typing import Dict, Any, List, AsyncGenerator
from app.agents.supervisor import supervisor_agent
from app.agents.planner_agent import planner_agent
from app.agents.destination_agent import destination_agent
from app.agents.weather_agent import weather_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.transport_agent import transport_agent
from app.agents.restaurant_agent import restaurant_agent
from app.agents.budget_agent import budget_agent
from app.agents.itinerary_agent import itinerary_agent
from app.agents.packing_agent import packing_agent
from app.agents.report_agent import report_agent
from app.utils.logger import logger

class LangGraphTripPlannerWorkflow:
    """Orchestrates LangGraph multi-agent network execution and emits progress stream events."""
    
    def __init__(self):
        self.agents_map = {
            "planner": (planner_agent, "Planning high-level trip strategy & daily timeline..."),
            "destination": (destination_agent, "Researching sights, attractions & map coordinates..."),
            "weather": (weather_agent, "Analyzing climate conditions & temperature forecast..."),
            "hotel": (hotel_agent, "Searching curated hotels matching budget & luxury levels..."),
            "transport": (transport_agent, "Calculating optimal flight & transport routes..."),
            "restaurant": (restaurant_agent, "Finding local dining spots matching dietary preferences..."),
            "budget": (budget_agent, "Computing itemized financial allocation breakdown..."),
            "itinerary": (itinerary_agent, "Synthesizing hourly day-by-day timetable..."),
            "packing": (packing_agent, "Assembling custom packing list & emergency contacts..."),
            "report": (report_agent, "Generating final autonomous travel plan package...")
        }

    async def execute_stream(self, request_payload: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        state = {
            "request": request_payload,
            "completed_nodes": [],
            "history": []
        }

        # Step 0: Emit Supervisor initialization event
        yield {
            "agent_name": "Supervisor Agent",
            "status": "starting",
            "message": "Supervisor Agent received trip requirement. Analyzing & delegating sub-tasks..."
        }
        await asyncio.sleep(0.3)

        while True:
            next_node = supervisor_agent.plan_next_step(state)
            if next_node == "FINISH":
                break

            agent_obj, start_msg = self.agents_map[next_node]
            agent_name = getattr(agent_obj, "name", next_node.capitalize() + " Agent")
            
            # Emit starting event for sub-agent
            yield {
                "agent_name": agent_name,
                "status": "in_progress",
                "message": start_msg
            }
            await asyncio.sleep(0.4)

            # Execute agent logic with error recovery
            try:
                if hasattr(agent_obj, "run_async"):
                    output = await agent_obj.run_async(state)
                else:
                    res = agent_obj.run(state)
                    output = await res if asyncio.iscoroutine(res) else res
                
                if isinstance(output, dict):
                    state.update(output)
                state["completed_nodes"].append(next_node)
                
                # Emit completed event for sub-agent
                yield {
                    "agent_name": agent_name,
                    "status": "completed",
                    "message": f"{agent_name} finished task successfully.",
                    "data": output
                }
                await asyncio.sleep(0.3)

            except Exception as e:
                logger.error(f"Error in node {next_node}: {e}", exc_info=True)
                state["completed_nodes"].append(next_node)
                yield {
                    "agent_name": agent_name,
                    "status": "error",
                    "message": f"Handled minor exception in {agent_name}: {str(e)}"
                }

        # Supervisor wrap up
        yield {
            "agent_name": "Supervisor Agent",
            "status": "completed",
            "message": "Autonomous travel plan generation complete!",
            "final_state": state
        }

    def execute_sync(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronously execute full agent graph to completion."""
        state = {"request": request_payload, "completed_nodes": []}
        for node_key in ["planner", "destination", "weather", "hotel", "restaurant", "budget", "itinerary", "transport", "packing", "report"]:

            agent_obj, _ = self.agents_map[node_key]
            try:
                if hasattr(agent_obj, "run_async"):
                    try:
                        loop = asyncio.get_running_loop()
                        import nest_asyncio
                        nest_asyncio.apply()
                        out = loop.run_until_complete(agent_obj.run_async(state))
                    except RuntimeError:
                        out = asyncio.run(agent_obj.run_async(state))
                else:
                    out = agent_obj.run(state)
                    if asyncio.iscoroutine(out):
                        out = asyncio.run(out)
                
                if isinstance(out, dict):
                    state.update(out)
            except Exception as e:
                logger.error(f"Error in execute_sync node {node_key}: {e}", exc_info=True)
            state["completed_nodes"].append(node_key)
        return state

langgraph_planner_workflow = LangGraphTripPlannerWorkflow()
