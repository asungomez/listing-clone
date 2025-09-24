import logging
import os
from typing import Any, Dict

import docker
import pytest
from testcontainers.core.container import DockerContainer  # type: ignore
from testcontainers.core.network import Network  # type: ignore
from testcontainers.core.waiting_utils import wait_for_logs  # type: ignore

from .factories.user import UserFactory
from .utils import Helper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


_front_end_url = None


def set_base_url(url: str) -> None:
    """Set the base URL for Playwright tests"""
    global _front_end_url
    _front_end_url = url


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: Dict[str, Any]
) -> Dict[str, Any]:
    """Override the browser_context_args fixture to set the base URL"""
    global _front_end_url
    if _front_end_url:
        return {
            **browser_context_args,
            "base_url": _front_end_url
        }
    return browser_context_args


@pytest.fixture(scope="session", autouse=True)
def tests_helper(request: pytest.FixtureRequest) -> Helper:
    """
    Spin up all necessary containers and return a Helper object to use
    in tests.
    This fixture is automatically used in all tests.
    """

    docker_client = docker.from_env()

    db_container: DockerContainer = None
    mockserver_container: DockerContainer = None
    back_end_container: DockerContainer = None
    front_end_container: DockerContainer = None
    back_end_image = None
    front_end_image = None

    def cleanup() -> None:
        try:
            if db_container is not None:
                logger.info("Stopping database container")
                db_container.stop()
                db_container._container.remove(force=True)
            if mockserver_container is not None:
                logger.info("Stopping MockServer container")
                mockserver_container.stop()
                mockserver_container._container.remove(force=True)
            if network is not None:
                logger.info("Removing network")
                network.remove()
            if back_end_image is not None:
                logger.info("Removing back-end image")
                docker_client.images.remove(back_end_image.id, force=True)
            if back_end_container is not None:
                logger.info("Stopping back-end container")
                back_end_container.stop()
                back_end_container._container.remove(force=True)
            if front_end_container is not None:
                logger.info("Stopping front-end container")
                front_end_container.stop()
                front_end_container._container.remove(force=True)
            if front_end_image is not None:
                logger.info("Removing front-end image")
                docker_client.images.remove(front_end_image.id, force=True)
        except Exception as e:
            logger.error("Error during cleanup: %s", str(e))

    request.addfinalizer(cleanup)

    try:
        # Create Docker Network
        network = Network().create()

        # Create a Posgres container inside the network
        logger.info("Starting PostgreSQL container")
        db_container = (
            DockerContainer(image="postgres:17-alpine")
            .with_exposed_ports(5432)
            .with_env("POSTGRES_DB", "test")
            .with_env("POSTGRES_USER", "test")
            .with_env("POSTGRES_PASSWORD", "test")
            .with_network(network)
            .with_network_aliases(("db"))
            .start()
        )

        # Create a MockServer container inside the network
        logger.info("Starting MockServer container")
        mockserver_container = (
            DockerContainer(image="mockserver/mockserver")
            .with_exposed_ports(1080)
            .with_network(network)
            .with_network_aliases(("mockserver"))
            .start()
        )

        # Build the back-end image
        build_env = os.environ.get("BUILD_ENV", "development")
        logger.info("Building image")
        back_end_image, _ = docker_client.images.build(
            path="../back-end",
            buildargs={"BUILD_ENV": build_env}
            )

        # Spin up the back-end container
        logger.info("Starting container")
        mockserver_url = "http://mockserver:1080"
        front_end_url = "http://front-end:5173"
        back_end_container = (
            DockerContainer(image=back_end_image.id)
            .with_exposed_ports(8000)
            .with_env("ALLOWED_ORIGINS", "*")
            .with_env("ALLOWED_HOSTS", "*")
            .with_env("DB_HOST", "db")
            .with_env("DB_NAME", "test")
            .with_env("DB_PASSWORD", "test")
            .with_env("DB_PORT", "5432")
            .with_env("DB_USER", "test")
            .with_env("DEBUG", "True")
            .with_env("DJANGO_SECRET_KEY", "test")
            .with_env("FRONT_END_URL", front_end_url)
            .with_env("MOCK_AUTH", "True")
            .with_env("OKTA_CLIENT_ID", "client-id")
            .with_env("OKTA_CLIENT_SECRET", "client-secret")
            .with_env("OKTA_DOMAIN", f"{mockserver_url}/okta")
            .with_env("OKTA_LOGIN_REDIRECT", front_end_url)
            .with_env("USE_HTTPS", False)
            .with_env(
                "ENCRYPTION_KEY",
                "HqvJK8Ur9q_ZFZlnM-1TOKu7sK4HidccP6NnmMdCEVo="
                )
            .with_network(network)
            .with_network_aliases(("back-end"))
            .start()
        )

        # Wait for Gunicorn to start
        logger.info("Waiting for Gunicorn to start")
        wait_for_logs(
            back_end_container,
            "Listening at: http://0.0.0.0:8000",
            timeout=30,
        )

        # Run the DB migrations
        logger.info("Running migrations")
        exit_code, output = back_end_container.exec(
            "python /app/manage.py migrate",
        )
        if exit_code != 0:
            logger.error(f"Migration failed: {output.decode()}")
            raise Exception("Failed to apply migrations")
        else:
            logger.info("Migrations applied successfully")

        # Build the front-end image
        logger.info("Building front-end image")
        # Get the external back-end URL
        back_end_host = back_end_container.get_container_host_ip()
        back_end_port = back_end_container.get_exposed_port(8000)
        back_end_url = f"http://{back_end_host}:{back_end_port}"
        login_redirect = f"{back_end_url}/users/login-callback"
        front_end_image, _ = docker_client.images.build(
            path="../front-end",
            buildargs={
                "BUILD_ENV": build_env,
                "OKTA_DOMAIN": "http://localhost:1080/okta",
                "OKTA_CLIENT_ID": "client-id",
                "OKTA_LOGIN_REDIRECT": login_redirect,
                "API_URL": back_end_url
            }
        )

        # Spin up the front-end container
        logger.info("Starting front-end container")
        front_end_container = (
            DockerContainer(image=front_end_image.id)
            .with_exposed_ports(5173)
            .with_network(network)
            .with_network_aliases(("front-end"))
            .start()
        )

        # Get the DB port
        db_port = db_container.get_exposed_port(5432)

        # Get the external MockServer URL
        mockserver_host = mockserver_container.get_container_host_ip()
        mockserver_port = mockserver_container.get_exposed_port(1080)
        mockserver_external_url = f"http://{mockserver_host}:{mockserver_port}"

        # Get the external back-end URL
        back_end_host = back_end_container.get_container_host_ip()
        back_end_port = back_end_container.get_exposed_port(8000)
        back_end_url = f"http://{back_end_host}:{back_end_port}"

        # Get the external front-end URL
        front_end_host = front_end_container.get_container_host_ip()
        front_end_port = front_end_container.get_exposed_port(5173)
        front_end_url = f"http://{front_end_host}:{front_end_port}"

        set_base_url(front_end_url)

        helper = Helper(
            db_port=db_port,
            mockserver_url=mockserver_external_url,
            back_end_url=back_end_url,
            front_end_url=front_end_url
          )
        return helper
    except Exception as e:
        logger.error("Error starting containerized system: %s", str(e))
        raise Exception(f"Failed to start containerized system: {str(e)}")


@pytest.fixture(autouse=True)
def tear_down(request: pytest.FixtureRequest, tests_helper: Helper) -> None:
    """
    Tear down after each test.
    This is used to clean up the database and remove the mocks
    after each test.
    """

    def cleanup() -> None:
        tests_helper.clean_up_db()
        tests_helper.clean_up_mocks()

    request.addfinalizer(cleanup)


@pytest.fixture
def user_factory() -> UserFactory:
    """
    Fixture that provides a UserFactory instance.

    Usage:
        def test_something(user_factory):
            user = user_factory.generate(is_active=False)
    """
    return UserFactory()
