import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import ReactMarkdown from "react-markdown";
import { useState } from "react";
// @ts-ignore
import jsPDF from "jspdf";

function splitReportSections(report: string) {
  // Naive split by headings for demo; can be improved
  const sections = {} as Record<string, string>;
  let current = "Overview";
  let buffer = [] as string[];
  report.split(/\n/).forEach(line => {
    const heading = line.match(/^\*\*(.+)\*\*$/);
    if (heading) {
      if (buffer.length) sections[current] = buffer.join("\n");
      current = heading[1].trim();
      buffer = [];
    } else {
      buffer.push(line);
    }
  });
  if (buffer.length) sections[current] = buffer.join("\n");
  return sections;
}

export default function ReportArtifact({ loading, result, error }: { loading: boolean; result: any; error: string | null }) {
  const [activeTab, setActiveTab] = useState<string | undefined>(undefined);
  const report = result?.final_report || "";
  const sections = report ? splitReportSections(report) : {};
  const sectionKeys = Object.keys(sections);
  const firstTab = sectionKeys[0] || "Report";

  // Copy to clipboard
  const handleCopy = () => {
    navigator.clipboard.writeText(report);
  };

  // Export as Markdown
  const handleExportMarkdown = () => {
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "orchestrateai-report.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  // Export as PDF
  const handleExportPDF = () => {
    if (!report) return;
    const doc = new jsPDF({ unit: "pt", format: "a4" });
    const lines = doc.splitTextToSize(report, 500);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);
    let y = 40;
    lines.forEach((line: string) => {
      if (y > 800) {
        doc.addPage();
        y = 40;
      }
      doc.text(line, 40, y);
      y += 18;
    });
    doc.save("orchestrateai-report.pdf");
  };

  return (
    <Card className="p-6 bg-background border border-border shadow-md min-h-[400px] flex flex-col gap-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-bold text-lg">Final Report</h2>
        <div className="flex gap-2">
          <button
            className="text-xs px-3 py-1 rounded bg-muted hover:bg-gray-200 border border-border font-semibold"
            onClick={handleCopy}
            disabled={!report}
          >
            Copy
          </button>
          <button
            className="text-xs px-3 py-1 rounded bg-muted hover:bg-gray-200 border border-border font-semibold"
            onClick={handleExportMarkdown}
            disabled={!report}
          >
            Export Markdown
          </button>
          <button
            className="text-xs px-3 py-1 rounded bg-muted hover:bg-gray-200 border border-border font-semibold"
            onClick={handleExportPDF}
            disabled={!report}
          >
            Export PDF
          </button>
        </div>
      </div>
      {error && <div className="text-red-500">{error}</div>}
      {loading && <div className="text-muted-foreground">Generating report...</div>}
      {!loading && report && sectionKeys.length > 1 ? (
        <Tabs value={activeTab || firstTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="mb-4">
            {sectionKeys.map(key => (
              <TabsTrigger key={key} value={key} className="capitalize">
                {key}
              </TabsTrigger>
            ))}
          </TabsList>
          {sectionKeys.map(key => (
            <TabsContent key={key} value={key} className="prose prose-gray max-w-none text-foreground">
              <ReactMarkdown>{sections[key]}</ReactMarkdown>
            </TabsContent>
          ))}
        </Tabs>
      ) : !loading && report ? (
        <div className="prose prose-gray max-w-none text-foreground">
          <ReactMarkdown>{report}</ReactMarkdown>
        </div>
      ) : !loading && !report && !error ? (
        <div className="text-muted-foreground">The final report will appear here.</div>
      ) : null}
    </Card>
  );
} 