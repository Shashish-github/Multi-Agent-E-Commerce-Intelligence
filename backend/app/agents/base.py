"""
Abstract base class for typed, observable AI agents.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import time
from app.core.telemetry import logger


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Wrap agent execution with telemetry, timing, and error handling."""
        start_time = time.time()
        agent_meta: Dict[str, Any] = {
            "agent_name": self.name,
            "status": "RUNNING",
            "started_at": start_time,
            "duration_ms": 0.0,
            "error_code": None,
            "token_usage": 0,
            "metadata": {}
        }

        try:
            logger.info(f"[{self.name}] Beginning execution...")
            output_state = await self.process(state)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            agent_meta["status"] = "COMPLETED"
            agent_meta["duration_ms"] = duration_ms
            agent_meta["completed_at"] = time.time()
            logger.info(f"[{self.name}] Completed in {duration_ms}ms")
            
            # Record agent run in state
            runs = output_state.get("agent_runs", [])
            runs.append(agent_meta)
            output_state["agent_runs"] = runs
            return output_state

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            agent_meta["status"] = "DEGRADED" if self.allow_degradation() else "FAILED"
            agent_meta["duration_ms"] = duration_ms
            agent_meta["error_code"] = type(e).__name__
            agent_meta["metadata"]["error_message"] = str(e)
            agent_meta["completed_at"] = time.time()
            logger.error(f"[{self.name}] Error after {duration_ms}ms: {e}", exc_info=True)

            runs = state.get("agent_runs", [])
            runs.append(agent_meta)
            state["agent_runs"] = runs
            
            if self.allow_degradation():
                # Handle graceful degradation
                return await self.handle_fallback(state, str(e))
            else:
                raise e

    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Core agent logic to be implemented by specialized agents."""
        pass

    def allow_degradation(self) -> bool:
        """Override to True if this agent failure should not abort the entire pipeline."""
        return True

    async def handle_fallback(self, state: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Fallback implementation when agent fails."""
        return state
