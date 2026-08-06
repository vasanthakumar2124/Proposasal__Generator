from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DomainEvent:
    event_type: str
    organization_id: str
    user_id: str
    resource_type: str
    resource_id: str
    payload: dict = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


EVENT_USER_REGISTERED = "user.registered"

EVENT_CLIENT_CREATED = "client.created"

EVENT_PROJECT_CREATED = "project.created"

EVENT_WORKSPACE_CREATED = "workspace.created"

EVENT_PROPOSAL_CREATED = "proposal.created"
EVENT_PROPOSAL_GENERATED = "proposal.generated"
EVENT_PROPOSAL_FAILED = "proposal.failed"
