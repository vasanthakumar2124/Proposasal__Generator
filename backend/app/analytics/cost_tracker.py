import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("proposalcraft.cost_tracker")


@dataclass
class ProposalCostSummary:
    proposal_id: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    total_latency_ms: int = 0
    call_count: int = 0
    models_used: set[str] = field(default_factory=set)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def record_call(self, model: str, input_tokens: int, output_tokens: int, cost: float, latency_ms: int) -> None:
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        self.total_latency_ms += latency_ms
        self.call_count += 1
        self.models_used.add(model)

    def finalize(self) -> dict:
        self.completed_at = datetime.now(timezone.utc)
        duration = (self.completed_at - self.started_at).total_seconds()
        return {
            "proposal_id": self.proposal_id,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": round(self.total_cost, 6),
            "total_latency_ms": self.total_latency_ms,
            "call_count": self.call_count,
            "models_used": sorted(self.models_used),
            "duration_seconds": round(duration, 2),
            "timestamp": self.completed_at.isoformat(),
        }


class CostTracker:
    def __init__(self):
        self._active: dict[str, ProposalCostSummary] = {}

    def start(self, proposal_id: str) -> ProposalCostSummary:
        summary = ProposalCostSummary(proposal_id=proposal_id)
        self._active[proposal_id] = summary
        return summary

    def record(self, proposal_id: str, model: str, input_tokens: int, output_tokens: int, cost: float, latency_ms: int) -> None:
        summary = self._active.get(proposal_id)
        if summary:
            summary.record_call(model, input_tokens, output_tokens, cost, latency_ms)

    def finish(self, proposal_id: str) -> Optional[dict]:
        summary = self._active.pop(proposal_id, None)
        if summary:
            result = summary.finalize()
            logger.info(
                "Proposal %s cost summary: calls=%d tokens=%d cost=%.6f duration=%.1fs models=%s",
                proposal_id, result["call_count"], result["total_tokens"],
                result["total_cost"], result["duration_seconds"], result["models_used"],
            )
            return result
        return None


cost_tracker = CostTracker()
