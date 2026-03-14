"use client";

import { useEffect, useState } from "react";

interface Project {
  id: string;
  name: string;
  description: string | null;
  prompt: string;
  status: string;
  created_at: string;
}

export function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In production, this would fetch from the API
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-gray-300 bg-white p-12 text-center">
        <p className="text-gray-500">
          No projects yet. Generate your first project above!
        </p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="mb-4 text-lg font-semibold text-gray-900">
        Recent Projects
      </h3>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <a
            key={project.id}
            href={`/project/${project.id}`}
            className="rounded-xl border bg-white p-5 transition-shadow hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">{project.name}</h4>
              <StatusBadge status={project.status} />
            </div>
            <p className="mt-2 line-clamp-2 text-sm text-gray-600">
              {project.description || project.prompt}
            </p>
            <p className="mt-3 text-xs text-gray-400">
              {new Date(project.created_at).toLocaleDateString()}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-700",
    generating: "bg-blue-100 text-blue-700",
    ready: "bg-green-100 text-green-700",
    error: "bg-red-100 text-red-700",
    deployed: "bg-purple-100 text-purple-700",
  };

  return (
    <span
      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
        colors[status] || "bg-gray-100 text-gray-700"
      }`}
    >
      {status}
    </span>
  );
}
