import { Skeleton } from "@/components/ui/skeleton";

export default function ReportSkeleton() {
  return (
    <div className="p-6 bg-background border border-border shadow-md min-h-[400px] flex flex-col gap-4 rounded-xl">
      <div className="flex items-center justify-between mb-2">
        <Skeleton className="h-6 w-32 rounded" />
        <div className="flex gap-2">
          <Skeleton className="h-6 w-16 rounded" />
          <Skeleton className="h-6 w-28 rounded" />
          <Skeleton className="h-6 w-24 rounded" />
        </div>
      </div>
      <div className="flex gap-2 mb-4">
        <Skeleton className="h-8 w-32 rounded" />
        <Skeleton className="h-8 w-40 rounded" />
        <Skeleton className="h-8 w-28 rounded" />
      </div>
      <Skeleton className="h-64 w-full rounded" />
    </div>
  );
} 