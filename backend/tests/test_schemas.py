"""Tests for Pydantic schemas validation."""


import pytest

from app.schemas.schemas import (
    EditPlan,
    FileMapEntry,
    GeneratedFile,
    ProjectArchitecture,
    ProjectCreate,
    ProjectSpecification,
    UserCreate,
)


class TestUserCreate:
    def test_valid_user(self):
        user = UserCreate(email="test@example.com", password="password123")
        assert user.email == "test@example.com"
        assert user.password == "password123"

    def test_short_password_rejected(self):
        with pytest.raises(Exception):
            UserCreate(email="test@example.com", password="short")

    def test_invalid_email_rejected(self):
        with pytest.raises(Exception):
            UserCreate(email="not-an-email", password="password123")


class TestProjectCreate:
    def test_valid_project(self):
        project = ProjectCreate(prompt="Build a job portal with salary filter")
        assert project.prompt == "Build a job portal with salary filter"
        assert project.name is None

    def test_with_name(self):
        project = ProjectCreate(prompt="Build a blog app", name="my-blog")
        assert project.name == "my-blog"

    def test_short_prompt_rejected(self):
        with pytest.raises(Exception):
            ProjectCreate(prompt="hi")


class TestProjectSpecification:
    def test_valid_spec(self):
        spec = ProjectSpecification(
            name="job-portal",
            description="A job portal with admin panel",
            features=["job listing", "salary filter", "admin panel"],
            tech_stack={"frontend": "Next.js", "styling": "TailwindCSS"},
            pages=["Home", "Jobs", "Admin"],
            api_endpoints=["GET /api/jobs", "POST /api/jobs"],
        )
        assert spec.name == "job-portal"
        assert len(spec.features) == 3
        assert spec.tech_stack["frontend"] == "Next.js"

    def test_minimal_spec(self):
        spec = ProjectSpecification(
            name="test",
            description="test",
            features=[],
            tech_stack={},
            pages=[],
        )
        assert spec.api_endpoints is None


class TestProjectArchitecture:
    def test_valid_architecture(self):
        arch = ProjectArchitecture(
            files=[
                FileMapEntry(path="package.json", description="Dependencies"),
                FileMapEntry(
                    path="src/app/page.tsx",
                    description="Main page",
                    dependencies=["package.json"],
                ),
            ],
            folder_structure="src/\n  app/\n    page.tsx",
        )
        assert len(arch.files) == 2
        assert arch.install_command == "npm install"
        assert arch.dev_command == "npm run dev"
        assert arch.port == 3000

    def test_custom_commands(self):
        arch = ProjectArchitecture(
            files=[],
            folder_structure="",
            install_command="yarn install",
            dev_command="yarn dev",
            port=8080,
        )
        assert arch.install_command == "yarn install"
        assert arch.port == 8080


class TestGeneratedFile:
    def test_valid_file(self):
        f = GeneratedFile(
            path="src/app/page.tsx",
            content='export default function Home() { return <div>Hello</div>; }',
            language="typescript",
        )
        assert f.path == "src/app/page.tsx"
        assert "Home" in f.content


class TestEditPlan:
    def test_valid_plan(self):
        plan = EditPlan(
            affected_files=["src/app/page.tsx"],
            changes_description="Add authentication",
            new_files=["src/components/AuthButton.tsx"],
        )
        assert len(plan.affected_files) == 1
        assert len(plan.new_files) == 1

    def test_plan_without_new_files(self):
        plan = EditPlan(
            affected_files=["src/app/page.tsx"],
            changes_description="Fix styling",
        )
        assert plan.new_files == []
