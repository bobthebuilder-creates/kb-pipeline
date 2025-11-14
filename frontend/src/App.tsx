import React, { useState } from "react";
import LlmConfigPanel from "./components/LlmConfigPanel";
import InputPathPanel from "./components/InputPathPanel";
import PipelineStatusPanel from "./components/PipelineStatusPanel";

import "./App.css";

function App() {
  const [inputPath, setInputPath] = useState("");

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#111827",
        color: "#e5e7eb",
        padding: "24px",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      <h1 style={{ marginBottom: 8 }}>KB Pipeline Dashboard</h1>
      <p style={{ marginBottom: 24, color: "#9ca3af" }}>
        Configure LLM, choose input path, and run the document → graph-based KB pipeline.
      </p>

      <div
        style={{
          display: "grid",
          gap: 16,
          gridTemplateColumns: "1fr",
          maxWidth: 900,
        }}
      >
        <LlmConfigPanel />
        <InputPathPanel inputPath={inputPath} onChange={setInputPath} />
        <PipelineStatusPanel inputPath={inputPath} />
      </div>
    </div>
  );
}

export default App;
