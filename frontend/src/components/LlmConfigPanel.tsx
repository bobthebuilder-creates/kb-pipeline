import React, { useEffect, useState } from "react";
import {
  getLlmStatus,
  setLlmConfig,
  getOllamaModels,
  LlmMode,
} from "../api";

interface Props {}

const LlmConfigPanel: React.FC<Props> = () => {
  const [mode, setMode] = useState<LlmMode>("ollama");
  const [baseUrl, setBaseUrl] = useState("");
  const [modelName, setModelName] = useState("");
  const [models, setModels] = useState<string[]>([]);
  const [clientInitialized, setClientInitialized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const status = await getLlmStatus();
        setMode(status.mode);
        setBaseUrl(status.base_url ?? "");
        setModelName(status.model_name ?? "");
        setClientInitialized(status.client_initialized);
        setError(null);
      } catch (e: any) {
        setError(e.message);
      }
    })();
  }, []);

  const handleSave = async () => {
    try {
      setLoading(true);
      setStatusMessage(null);
      setError(null);
      await setLlmConfig({
        mode,
        base_url: baseUrl || undefined,
        model_name: modelName || undefined,
      });
      const status = await getLlmStatus();
      setClientInitialized(status.client_initialized);
      setStatusMessage("LLM configuration updated.");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadModels = async () => {
    try {
      setLoading(true);
      setStatusMessage(null);
      setError(null);
      const m = await getOllamaModels();
      setModels(m);
      setStatusMessage(`Loaded ${m.length} models from Ollama.`);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, marginBottom: 16 }}>
      <h2>LLM Configuration</h2>

      <div style={{ marginBottom: 8 }}>
        <strong>Mode:</strong>
        <div>
          <label style={{ marginRight: 12 }}>
            <input
              type="radio"
              name="llmMode"
              value="ollama"
              checked={mode === "ollama"}
              onChange={() => setMode("ollama")}
            />
            Ollama (auto / local)
          </label>
          <label>
            <input
              type="radio"
              name="llmMode"
              value="custom"
              checked={mode === "custom"}
              onChange={() => setMode("custom")}
            />
            Custom endpoint
          </label>
        </div>
      </div>

      <div style={{ marginBottom: 8 }}>
        <label>
          Base URL:&nbsp;
          <input
            type="text"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            style={{ width: "100%" }}
            placeholder={mode === "ollama" ? "http://localhost:11434" : "http://my-llm:8000"}
          />
        </label>
      </div>

      <div style={{ marginBottom: 8 }}>
        <label>
          Model name:&nbsp;
          <input
            type="text"
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            style={{ width: "100%" }}
            placeholder={mode === "ollama" ? "llama3" : "optional/custom"}
          />
        </label>
      </div>

      <div style={{ marginBottom: 8 }}>
        <button onClick={handleSave} disabled={loading}>
          {loading ? "Saving..." : "Save LLM Config"}
        </button>

        {mode === "ollama" && (
          <button
            style={{ marginLeft: 8 }}
            onClick={handleLoadModels}
            disabled={loading}
          >
            {loading ? "Loading..." : "Load Ollama Models"}
          </button>
        )}
      </div>

      <div style={{ fontSize: 12 }}>
        <div>Client initialized: {clientInitialized ? "✅ yes" : "❌ no"}</div>
      </div>

      {statusMessage && (
        <div style={{ color: "lightgreen", marginTop: 4 }}>{statusMessage}</div>
      )}
      {error && (
        <div style={{ color: "salmon", marginTop: 4 }}>Error: {error}</div>
      )}

      {models.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <strong>Available models:</strong>
          <ul>
            {models.map((m) => (
              <li key={m}>
                <button
                  type="button"
                  onClick={() => setModelName(m)}
                  style={{ marginRight: 4 }}
                >
                  Use
                </button>
                {m}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LlmConfigPanel;
