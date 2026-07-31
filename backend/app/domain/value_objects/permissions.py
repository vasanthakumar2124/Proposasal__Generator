from dataclasses import dataclass, field


@dataclass(frozen=True)
class Permission:
    resource: str
    action: str

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"

    @classmethod
    def from_string(cls, permission_str: str) -> "Permission":
        parts = permission_str.split(":", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid permission format: {permission_str}")
        return cls(resource=parts[0], action=parts[1])


@dataclass
class PermissionSet:
    permissions: set[str] = field(default_factory=set)

    def has(self, permission: str) -> bool:
        return permission in self.permissions

    def has_any(self, *permissions: str) -> bool:
        return any(p in self.permissions for p in permissions)

    def has_all(self, *permissions: str) -> bool:
        return all(p in self.permissions for p in permissions)

    def add(self, permission: str) -> None:
        self.permissions.add(permission)

    def remove(self, permission: str) -> None:
        self.permissions.discard(permission)
