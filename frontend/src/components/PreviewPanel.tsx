"use client";

interface PreviewPanelProps {
  previewUrl: string | null;
}

export function PreviewPanel({ previewUrl }: PreviewPanelProps) {
  return (
    <div className="flex h-full flex-col">
      {/* Preview header */}
      <div className="flex items-center justify-between border-b bg-white px-4 py-2">
        <h3 className="text-sm font-medium text-gray-700">Preview</h3>
        {previewUrl && !previewUrl.startsWith("Sandbox") && (
          <a
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-primary-600 hover:underline"
          >
            Open in new tab ↗
          </a>
        )}
      </div>

      {/* Preview content */}
      <div className="flex-1 bg-white">
        {previewUrl && !previewUrl.startsWith("Sandbox") ? (
          <iframe
            src={previewUrl}
            className="h-full w-full border-0"
            title="Project Preview"
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          />
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="mx-auto h-16 w-16 rounded-full bg-gray-100 flex items-center justify-center">
                <span className="text-2xl">🖥️</span>
              </div>
              <p className="mt-4 text-sm text-gray-500">
                {previewUrl?.startsWith("Sandbox")
                  ? "Sandbox is starting up..."
                  : "Preview will appear here once the project is running"}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
