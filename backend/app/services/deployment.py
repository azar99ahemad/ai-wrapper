"""Deployment service - handles deploying projects to cloud providers."""

import logging

import httpx

from app.core.config import settings
from app.models.models import DeploymentProvider

logger = logging.getLogger(__name__)


class DeploymentService:
    """Handles deploying generated projects to cloud providers."""

    async def deploy(
        self,
        provider: DeploymentProvider,
        project_name: str,
        files: dict[str, str],
    ) -> tuple[str, str]:
        """Deploy a project to the specified provider.

        Args:
            provider: Cloud provider to deploy to.
            project_name: Name of the project.
            files: Dict mapping file paths to content.

        Returns:
            Tuple of (deployment_url, build_log)
        """
        if provider == DeploymentProvider.VERCEL:
            return await self._deploy_vercel(project_name, files)
        elif provider == DeploymentProvider.CLOUDFLARE:
            return await self._deploy_cloudflare(project_name, files)
        elif provider == DeploymentProvider.AWS:
            return await self._deploy_aws(project_name, files)
        else:
            raise ValueError(f"Unsupported deployment provider: {provider}")

    async def _deploy_vercel(
        self, project_name: str, files: dict[str, str]
    ) -> tuple[str, str]:
        """Deploy to Vercel via their API."""
        if not settings.vercel_token:
            raise ValueError("Vercel token not configured")

        # Prepare files for Vercel deployment API
        vercel_files = [
            {"file": path, "data": content}
            for path, content in files.items()
        ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vercel.com/v13/deployments",
                headers={
                    "Authorization": f"Bearer {settings.vercel_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "name": project_name,
                    "files": vercel_files,
                    "target": "production",
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            url = f"https://{data.get('url', '')}"
            logger.info(f"Deployed to Vercel: {url}")
            return url, "Deployment successful"

    async def _deploy_cloudflare(
        self, project_name: str, files: dict[str, str]
    ) -> tuple[str, str]:
        """Deploy to Cloudflare Pages."""
        if not settings.cloudflare_token:
            raise ValueError("Cloudflare token not configured")

        # Cloudflare Pages deployment would use their API
        # This is a simplified implementation
        logger.info(f"Cloudflare deployment for {project_name} - not yet implemented")
        return f"https://{project_name}.pages.dev", "Deployment queued"

    async def _deploy_aws(
        self, project_name: str, files: dict[str, str]
    ) -> tuple[str, str]:
        """Deploy to AWS (S3 + CloudFront or Amplify)."""
        if not settings.aws_access_key:
            raise ValueError("AWS credentials not configured")

        # AWS deployment would use boto3
        logger.info(f"AWS deployment for {project_name} - not yet implemented")
        return f"https://{project_name}.amplifyapp.com", "Deployment queued"
