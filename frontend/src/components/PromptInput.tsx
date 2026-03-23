"use client";

import { useState } from "react";

interface PromptInputProps {
  onGenerate: (prompt: string) => Promise<void>;
  isLoading?: boolean;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export function PromptInput({
  onGenerate,
  isLoading = false,
  placeholder = 'Describe the web application you want to build... e.g., "Build a job portal with admin panel and salary filter"',
  value: controlledValue,
  onChange: controlledOnChange,
}: PromptInputProps) {
  const [internalValue, setInternalValue] = useState("");
  const prompt = controlledValue !== undefined ? controlledValue : internalValue;
  const setPrompt = controlledOnChange || setInternalValue;

  const handleSubmit = async () => {
    if (!prompt.trim() || isLoading) return;
    await onGenerate(prompt.trim());
  };

  return (
    <div className="relative mx-auto max-w-2xl">
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder={placeholder}
        rows={3}
        className="w-full resize-none rounded-xl border border-gray-300 bg-white px-4 py-3 pr-24 text-gray-900 shadow-sm placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
            handleSubmit();
          }
        }}
        disabled={isLoading}
      />
      <button
        onClick={handleSubmit}
        disabled={!prompt.trim() || isLoading}
        className="absolute bottom-3 right-3 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <svg
              className="h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Generating...
          </span>
        ) : (
          "Generate →"
        )}
      </button>
    </div>
  );
}
