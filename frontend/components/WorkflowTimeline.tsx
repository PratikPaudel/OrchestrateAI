import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

const AGENT_STEPS = [
  { key: "planner", label: "📝 Planner" },
  { key: "searcher", label: "🔍 Searcher" },
  { key: "summarizer", label: "📖 Summarizer & Reviewer" },
  { key: "writer", label: "✍️ Writer" },
];

function getStepStatus(stepKey: string, stepProgressMap: any, status: string, allSteps: typeof AGENT_STEPS) {
  const stepData = stepProgressMap[stepKey];
  
  // If we have data for this step and it's complete
  if (stepData && stepData.status === "complete") {
    return "complete";
  }
  
  // Find completed steps
  const completedSteps = allSteps.filter(step => 
    stepProgressMap[step.key] && stepProgressMap[step.key].status === "complete"
  );
  
  // Find the current step index
  const stepIndex = allSteps.findIndex(step => step.key === stepKey);
  
  // If not all steps are complete yet, show progression
  if (completedSteps.length < allSteps.length) {
    // If this is the next step to be worked on (right after completed steps)
    if (stepIndex === completedSteps.length) {
      return "inprogress";
    }
  }
  
  return "pending";
}

export default function WorkflowTimeline({ loading, progress, status, error }: {
  loading: boolean;
  progress: any[];
  status: string;
  error: string | null;
}) {
  // Create a map of step progress
  const stepProgressMap = Object.fromEntries(
    progress.map((p: any) => {
      // Handle potential step name mapping if needed
      const stepKey = p.step === "summarize_and_review" ? "summarizer" : p.step;
      return [stepKey, p];
    })
  );

  // Calculate progress percentage
  const completedSteps = AGENT_STEPS.filter(step => 
    stepProgressMap[step.key] && stepProgressMap[step.key].status === "complete"
  );
  const progressPercentage = (completedSteps.length / AGENT_STEPS.length) * 100;

  return (
    <div className="flex flex-col gap-6">
      {/* Progress Bar / Stepper */}
      <div className="flex items-center justify-between mb-2">
        {AGENT_STEPS.map((step, idx) => {
          const stepStatus = getStepStatus(step.key, stepProgressMap, status, AGENT_STEPS);
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
          className="absolute top-1/2 left-4 h-1 bg-blue-500 rounded-full z-10 transition-all duration-300"
          style={{
            width: `calc(${progressPercentage}% - 2rem)`,
            maxWidth: `calc(100% - 2rem)`
          }}
        />
      </div>
      
      {/* Debug info - you can remove this once it's working */}
      <div className="text-xs text-gray-500 p-2 bg-gray-50 rounded">
        <div>Status: {status}</div>
        <div>Completed: {completedSteps.length}/{AGENT_STEPS.length}</div>
        <div>Progress: {progressPercentage.toFixed(1)}%</div>
        <div>Steps: {Object.keys(stepProgressMap).join(", ")}</div>
      </div>
      
      {/* Accordion for steps */}
      <Accordion type="multiple" className="w-full">
        {AGENT_STEPS.map((step, idx) => {
          const stepStatus = getStepStatus(step.key, stepProgressMap, status, AGENT_STEPS);
          const stepData = stepProgressMap[step.key];
          return (
            <AccordionItem key={step.key} value={step.key} className="mb-2 border border-border rounded-lg bg-background transition-all duration-300">
              <AccordionTrigger className={cn(
                "flex items-center gap-2 px-4 py-2 text-base font-semibold transition-colors duration-300",
                stepStatus === "complete" && "text-green-700",
                stepStatus === "inprogress" && "text-blue-700 animate-pulse",
                stepStatus === "pending" && "text-gray-500"
              )}>
                <span className="flex items-center gap-1">
                  {step.label}
                  {stepStatus === "complete" && <span className="text-green-600">✓</span>}
                </span>
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