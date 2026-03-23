"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { FileExplorer } from "@/components/FileExplorer";
import { CodeEditor } from "@/components/CodeEditor";
import { PreviewPanel } from "@/components/PreviewPanel";
import { PromptInput } from "@/components/PromptInput";

interface ProjectFile {
  id: string;
  path: string;
  content: string;
  version: number;
}

interface Project {
  id: string;
  name: string;
  description: string | null;
  prompt: string;
  status: string;
  preview_url: string | null;
  specification: string | null;
  architecture: string | null;
  files: ProjectFile[];
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export default function ProjectPage() {
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [selectedFile, setSelectedFile] = useState<ProjectFile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProject = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/projects/${projectId}`);
      if (!response.ok) throw new Error("Failed to fetch project");
      const data = await response.json();
      setProject(data);
      if (data.files?.length > 0 && !selectedFile) {
        setSelectedFile(data.files[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [projectId, selectedFile]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  const handleEditWithPrompt = async (prompt: string) => {
    if (!selectedFile || !project) return;
    setIsEditing(true);
    try {
      const response = await fetch(
        `${API_BASE}/projects/${project.id}/files/${selectedFile.id}/edit`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt }),
        }
      );
      if (response.ok) {
        const result = await response.json();
        setSelectedFile(result.file);
        await fetchProject();
      }
    } catch (err) {
      console.error("Edit failed:", err);
    } finally {
      setIsEditing(false);
    }
  };

  const handleDeploy = async (provider: string) => {
    if (!project) return;
    try {
      const response = await fetch(
        `${API_BASE}/projects/${project.id}/deploy`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider }),
        }
      );
      if (response.ok) {
        const deployment = await response.json();
        alert(`Deployed! URL: ${deployment.url || "Pending..."}`);
        await fetchProject();
      }
    } catch (err) {
      console.error("Deploy failed:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 mx-auto animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-lg font-medium text-red-600">
            {error || "Project not found"}
          </p>
          <a href="/" className="mt-4 text-primary-600 hover:underline">
            ← Back to home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Toolbar */}
      <header className="flex items-center justify-between border-b bg-white px-4 py-2">
        <div className="flex items-center gap-3">
          <a href="/" className="text-gray-400 hover:text-gray-600">
            ←
          </a>
          <h1 className="text-lg font-semibold text-gray-900">
            {project.name}
          </h1>
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
              project.status === "ready"
                ? "bg-green-100 text-green-700"
                : project.status === "error"
                ? "bg-red-100 text-red-700"
                : "bg-blue-100 text-blue-700"
            }`}
          >
            {project.status}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleDeploy("vercel")}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Deploy to Vercel
          </button>
          <button
            onClick={() => handleDeploy("cloudflare")}
            className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Deploy to Cloudflare
          </button>
        </div>
      </header>

      {/* Main Editor Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* File Explorer */}
        <div className="w-60 flex-shrink-0 border-r bg-gray-50 overflow-y-auto">
          <FileExplorer
            files={project.files}
            selectedFile={selectedFile}
            onSelectFile={setSelectedFile}
          />
        </div>

        {/* Code Editor */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-hidden">
            <CodeEditor
              file={selectedFile}
              onChange={(content) => {
                if (selectedFile) {
                  setSelectedFile({ ...selectedFile, content });
                }
              }}
            />
          </div>

          {/* AI Prompt Input */}
          <div className="border-t bg-white p-3">
            <PromptInput
              onGenerate={handleEditWithPrompt}
              isLoading={isEditing}
              placeholder='Edit with AI... e.g., "Add authentication using Google"'
            />
          </div>
        </div>

        {/* Preview Panel */}
        <div className="w-[45%] flex-shrink-0 border-l">
          <PreviewPanel previewUrl={project.preview_url} />
        </div>
      </div>
    </div>
  );
}
