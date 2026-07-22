export type Route = "sql" | "rag" | "hybrid";

export interface SqlResult {
  rows: Record<string, unknown>[];
  row_count: number;
  columns: string[];
}

export interface DocChunk {
  source: string;
  text: string;
  score?: number;
}

export interface PlotlyChartData {
  data: Record<string, unknown>[];
  layout: Record<string, unknown>;
}

export interface AskResponse {
  question: string;
  route: Route;
  sql_query: string | null;
  sql_result: SqlResult | null;
  doc_chunks: DocChunk[];
  final_answer: string;
  chart_data: PlotlyChartData | null;
  error: string | null;
}

export interface AskRequest {
  question: string;
  route?: Route;
}

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function getBackendUrl(): string {
  return (
    process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "") ||
    "http://localhost:8000"
  );
}

export async function askQuestion(payload: AskRequest): Promise<AskResponse> {
  let res: Response;
  try {
    res = await fetch(`${getBackendUrl()}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ApiError(
      `Cannot reach backend at ${getBackendUrl()}. Is it running?`
    );
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* response wasn't JSON, keep statusText */
    }
    throw new ApiError(`Backend error (${res.status}): ${detail}`, res.status);
  }

  return res.json();
}

export interface UploadStructuredResponse {
  table_name: string;
  row_count: number;
  columns: { name: string; type: string }[];
}

async function uploadFile<T>(
  endpoint: string,
  file: File,
  fallbackMessage: string
): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  let res: Response;
  try {
    res = await fetch(`${getBackendUrl()}${endpoint}`, {
      method: "POST",
      body: form,
    });
  } catch {
    throw new ApiError(
      `Cannot reach backend at ${getBackendUrl()}. Is it running?`
    );
  }
  if (!res.ok) {
    let detail = fallbackMessage;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      detail = res.statusText || detail;
    }
    throw new ApiError(`Backend error (${res.status}): ${detail}`, res.status);
  }
  return res.json();
}

export async function uploadStructured(
  file: File
): Promise<UploadStructuredResponse> {
  return uploadFile<UploadStructuredResponse>(
    "/upload/structured",
    file,
    "Structured upload failed"
  );
}

export interface UploadDocumentResponse {
  source: string;
  chunks_ingested: number;
}

export async function uploadDocument(
  file: File
): Promise<UploadDocumentResponse> {
  return uploadFile<UploadDocumentResponse>(
    "/upload/document",
    file,
    "Document upload failed"
  );
}

export interface SourcesResponse {
  tables: string[];
  documents: string[];
}

export async function fetchSources(): Promise<SourcesResponse> {
  let res: Response;
  try {
    res = await fetch(`${getBackendUrl()}/sources`);
  } catch {
    throw new ApiError(
      `Cannot reach backend at ${getBackendUrl()}. Is it running?`
    );
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* keep statusText */
    }
    throw new ApiError(`Backend error (${res.status}): ${detail}`, res.status);
  }
  return res.json();
}
