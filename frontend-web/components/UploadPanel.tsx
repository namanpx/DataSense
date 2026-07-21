"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiError,
  fetchSources,
  uploadDocument,
  uploadStructured,
  type SourcesResponse,
  type UploadDocumentResponse,
  type UploadStructuredResponse,
} from "@/lib/api";

type DropzoneState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: UploadStructuredResponse | UploadDocumentResponse }
  | { status: "error"; message: string };

function Dropzone({
  label,
  accept,
  icon,
  onUpload,
  resultKey,
}: {
  label: string;
  accept: string;
  icon: "upload" | "clipboard";
  onUpload: (file: File) => Promise<UploadStructuredResponse | UploadDocumentResponse>;
  resultKey: "structured" | "document";
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<DropzoneState>({ status: "idle" });
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback(
    async (file: File | undefined) => {
      if (!file) return;
      setState({ status: "loading" });
      try {
        const data = await onUpload(file);
        setState({ status: "success", data });
      } catch (err) {
        const message =
          err instanceof ApiError ? err.message : "Upload failed unexpectedly.";
        setState({ status: "error", message });
      }
    },
    [onUpload]
  );

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  }

  return (
    <div
      className={`glass-panel flex flex-1 flex-col p-5 transition-colors ${
        dragOver ? "border-cyan/40 bg-cyan/5" : ""
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
    >
      <div className="mb-4 flex items-center gap-2">
        {icon === "upload" ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-cyan">
            <path
              d="M12 16V4m0 0l-4 4m4-4l4 4M4 20h16"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-cyan">
            <path
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
        <span className="font-mono text-label-caps uppercase tracking-widest text-on-surface">
          {label}
        </span>
      </div>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={state.status === "loading"}
        className="flex flex-1 flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-white/10 px-4 py-10 transition hover:border-cyan/30 hover:bg-white/[0.02] disabled:opacity-50"
      >
        {state.status === "loading" ? (
          <span className="font-mono text-terminal-log text-cyan animate-pulse-cyan">
            uploading...
          </span>
        ) : (
          <>
            <span className="font-mono text-terminal-code text-outline">
              drag &amp; drop or click to browse
            </span>
            <span className="font-mono text-label-caps uppercase text-outline/60">
              {accept}
            </span>
          </>
        )}
      </button>

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />

      {state.status === "success" && resultKey === "structured" && (
        <div className="mt-4 font-mono text-terminal-log text-primary">
          <div>[ok] table: {(state.data as UploadStructuredResponse).table_name}</div>
          <div>rows: {(state.data as UploadStructuredResponse).row_count}</div>
          <div className="mt-1 text-outline">
            columns:{" "}
            {(state.data as UploadStructuredResponse).columns
              .map((c) => c.name)
              .join(", ")}
          </div>
        </div>
      )}

      {state.status === "success" && resultKey === "document" && (
        <div className="mt-4 font-mono text-terminal-log text-primary">
          <div>[ok] source: {(state.data as UploadDocumentResponse).source}</div>
          <div>
            chunks ingested: {(state.data as UploadDocumentResponse).chunks_ingested}
          </div>
        </div>
      )}

      {state.status === "error" && (
        <div className="mt-4 font-mono text-terminal-log text-error">
          [error] {state.message}
        </div>
      )}
    </div>
  );
}

export default function UploadPanel() {
  const [sources, setSources] = useState<SourcesResponse | null>(null);
  const [sourcesError, setSourcesError] = useState<string | null>(null);

  useEffect(() => {
    fetchSources()
      .then(setSources)
      .catch((err) =>
        setSourcesError(err instanceof ApiError ? err.message : "Failed to load sources")
      );
  }, []);

  return (
    <div className="flex flex-1 flex-col gap-6 overflow-y-auto pb-4">
      <div className="flex flex-col gap-4 md:flex-row">
        <Dropzone
          label="Upload Structured Data"
          accept=".csv"
          icon="upload"
          resultKey="structured"
          onUpload={uploadStructured}
        />
        <Dropzone
          label="Upload Knowledge Doc"
          accept=".txt,.md,.pdf"
          icon="clipboard"
          resultKey="document"
          onUpload={uploadDocument}
        />
      </div>

      <div className="glass-panel p-5">
        <div className="mb-3 font-mono text-label-caps uppercase tracking-widest text-outline">
          Active Sources
        </div>
        {sourcesError && (
          <div className="font-mono text-terminal-log text-error">{sourcesError}</div>
        )}
        {sources && (
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <div className="mb-2 font-mono text-label-caps uppercase text-cyan">
                DuckDB Tables
              </div>
              {sources.tables.length === 0 ? (
                <div className="font-mono text-terminal-log text-outline">none</div>
              ) : (
                <ul className="space-y-1 font-mono text-terminal-log text-on-surface-variant">
                  {sources.tables.map((t) => (
                    <li key={t}>[table] {t}</li>
                  ))}
                </ul>
              )}
            </div>
            <div>
              <div className="mb-2 font-mono text-label-caps uppercase text-cyan">
                Documents
              </div>
              {sources.documents.length === 0 ? (
                <div className="font-mono text-terminal-log text-outline">none</div>
              ) : (
                <ul className="space-y-1 font-mono text-terminal-log text-on-surface-variant">
                  {sources.documents.map((d) => (
                    <li key={d}>[doc] {d}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
