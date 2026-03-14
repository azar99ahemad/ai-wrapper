"use client";

import dynamic from "next/dynamic";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center bg-gray-900">
      <p className="text-gray-400">Loading editor...</p>
    </div>
  ),
});

interface ProjectFile {
  id: string;
  path: string;
  content: string;
  version: number;
}

interface CodeEditorProps {
  file: ProjectFile | null;
  onChange?: (content: string) => void;
}

function getLanguage(path: string): string {
  if (path.endsWith(".tsx") || path.endsWith(".ts")) return "typescript";
  if (path.endsWith(".jsx") || path.endsWith(".js")) return "javascript";
  if (path.endsWith(".css")) return "css";
  if (path.endsWith(".json")) return "json";
  if (path.endsWith(".html")) return "html";
  if (path.endsWith(".md")) return "markdown";
  return "plaintext";
}

export function CodeEditor({ file, onChange }: CodeEditorProps) {
  if (!file) {
    return (
      <div className="flex h-full items-center justify-center bg-gray-900">
        <p className="text-gray-400">Select a file to edit</p>
      </div>
    );
  }

  return (
    <div className="h-full">
      {/* File tab */}
      <div className="flex items-center border-b bg-gray-800 px-4 py-1.5">
        <span className="text-sm text-gray-300">{file.path}</span>
        <span className="ml-2 rounded bg-gray-700 px-1.5 py-0.5 text-xs text-gray-400">
          v{file.version}
        </span>
      </div>

      {/* Monaco Editor */}
      <MonacoEditor
        height="calc(100% - 36px)"
        language={getLanguage(file.path)}
        value={file.content}
        theme="vs-dark"
        onChange={(value) => onChange?.(value || "")}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: "on",
          scrollBeyondLastLine: false,
          wordWrap: "on",
          tabSize: 2,
          formatOnPaste: true,
          automaticLayout: true,
        }}
      />
    </div>
  );
}
