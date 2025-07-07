"use client";
import { useState } from "react";
import QueryInput from "../components/QueryInput";
import WorkflowTimeline from "../components/WorkflowTimeline";
import ReportArtifact from "../components/ReportArtifact";
import { useJobWebSocket } from "../hooks/useJobWebSocket";

// Types for backend response (simplified for now)
type AgentState = {
  query: string;
  plan?: any;
  current_task_index?: number;
  search_results?: any[];
  research_data?: any[];
  final_report?: string;
  error?: string;
};

type ApiResponse = {
  final_report: string;
  state: AgentState;
  error?: string;
};

export default function Home() {
  const [query, setQuery] = useState<string | null>(null);
  const [finalResult, setFinalResult] = useState<ApiResponse | null>(null);
  const { progress, status, error } = useJobWebSocket(query);
  const [loading, setLoading] = useState(false);

  // Fallback: fetch final report when job is complete (simulate for now)
  const handleQuery = async (q: string) => {
    setQuery(q);
    setFinalResult(null);
    setLoading(true);
    // Wait for WebSocket to finish, then fetch final report
    // (In real app, backend should send final report over WebSocket)
    // For now, poll for final report after status is complete
  };

  // Simulate fetching final report after status is complete
  // (Replace with real logic if backend sends final report over WebSocket)
  if (status === "complete" && !finalResult && query && !loading) {
    setLoading(true);
    fetch("http://localhost:8000/api/v1/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })
      .then((res) => res.json())
      .then((data) => setFinalResult(data))
      .finally(() => setLoading(false));
  }

  return (
    <div className="w-full flex flex-col items-center">
      <QueryInput onSubmit={handleQuery} loading={status === "running" || loading} />
      <div className="w-full max-w-7xl flex flex-row gap-8 mt-12">
        {/* Left: Workflow/Chat */}
        <div className="flex-1 min-w-[350px] max-w-[520px] bg-muted rounded-xl p-6 shadow-sm border border-border">
          <WorkflowTimeline
            loading={status === "running" || loading}
            progress={progress}
            status={status}
            error={error}
          />
        </div>
        {/* Right: Report Artifact */}
        <div className="flex-1 min-w-[350px] max-w-[600px]">
          <ReportArtifact loading={loading} result={finalResult} error={finalResult?.error || error} />
        </div>
      </div>
    </div>
  );
}
