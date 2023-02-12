import pytest

from briefcase.commands import UpdateCommand
from briefcase.config import AppConfig
from briefcase.console import Console, Log


class DummyUpdateCommand(UpdateCommand):
    """A dummy update command that doesn't actually do anything.

    It only serves to track which actions would be performed.
    """

    platform = "tester"
    output_format = "dummy"
    description = "Dummy update command"

    def __init__(self, *args, apps, **kwargs):
        kwargs.setdefault("logger", Log())
        kwargs.setdefault("console", Console())
        super().__init__(*args, apps=apps, **kwargs)

        self.actions = []

    def bundle_path(self, app):
        return self.platform_path / f"{app.app_name}.dummy"

    def binary_path(self, app):
        return self.platform_path / f"{app.app_name}.dummy.bin"

    def distribution_path(self, app, packaging_format):
        return self.platform_path / f"{app.app_name}.dummy.{packaging_format}"

    def verify_host(self):
        super().verify_host()
        self.actions.append(("verify-host",))

    def verify_tools(self):
        super().verify_tools()
        self.actions.append(("verify-tools",))

    def finalize_app_config(self, app):
        super().finalize_app_config(app=app)
        self.actions.append(("finalize-app-config", app.app_name))

    def verify_app_tools(self, app):
        super().verify_app_tools(app=app)
        self.actions.append(("verify-app-tools", app.app_name))

    # Override all the body methods of a UpdateCommand
    # with versions that we can use to track actions performed.
    def install_app_requirements(self, app, test_mode):
        self.actions.append(("requirements", app.app_name, test_mode))
        with (self.bundle_path(app) / "requirements").open("w") as f:
            f.write("app requirements")

    def install_app_code(self, app, test_mode):
        self.actions.append(("code", app.app_name, test_mode))
        with (self.bundle_path(app) / "code.py").open("w") as f:
            f.write("print('app')")

    def install_app_resources(self, app):
        self.actions.append(("resources", app.app_name))
        with (self.bundle_path(app) / "resources").open("w") as f:
            f.write("app resources")

    def cleanup_app_content(self, app):
        self.actions.append(("cleanup", app.app_name))


@pytest.fixture
def update_command(tmp_path):
    return DummyUpdateCommand(
        base_path=tmp_path,
        apps={
            "first": AppConfig(
                app_name="first",
                bundle="com.example",
                version="0.0.1",
                description="The first simple app",
                sources=["src/first"],
            ),
            "second": AppConfig(
                app_name="second",
                bundle="com.example",
                version="0.0.2",
                description="The second simple app",
                sources=["src/second"],
            ),
        },
    )


@pytest.fixture
def first_app(tmp_path):
    """Populate skeleton app content for the first app."""
    bundle_dir = tmp_path / "tester" / "first.dummy"
    bundle_dir.mkdir(parents=True)
    with (bundle_dir / "Content").open("w") as f:
        f.write("first app.bundle")


@pytest.fixture
def second_app(tmp_path):
    """Populate skeleton app content for the second app."""
    bundle_dir = tmp_path / "tester" / "second.dummy"
    bundle_dir.mkdir(parents=True)
    with (bundle_dir / "Content").open("w") as f:
        f.write("second app.bundle")
