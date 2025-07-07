"use client";
import { useState } from "react";

type QueryInputProps = {
  onSubmit: (query: string) => void;
  loading?: boolean;
};

const QueryInput = ({ onSubmit, loading }: QueryInputProps) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl flex gap-2 mt-8">
      <input
        type="text"
        className="flex-1 px-4 py-3 rounded-lg border border-border bg-background text-foreground text-lg focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
        placeholder="Enter your research query..."
        value={query}
        onChange={e => setQuery(e.target.value)}
        disabled={loading}
      />
      <button
        type="submit"
        className="px-6 py-3 rounded-lg bg-primary text-background font-semibold text-lg disabled:opacity-60 transition"
        disabled={loading || !query.trim()}
      >
        {loading ? "Thinking..." : "Research"}
      </button>
    </form>
  );
};

export default QueryInput; 