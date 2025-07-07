import { Card } from "@/components/ui/card";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
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

export default function ReportArtifact({ loading, result, error, expandAll = false }: { loading: boolean; result: any; error: string | null; expandAll?: boolean }) {
  const report = result?.final_report || "";
  const sections = report ? splitReportSections(report) : {};
  const sectionKeys = Object.keys(sections);

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

  // Export as PDF (vertical accordion: all sections in order)
  const handleExportPDF = () => {
    if (!report) return;
    const doc = new jsPDF({ unit: "pt", format: "a4" });
    doc.setFont("helvetica", "normal");
    doc.setFontSize(14);
    let y = 40;
    sectionKeys.forEach((key, idx) => {
      if (y > 800) {
        doc.addPage();
        y = 40;
      }
      doc.text(key, 40, y, { maxWidth: 500 });
      y += 24;
      const lines = doc.splitTextToSize(sections[key], 500);
      lines.forEach((line: string) => {
        if (y > 800) {
          doc.addPage();
          y = 40;
        }
        doc.text(line, 40, y);
        y += 18;
      });
      y += 12;
    });
    doc.save("orchestrateai-report.pdf");
  };

  // Accordion defaultValue: open all if expandAll, else none
  const defaultAccordionValue = expandAll ? sectionKeys : [];

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
      {!loading && report && sectionKeys.length > 0 ? (
        <Accordion type="multiple" className="w-full" defaultValue={defaultAccordionValue}>
          {sectionKeys.map((key) => (
            <AccordionItem key={key} value={key} className="mb-2 border border-border rounded-lg bg-background transition-all duration-300">
              <AccordionTrigger className="flex items-center gap-2 px-4 py-2 text-base font-semibold transition-colors duration-300">
                {key}
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4 transition-all duration-300">
                <div className="prose prose-gray max-w-none text-foreground">
                  <ReactMarkdown>{sections[key]}</ReactMarkdown>
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      ) : !loading && !report && !error ? (
        <div className="text-muted-foreground">The final report will appear here.</div>
      ) : null}
    </Card>
  );
} 