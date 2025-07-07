import { useEffect, useRef, useState } from "react";

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
      if (data.status === "complete") {
        setStatus("complete");
        if (data.final_report) setFinalReport(data.final_report);
      } else if (data.status === "error") {
        setStatus("error");
        setError(data.message || "Unknown error");
      } else if (data.step) {
        setProgress((prev) => [...prev, data]);
      }
    };

    ws.onerror = () => {
      setStatus("error");
      setError("WebSocket error");
    };

    ws.onclose = () => {
      if (status === "running") setStatus("error");
    };

    return () => {
      ws.close();
    };
    // eslint-disable-next-line
  }, [query]);

  return { progress, status, error, finalReport };
} 