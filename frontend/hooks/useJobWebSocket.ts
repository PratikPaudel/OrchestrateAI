import { useEffect, useRef, useState } from "react";

const EXPECTED_STEPS = ["planner", "searcher", "summarizer", "writer"];

export function useJobWebSocket(query: string | null) {
  const [progress, setProgress] = useState<any[]>([]);
  const [status, setStatus] = useState<"idle" | "running" | "complete" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [finalReport, setFinalReport] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!query) return;
    setProgress([]);
    setStatus("running");
    setError(null);
    setFinalReport(null);

    const ws = new WebSocket("ws://localhost:8000/api/v1/ws/jobs");
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ query }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("[WebSocket] Received:", data);
      
      // Handle final completion message (when the job is fully done)
      if (data.status === "complete" && data.final_report) {
        setStatus("complete");
        setFinalReport(data.final_report);
        return;
      }
      
      // Handle error messages
      if (data.status === "error") {
        setStatus("error");
        setError(data.message || "Unknown error");
        return;
      }
      
      // Handle step progress updates
      if (data.step) {
        setProgress((prev) => {
          const idx = prev.findIndex((p) => p.step === data.step);
          let newProgress;
          if (idx !== -1) {
            newProgress = [...prev];
            newProgress[idx] = data;
          } else {
            newProgress = [...prev, data];
          }
          
          // Check if all steps are complete
          const stepMap = Object.fromEntries(
            newProgress.map(p => [p.step === "summarize_and_review" ? "summarizer" : p.step, p])
          );
          
          const allStepsComplete = EXPECTED_STEPS.every(
            step => stepMap[step] && stepMap[step].status === "complete"
          );
          
          // Only set to complete if we have all steps and no final_report message is expected
          if (allStepsComplete && !data.final_report) {
            setTimeout(() => setStatus("complete"), 100); // Small delay to ensure UI updates
          }
          
          return newProgress;
        });
        console.log("[WebSocket] Progress update:", data);
      }
    };

    ws.onerror = (e) => {
      setStatus("error");
      setError("WebSocket error");
      console.error("[WebSocket] Error:", e);
    };

    ws.onclose = () => {
      // Only set error if we were still running (unexpected close)
      if (status === "running") {
        setStatus("error");
        setError("Connection closed unexpectedly");
      }
      console.log("[WebSocket] Connection closed");
    };

    return () => {
      ws.close();
    };
    // eslint-disable-next-line
  }, [query]);

  return { progress, status, error, finalReport };
}