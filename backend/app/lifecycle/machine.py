"""Explicit state machine for the proposal lifecycle.

Every allowed transition is declared below; anything else raises
InvalidStateTransitionError. This is the single source of truth — services
must route status changes through `transition()` instead of setting the
status field directly.
"""

from app.config.constants import ProposalStatus
from app.domain.exceptions import InvalidStateTransitionError

_ALLOWED: dict[str, set[str]] = {
    ProposalStatus.DRAFT.value: {
        ProposalStatus.PROCESSING.value,
        ProposalStatus.GENERATING.value,
        ProposalStatus.REVIEW.value,
    },
    ProposalStatus.PROCESSING.value: {
        ProposalStatus.DRAFT.value,
        ProposalStatus.GENERATING.value,
        ProposalStatus.REVIEW.value,
        ProposalStatus.REJECTED.value,
    },
    ProposalStatus.GENERATING.value: {
        ProposalStatus.DRAFT.value,
        ProposalStatus.REVIEW.value,
    },
    ProposalStatus.REVIEW.value: {
        ProposalStatus.DRAFT.value,
        ProposalStatus.APPROVED.value,
        ProposalStatus.REJECTED.value,
    },
    ProposalStatus.APPROVED.value: {
        ProposalStatus.DRAFT.value,
        ProposalStatus.SENT.value,
    },
    ProposalStatus.REJECTED.value: {
        ProposalStatus.DRAFT.value,
    },
    ProposalStatus.SENT.value: set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in _ALLOWED.get(current, set())


def allowed_targets(current: str) -> set[str]:
    return set(_ALLOWED.get(current, set()))


def transition(current: str, target: str) -> str:
    if not can_transition(current, target):
        raise InvalidStateTransitionError("proposal", current, target)
    return target
