import pytest

from briefcase.commands.create import git
from briefcase.exceptions import BriefcaseCommandError


def test_no_git(tracking_create_command, monkeypatch):
    """If Git is not installed, an error is raised."""

    def monkeypatch_verify_git(*a, **kw):
        raise BriefcaseCommandError("Briefcase requires git, but it is not installed")

    monkeypatch.setattr(git, "verify_git_is_installed", monkeypatch_verify_git)

    # The command will fail tool verification.
    with pytest.raises(
        BriefcaseCommandError,
        match=r"Briefcase requires git, but it is not installed",
    ):
        tracking_create_command()


def test_create(tracking_create_command):
    """The create command can be called."""
    tracking_create_command()

    # The right sequence of things will be done
    assert tracking_create_command.actions == [
        # Host OS is verified
        ("verify-host",),
        # Tools are verified
        ("verify-tools",),
        # App configs have been finalized
        ("finalize-app-config", "first"),
        ("finalize-app-config", "second"),
        # Create the first app
        ("generate", "first"),
        ("support", "first"),
        ("verify-app-tools", "first"),
        ("code", "first", False),
        ("requirements", "first", False),
        ("resources", "first"),
        ("cleanup", "first"),
        # Create the second app
        ("generate", "second"),
        ("support", "second"),
        ("verify-app-tools", "second"),
        ("code", "second", False),
        ("requirements", "second", False),
        ("resources", "second"),
        ("cleanup", "second"),
    ]

    # New app content has been created
    assert (tracking_create_command.platform_path / "first.bundle" / "new").exists()
    assert (tracking_create_command.platform_path / "second.bundle" / "new").exists()


def test_create_single(tracking_create_command):
    """The create command can be called to create a single app from the config."""
    tracking_create_command(app=tracking_create_command.apps["first"])

    # The right sequence of things will be done
    assert tracking_create_command.actions == [
        # Host OS is verified
        ("verify-host",),
        # Tools are verified
        ("verify-tools",),
        # App config has been finalized
        ("finalize-app-config", "first"),
        # Create the first app
        ("generate", "first"),
        ("support", "first"),
        ("verify-app-tools", "first"),
        ("code", "first", False),
        ("requirements", "first", False),
        ("resources", "first"),
        ("cleanup", "first"),
    ]

    # New app content has been created
    assert (tracking_create_command.platform_path / "first.bundle" / "new").exists()
    assert not (
        tracking_create_command.platform_path / "second.bundle" / "new"
    ).exists()
