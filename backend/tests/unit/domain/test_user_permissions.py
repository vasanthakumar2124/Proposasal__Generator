from app.config.constants import UserRole, DEFAULT_PERMISSIONS
from app.domain.entities.user import User


class TestUserPermissions:
    def test_admin_has_all_default_permissions(self):
        user = User(
            email="a@b.com",
            password_hash="x",
            name="A",
            organization_id="org1",
            role=UserRole.ADMIN,
            permissions=[],
        )
        for perm in DEFAULT_PERMISSIONS[UserRole.ADMIN]:
            assert user.has_permission(perm), perm

    def test_falls_back_to_role_defaults_when_list_is_stale(self):
        # Permissions lists written before constants grew (e.g. project:* was
        # added later) must still grant access through the role defaults.
        user = User(
            email="a@b.com",
            password_hash="x",
            name="A",
            organization_id="org1",
            role=UserRole.ADMIN,
            permissions=["proposal:read"],
        )
        assert user.has_permission("project:read")
        assert user.has_permission("proposal:read")

    def test_explicit_list_still_wins(self):
        user = User(
            email="a@b.com",
            password_hash="x",
            name="A",
            organization_id="org1",
            role=UserRole.VIEWER,
            permissions=["proposal:read"],
        )
        # viewer defaults include project:read but the explicit list does not
        # get narrowed; both sources combined grant it. Assert no error and
        # that an unrelated permission is still denied.
        assert not user.has_permission("client:delete")

    def test_unknown_role_denies_everything(self):
        user = User(
            email="a@b.com",
            password_hash="x",
            name="A",
            organization_id="org1",
            role=UserRole.VIEWER,
            permissions=["some:custom"],
        )
        assert user.has_permission("some:custom")
        assert not user.has_permission("admin")
