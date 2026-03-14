"use client";

interface ProjectFile {
  id: string;
  path: string;
  content: string;
  version: number;
}

interface FileExplorerProps {
  files: ProjectFile[];
  selectedFile: ProjectFile | null;
  onSelectFile: (file: ProjectFile) => void;
}

interface TreeNode {
  name: string;
  path: string;
  file?: ProjectFile;
  children: TreeNode[];
}

function buildTree(files: ProjectFile[]): TreeNode[] {
  const root: TreeNode[] = [];

  for (const file of files) {
    const parts = file.path.split("/");
    let current = root;

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isFile = i === parts.length - 1;
      const path = parts.slice(0, i + 1).join("/");

      let existing = current.find((n) => n.name === part);
      if (!existing) {
        existing = {
          name: part,
          path,
          file: isFile ? file : undefined,
          children: [],
        };
        current.push(existing);
      }
      if (!isFile) {
        current = existing.children;
      }
    }
  }

  // Sort: directories first, then files, alphabetically
  const sortNodes = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.sort((a, b) => {
      const aIsDir = a.children.length > 0 || !a.file;
      const bIsDir = b.children.length > 0 || !b.file;
      if (aIsDir && !bIsDir) return -1;
      if (!aIsDir && bIsDir) return 1;
      return a.name.localeCompare(b.name);
    });
  };

  const sortTree = (nodes: TreeNode[]): TreeNode[] => {
    return sortNodes(nodes).map((node) => ({
      ...node,
      children: sortTree(node.children),
    }));
  };

  return sortTree(root);
}

function getFileIcon(name: string): string {
  if (name.endsWith(".tsx") || name.endsWith(".ts")) return "📘";
  if (name.endsWith(".jsx") || name.endsWith(".js")) return "📙";
  if (name.endsWith(".css")) return "🎨";
  if (name.endsWith(".json")) return "📋";
  if (name.endsWith(".md")) return "📝";
  if (name.endsWith(".html")) return "🌐";
  return "📄";
}

function TreeNodeComponent({
  node,
  selectedFile,
  onSelectFile,
  depth = 0,
}: {
  node: TreeNode;
  selectedFile: ProjectFile | null;
  onSelectFile: (file: ProjectFile) => void;
  depth?: number;
}) {
  const isDir = node.children.length > 0 || !node.file;
  const isSelected = selectedFile?.path === node.path;

  return (
    <div>
      <button
        className={`flex w-full items-center gap-1.5 px-2 py-1 text-left text-sm hover:bg-gray-200 ${
          isSelected ? "bg-primary-100 text-primary-700" : "text-gray-700"
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => {
          if (node.file) onSelectFile(node.file);
        }}
      >
        <span className="flex-shrink-0 text-xs">
          {isDir ? "📁" : getFileIcon(node.name)}
        </span>
        <span className="truncate">{node.name}</span>
      </button>
      {isDir &&
        node.children.map((child) => (
          <TreeNodeComponent
            key={child.path}
            node={child}
            selectedFile={selectedFile}
            onSelectFile={onSelectFile}
            depth={depth + 1}
          />
        ))}
    </div>
  );
}

export function FileExplorer({
  files,
  selectedFile,
  onSelectFile,
}: FileExplorerProps) {
  const tree = buildTree(files);

  return (
    <div className="py-2">
      <div className="px-3 py-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          Files ({files.length})
        </h3>
      </div>
      <div>
        {tree.map((node) => (
          <TreeNodeComponent
            key={node.path}
            node={node}
            selectedFile={selectedFile}
            onSelectFile={onSelectFile}
          />
        ))}
      </div>
    </div>
  );
}
