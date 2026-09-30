"""
Telemetry, correlation IDs, and structured observability logging.
"""
import uuid
import time
import logging
from typing import Optional, Dict, Any
from contextvars import ContextVar

# Correlation ID context
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
investigation_id_ctx: ContextVar[str] = ContextVar("investigation_id", default="")

class CorrelationFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "correlation_id"):
            record.correlation_id = get_request_id() or "none"
        return super().format(record)


handler = logging.StreamHandler()
handler.setFormatter(CorrelationFormatter("%(asctime)s [%(levelname)s] [req_id=%(correlation_id)s] %(name)s: %(message)s"))

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = [handler]

logger = logging.getLogger("commerce_intelligence")


def get_request_id() -> str:
    rid = request_id_ctx.get()
    return rid if rid else str(uuid.uuid4())


def set_request_id(rid: str) -> None:
    request_id_ctx.set(rid)


def get_investigation_id() -> str:
    return investigation_id_ctx.get()


def set_investigation_id(inv_id: str) -> None:
    investigation_id_ctx.set(inv_id)


class AgentExecutionTimer:
    """Context manager for timing and recording agent runs."""
    def __init__(self, agent_name: str, investigation_id: Optional[str] = None):
        self.agent_name = agent_name
        self.investigation_id = investigation_id or get_investigation_id()
        self.start_time = 0.0
        self.end_time = 0.0
        self.duration_ms = 0.0
        self.status = "PENDING"
        self.error: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def __enter__(self):
        self.start_time = time.time()
        self.status = "RUNNING"
        logger.info(f"Agent '{self.agent_name}' started for investigation '{self.investigation_id}'")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        if exc_type is not None:
            self.status = "FAILED"
            self.error = str(exc_val)
            logger.error(f"Agent '{self.agent_name}' failed after {self.duration_ms}ms: {self.error}")
        else:
            self.status = "COMPLETED"
            logger.info(f"Agent '{self.agent_name}' completed in {self.duration_ms}ms")
        return False  # Do not suppress exceptions
