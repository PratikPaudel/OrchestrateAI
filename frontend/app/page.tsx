"use client";
import { useState } from "react";
import QueryInput from "../components/QueryInput";
import WorkflowTimeline from "../components/WorkflowTimeline";
import ReportArtifact from "../components/ReportArtifact";
import { useJobWebSocket } from "../hooks/useJobWebSocket";
import ReportSkeleton from "../components/ReportSkeleton";

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
  const [hasSearched, setHasSearched] = useState(false);
  const { progress, status, error, finalReport } = useJobWebSocket(query);
  const loading = status === "running";

  const handleQuery = (q: string) => {
    setQuery(q);
    setHasSearched(true);
  };

  return (
    <div className="w-full min-h-screen flex flex-col items-center bg-background">
      {/* Animated search bar: slightly above center if not searched, sticky top if searched */}
      <div
        className={
          hasSearched
            ? "w-full flex justify-center sticky top-0 z-20 bg-background pt-8 pb-6 transition-all duration-700 ease-in-out"
            : "w-full flex justify-center items-start transition-all duration-700 ease-in-out"
        }
        style={{ minHeight: hasSearched ? undefined : "60vh", marginTop: hasSearched ? undefined : "20vh" }}
      >
        <div className="w-full max-w-2xl">
          <QueryInput onSubmit={handleQuery} loading={loading} />
        </div>
      </div>
      {/* Main content area: only show after search */}
      {hasSearched && (
        <div className="w-full max-w-7xl flex flex-row gap-8 mt-2 flex-1 items-start">
          {/* Left: Workflow/Chat */}
          <div className="flex-1 min-w-[350px] max-w-[520px] bg-muted rounded-xl p-6 shadow-sm border border-border">
            <WorkflowTimeline
              loading={loading}
              progress={progress}
              status={status}
              error={error}
            />
          </div>
          {/* Right: Report Artifact or Skeleton */}
          <div className="flex-1 min-w-[350px] max-w-[600px]">
            {loading ? (
              <ReportSkeleton />
            ) : (
              <ReportArtifact
                loading={loading}
                result={finalReport ? { final_report: finalReport } : null}
                error={error}
                expandAll={true}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
