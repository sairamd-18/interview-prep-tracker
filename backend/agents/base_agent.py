"""
Base Agent class providing execution timing, error handling, standardized input/output validation,
and metrics recording.
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(name)
        self.call_count = 0
        self.total_latency_ms = 0.0

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task and return structured output dictionary."""
        pass

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper to handle performance tracking, logging, and error resilience."""
        start_time = time.time()
        self.call_count += 1
        self.logger.info(f"Executing agent with inputs: {list(input_data.keys())}")
        
        try:
            result = self.run(input_data)
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.total_latency_ms += elapsed_ms
            
            result["agent_metadata"] = {
                "agent_name": self.name,
                "execution_time_ms": round(elapsed_ms, 2),
                "status": "success"
            }
            self.logger.info(f"Completed in {elapsed_ms:.1f}ms")
            return result
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.logger.error(f"Error during execution: {str(e)}", exc_info=True)
            return {
                "agent_metadata": {
                    "agent_name": self.name,
                    "execution_time_ms": round(elapsed_ms, 2),
                    "status": "error",
                    "error_message": str(e)
                },
                "success": False,
                "error": str(e)
            }

    def get_avg_latency(self) -> float:
        return (self.total_latency_ms / self.call_count) if self.call_count > 0 else 0.0
