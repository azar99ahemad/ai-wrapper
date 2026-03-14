"""Docker sandbox service - manages isolated containers for project execution."""

import logging
import os
import tempfile

import docker
from docker.errors import DockerException, NotFound

from app.core.config import settings

logger = logging.getLogger(__name__)


class SandboxService:
    """Manages Docker containers for running generated projects."""

    def __init__(self):
        try:
            self.client = docker.from_env()
        except DockerException:
            logger.warning("Docker not available - sandbox operations will fail")
            self.client = None

    def _ensure_client(self):
        if self.client is None:
            raise RuntimeError("Docker is not available")

    async def create_project_directory(
        self, project_id: str, files: dict[str, str]
    ) -> str:
        """Write project files to a temporary directory.

        Args:
            project_id: Unique project identifier.
            files: Dict mapping file paths to content.

        Returns:
            Path to the project directory.
        """
        project_dir = os.path.join(tempfile.gettempdir(), "ai-wrapper-projects", project_id)
        os.makedirs(project_dir, exist_ok=True)

        for file_path, content in files.items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)

        logger.info(f"Created project directory: {project_dir} with {len(files)} files")
        return project_dir

    async def start_container(
        self,
        project_id: str,
        project_dir: str,
        install_command: str = "npm install",
        dev_command: str = "npm run dev",
        port: int = 3000,
    ) -> tuple[str, str]:
        """Start a Docker container for the project.

        Args:
            project_id: Unique project identifier.
            project_dir: Path to the project directory.
            install_command: Command to install dependencies.
            dev_command: Command to start the dev server.
            port: Port the dev server listens on.

        Returns:
            Tuple of (container_id, preview_url)
        """
        self._ensure_client()

        container_name = f"ai-wrapper-{project_id[:12]}"

        # Remove existing container if present
        await self.stop_container(container_name)

        # Build the startup command
        startup_script = f"cd /app && {install_command} && {dev_command}"

        container = self.client.containers.run(
            image=settings.sandbox_image,
            command=["sh", "-c", startup_script],
            name=container_name,
            volumes={project_dir: {"bind": "/app", "mode": "rw"}},
            ports={f"{port}/tcp": None},  # Random host port
            detach=True,
            mem_limit=settings.sandbox_memory_limit,
            cpu_quota=int(settings.sandbox_cpu_limit * 100000),
            environment={"NODE_ENV": "development"},
            network_mode="bridge",
        )

        # Get the assigned port
        container.reload()
        host_port = container.ports.get(f"{port}/tcp")
        if host_port:
            preview_url = f"http://localhost:{host_port[0]['HostPort']}"
        else:
            preview_url = f"http://localhost:{port}"

        logger.info(f"Started container {container.id[:12]} at {preview_url}")
        return container.id, preview_url

    async def stop_container(self, container_id_or_name: str) -> None:
        """Stop and remove a container."""
        self._ensure_client()
        try:
            container = self.client.containers.get(container_id_or_name)
            container.stop(timeout=10)
            container.remove(force=True)
            logger.info(f"Stopped container: {container_id_or_name}")
        except NotFound:
            pass
        except Exception as e:
            logger.error(f"Error stopping container {container_id_or_name}: {e}")

    async def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """Get container logs."""
        self._ensure_client()
        try:
            container = self.client.containers.get(container_id)
            return container.logs(tail=tail).decode("utf-8", errors="replace")
        except NotFound:
            return "Container not found"
        except Exception as e:
            return f"Error getting logs: {e}"

    async def get_container_status(self, container_id: str) -> str:
        """Get container status."""
        self._ensure_client()
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except NotFound:
            return "not_found"
        except Exception as e:
            return f"error: {e}"
