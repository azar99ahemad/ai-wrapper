"use client";

import { useState } from "react";
import { PromptInput } from "@/components/PromptInput";
import { ProjectList } from "@/components/ProjectList";

export default function Home() {
  const [isGenerating, setIsGenerating] = useState(false);

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600">
                <span className="text-lg font-bold text-white">A</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">AI Wrapper</h1>
            </div>
            <nav className="flex items-center gap-4">
              <a
                href="/dashboard"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Dashboard
              </a>
              <button className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
                Sign In
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="mx-auto max-w-4xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <h2 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          Build web apps with{" "}
          <span className="text-primary-600">natural language</span>
        </h2>
        <p className="mt-4 text-lg text-gray-600">
          Describe your application and let AI generate a complete, deployable
          web project. Edit with prompts, preview in real-time, and deploy with
          one click.
        </p>

        {/* Main Prompt Input */}
        <div className="mt-10">
          <PromptInput
            onGenerate={async (prompt) => {
              setIsGenerating(true);
              try {
                const response = await fetch(
                  "http://localhost:8000/api/projects/generate",
                  {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt }),
                  }
                );
                if (response.ok) {
                  const project = await response.json();
                  window.location.href = `/project/${project.id}`;
                }
              } catch (error) {
                console.error("Generation failed:", error);
              } finally {
                setIsGenerating(false);
              }
            }}
            isLoading={isGenerating}
          />
        </div>

        {/* Example Prompts */}
        <div className="mt-8">
          <p className="text-sm font-medium text-gray-500">Try an example:</p>
          <div className="mt-3 flex flex-wrap justify-center gap-2">
            {[
              "Build a job portal with admin panel and salary filter",
              "Create a todo app with authentication",
              "Build a blog with markdown support",
              "Create a dashboard with charts and analytics",
            ].map((example) => (
              <button
                key={example}
                className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-600 hover:border-primary-300 hover:text-primary-600"
                onClick={() => {
                  const input = document.querySelector<HTMLTextAreaElement>(
                    "textarea"
                  );
                  if (input) {
                    input.value = example;
                    input.dispatchEvent(new Event("input", { bubbles: true }));
                  }
                }}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-3">
          <div className="rounded-xl border bg-white p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
              <span className="text-lg">🤖</span>
            </div>
            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              AI-Powered Generation
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Multi-agent pipeline converts your prompt into a complete project
              with specification, architecture, and code.
            </p>
          </div>
          <div className="rounded-xl border bg-white p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100">
              <span className="text-lg">👁️</span>
            </div>
            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              Live Preview
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              See your application running in real-time with an isolated Docker
              sandbox. Edit and watch changes instantly.
            </p>
          </div>
          <div className="rounded-xl border bg-white p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100">
              <span className="text-lg">🚀</span>
            </div>
            <h3 className="mt-4 text-lg font-semibold text-gray-900">
              One-Click Deploy
            </h3>
            <p className="mt-2 text-sm text-gray-600">
              Deploy your generated project to Vercel, Cloudflare, or AWS with a
              single click.
            </p>
          </div>
        </div>
      </section>

      {/* Recent Projects */}
      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <ProjectList />
      </section>
    </main>
  );
}
