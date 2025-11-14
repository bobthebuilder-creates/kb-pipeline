const API_BASE = "http://localhost:7777";

export type LlmMode = "ollama" | "custom";

export interface LlmStatus {
  mode: LlmMode;
  base_url: string | null;
  model_name: string | null;
  client_initialized: boolean;
}

export interface LlmConfigRequest {
  mode?: LlmMode;
  base_url?: string;
  model_name?: string;
}

export interface PipelineStatus {
  job_id: string;
  status: "pending" | "running" | "failed" | "completed";
  stage: string | null;
  progress: number;
  message: string | null;
  started_at: number;
  finished_at: number | null;
}

export async function getLlmStatus(): Promise<LlmStatus> {
  const res = await fetch(`${API_BASE}/api/llm/status`);
  if (!res.ok) throw new Error(`LLM status error: ${res.status}`);
  return res.json();
}

export async function setLlmConfig(body: LlmConfigRequest): Promise<void> {
  const res = await fetch(`${API_BASE}/api/llm/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`LLM config error: ${res.status} ${text}`);
  }
}

export async function getOllamaModels(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/llm/models`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Ollama models error: ${res.status} ${text}`);
  }
  const data = await res.json();
  return data.models ?? [];
}

export async function runPipeline(inputPath: string, indexingMethod = "standard"): Promise<PipelineStatus> {
  const res = await fetch(`${API_BASE}/api/pipeline/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input_path: inputPath, indexing_method: indexingMethod }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Pipeline run error: ${res.status} ${text}`);
  }
  return res.json();
}

export async function getPipelineStatus(jobId: string): Promise<PipelineStatus> {
  const res = await fetch(`${API_BASE}/api/pipeline/status/${jobId}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Pipeline status error: ${res.status} ${text}`);
  }
  return res.json();
}
