"use client";
import { useState } from "react";
import QueryInput from "../components/QueryInput";

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
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (query: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) throw new Error("API error: " + res.status);
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center">
      <QueryInput onSubmit={handleQuery} loading={loading} />
      <div className="w-full max-w-2xl mt-12">
        {/* Workflow progress */}
        <div className="h-24 bg-muted rounded-lg flex items-center justify-center text-muted-foreground">
          {loading && "Research in progress..."}
          {!loading && result && "Workflow progress tracker coming soon..."}
          {!loading && !result && "Workflow progress tracker coming soon..."}
        </div>
        {/* Agent output/results */}
        <div className="mt-8 min-h-48 bg-muted rounded-lg flex flex-col items-center justify-center text-muted-foreground p-6">
          {error && <div className="text-red-500">{error}</div>}
          {loading && <div>Thinking...</div>}
          {!loading && result && (
            <>
              <div className="w-full text-left">
                <h2 className="font-bold text-lg mb-2">Final Report</h2>
                <pre className="whitespace-pre-wrap text-foreground bg-background rounded p-4 overflow-x-auto">
                  {result.final_report}
                </pre>
              </div>
            </>
          )}
          {!loading && !result && !error && (
            <div>Agent output/results will appear here.</div>
          )}
        </div>
      </div>
    </div>
  );
}
