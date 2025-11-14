import React, { useEffect, useState } from "react";
import { runPipeline, getPipelineStatus, PipelineStatus } from "../api";

interface Props {
  inputPath: string;
}

const POLL_INTERVAL_MS = 2000;

const PipelineStatusPanel: React.FC<Props> = ({ inputPath }) => {
  const [currentJob, setCurrentJob] = useState<PipelineStatus | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [indexingMethod] = useState("standard");

  useEffect(() => {
    if (!currentJob) return;

    if (currentJob.status === "completed" || currentJob.status === "failed") {
      setPolling(false);
      return;
    }

    setPolling(true);
    const jobId = currentJob.job_id;

    const interval = setInterval(async () => {
      try {
        const status = await getPipelineStatus(jobId);
        setCurrentJob(status);
      } catch (e: any) {
        setError(e.message);
        setPolling(false);
        clearInterval(interval);
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [currentJob]);

  const handleRun = async () => {
    try {
      setError(null);
      if (!inputPath) {
        setError("Input path is required.");
        return;
      }
      const job = await runPipeline(inputPath, indexingMethod);
      setCurrentJob(job);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const progressPercent = currentJob ? Math.round(currentJob.progress * 100) : 0;

  return (
    <div style={{ border: "1px solid #444", borderRadius: 8, padding: 16, marginBottom: 16 }}>
      <h2>Pipeline Run & Status</h2>

      <button onClick={handleRun} disabled={!inputPath || (currentJob && currentJob.status === "running")}>
        {currentJob && currentJob.status === "running" ? "Pipeline Running..." : "Run Pipeline"}
      </button>

      {error && (
        <div style={{ color: "salmon", marginTop: 8 }}>Error: {error}</div>
      )}

      {currentJob && (
        <div style={{ marginTop: 12 }}>
          <div>
            <strong>Job ID:</strong> {currentJob.job_id}
          </div>
          <div>
            <strong>Status:</strong> {currentJob.status}
          </div>
          <div>
            <strong>Stage:</strong> {currentJob.stage ?? "-"}
          </div>
          <div>
            <strong>Progress:</strong> {progressPercent}%
          </div>
          <div>
            <strong>Message:</strong> {currentJob.message ?? "-"}
          </div>

          <div
            style={{
              marginTop: 8,
              width: "100%",
              background: "#222",
              borderRadius: 4,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${progressPercent}%`,
                height: 8,
                background: "#4ade80",
                transition: "width 0.3s ease",
              }}
            />
          </div>
        </div>
      )}

      {polling && (
        <div style={{ marginTop: 8, fontSize: 12 }}>Polling job status...</div>
      )}
    </div>
  );
};

export default PipelineStatusPanel;
