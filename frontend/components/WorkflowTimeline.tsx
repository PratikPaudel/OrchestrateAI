import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

const AGENT_STEPS = [
  { key: "planner", label: "📝 Planner" },
  { key: "searcher", label: "🔍 Searcher" },
  { key: "summarizer", label: "📖 Summarizer & Reviewer" }, // Updated to match actual workflow
  { key: "writer", label: "✍️ Writer" },
];

function getStepStatus(stepKey: string, stepProgressMap: any, status: string, idx: number) {
  if (stepProgressMap[stepKey]) return "complete";
  // Find the first incomplete step for "inprogress"
  const completedCount = Object.keys(stepProgressMap).length;
  if (idx === completedCount && status === "running") return "inprogress";
  return "pending";
}

export default function WorkflowTimeline({ loading, progress, status, error }: {
  loading: boolean;
  progress: any[];
  status: string;
  error: string | null;
}) {
  // Create a map of step progress, handling both old and new step names
  const stepProgressMap = Object.fromEntries(
    progress.map((p: any) => {
      // Handle the case where backend sends "summarize_and_review" but frontend expects "summarizer"
      const stepKey = p.step === "summarize_and_review" ? "summarizer" : p.step;
      return [stepKey, p];
    })
  );

  return (
    <div className="flex flex-col gap-6">
      {/* Progress Bar / Stepper */}
      <div className="flex items-center justify-between mb-2">
        {AGENT_STEPS.map((step, idx) => {
          const stepStatus = getStepStatus(step.key, stepProgressMap, status, idx);
          return (
            <div key={step.key} className="flex flex-col items-center flex-1">
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center border-2 text-lg font-bold transition-all",
                  stepStatus === "complete" && "bg-green-100 border-green-500 text-green-700",
                  stepStatus === "inprogress" && "bg-blue-100 border-blue-500 text-blue-700 animate-pulse",
                  stepStatus === "pending" && "bg-gray-100 border-gray-300 text-gray-400"
                )}
              >
                {stepStatus === "inprogress" ? <Loader2 className="animate-spin w-5 h-5" /> : idx + 1}
              </div>
              <span className={cn(
                "mt-1 text-xs font-medium text-center",
                stepStatus === "complete" && "text-green-700",
                stepStatus === "inprogress" && "text-blue-700",
                stepStatus === "pending" && "text-gray-400"
              )}>{step.label.replace(/^[^ ]+ /, "")}</span>
            </div>
          );
        })}
      </div>
      
      {/* Connecting lines for stepper */}
      <div className="relative h-2 mb-2">
        <div className="absolute top-1/2 left-4 right-4 h-1 bg-gray-200 rounded-full z-0" />
        <div
          className="absolute top-1/2 left-4 h-1 bg-blue-500 rounded-full z-10 transition-all"
          style={{
            width: `${((Object.keys(stepProgressMap).length) / (AGENT_STEPS.length - 1)) * 100}%` || "0%",
            right: "auto"
          }}
        />
      </div>
      
      {/* Accordion for steps */}
      <Accordion type="multiple" className="w-full">
        {AGENT_STEPS.map((step, idx) => {
          const stepStatus = getStepStatus(step.key, stepProgressMap, status, idx);
          const stepData = stepProgressMap[step.key];
          return (
            <AccordionItem key={step.key} value={step.key} className="mb-2 border border-border rounded-lg bg-background transition-all duration-300">
              <AccordionTrigger className={cn(
                "flex items-center gap-2 px-4 py-2 text-base font-semibold transition-colors duration-300",
                stepStatus === "complete" && "text-green-700",
                stepStatus === "inprogress" && "text-blue-700 animate-pulse",
                stepStatus === "pending" && "text-gray-500"
              )}>
                <span>{step.label}</span>
                {stepStatus === "complete" && <span className="ml-2 text-green-600">✓</span>}
                {stepStatus === "inprogress" && <Loader2 className="ml-2 animate-spin w-4 h-4 text-blue-600" />}
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4 transition-all duration-300">
                {stepStatus === "complete" && stepData && (
                  <div className="text-sm text-gray-800 whitespace-pre-wrap">
                    <b>Status:</b> {stepData.status}<br />
                    {stepData.message && <><b>Message:</b> {stepData.message}<br /></>}
                    {stepData.progress && <><b>Progress:</b> {stepData.progress}%<br /></>}
                  </div>
                )}
                {stepStatus === "inprogress" && (
                  <div className="flex items-center gap-2 text-blue-600 text-sm">
                    <Loader2 className="animate-spin w-4 h-4" />
                    Working on this step...
                  </div>
                )}
                {stepStatus === "pending" && <div className="text-sm text-gray-400">Pending...</div>}
              </AccordionContent>
            </AccordionItem>
          );
        })}
      </Accordion>
      {error && <div className="text-red-500 text-sm mt-2">{error}</div>}
    </div>
  );
}