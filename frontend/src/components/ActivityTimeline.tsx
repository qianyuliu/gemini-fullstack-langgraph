import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Loader2,
  Activity,
  Info,
  Search,
  TextSearch,
  Brain,
  Pen,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

export interface ProcessedEvent {
  title: string;
  data: any;
}

interface ActivityTimelineProps {
  processedEvents: ProcessedEvent[];
  isLoading: boolean;
}

// Markdown components for timeline
const timelineMdComponents = {
  h1: ({ className, children, ...props }: any) => (
    <h1 className="text-sm font-bold mt-2 mb-1 text-neutral-200" {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: any) => (
    <h2 className="text-xs font-semibold mt-1 mb-1 text-neutral-200" {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: any) => (
    <h3 className="text-xs font-medium mt-1 mb-0.5 text-neutral-200" {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: any) => (
    <p className="text-xs text-neutral-300 leading-relaxed mb-1" {...props}>
      {children}
    </p>
  ),
  ul: ({ className, children, ...props }: any) => (
    <ul className="list-disc pl-4 mb-2 text-xs text-neutral-300" {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: any) => (
    <ol className="list-decimal pl-4 mb-2 text-xs text-neutral-300" {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: any) => (
    <li className="mb-0.5 text-xs text-neutral-300" {...props}>
      {children}
    </li>
  ),
  strong: ({ className, children, ...props }: any) => (
    <strong className="font-semibold text-neutral-200" {...props}>
      {children}
    </strong>
  ),
  em: ({ className, children, ...props }: any) => (
    <em className="italic text-neutral-300" {...props}>
      {children}
    </em>
  ),
  code: ({ className, children, ...props }: any) => (
    <code className="bg-neutral-800 rounded px-1 py-0.5 font-mono text-xs text-neutral-300" {...props}>
      {children}
    </code>
  ),
};

export function ActivityTimeline({
  processedEvents,
  isLoading,
}: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] =
    useState<boolean>(false);
  const getEventIcon = (title: string, index: number) => {
    if (index === 0 && isLoading && processedEvents.length === 0) {
      return <Loader2 className="h-4 w-4 text-neutral-400 animate-spin" />;
    }
    if (title.toLowerCase().includes("generating")) {
      return <TextSearch className="h-4 w-4 text-neutral-400" />;
    } else if (title.toLowerCase().includes("thinking")) {
      return <Loader2 className="h-4 w-4 text-neutral-400 animate-spin" />;
    } else if (title.toLowerCase().includes("reflection")) {
      return <Brain className="h-4 w-4 text-neutral-400" />;
    } else if (title.toLowerCase().includes("research")) {
      return <Search className="h-4 w-4 text-neutral-400" />;
    } else if (title.toLowerCase().includes("finalizing")) {
      return <Pen className="h-4 w-4 text-neutral-400" />;
    } else if (title.toLowerCase().includes("planning")) {
      return <Brain className="h-4 w-4 text-blue-400" />;
    } else if (title.toLowerCase().includes("section")) {
      return <Pen className="h-4 w-4 text-green-400" />;
    } else if (title.toLowerCase().includes("compiling")) {
      return <Activity className="h-4 w-4 text-purple-400" />;
    }
    return <Activity className="h-4 w-4 text-neutral-400" />;
  };

  useEffect(() => {
    if (!isLoading && processedEvents.length !== 0) {
      setIsTimelineCollapsed(true);
    }
  }, [isLoading, processedEvents]);

  const renderEventData = (data: any) => {
    if (typeof data === "string") {
      // Check if the string contains markdown-like content
      if (data.includes("**") || data.includes("\n") || data.includes("#")) {
        return (
          <ReactMarkdown components={timelineMdComponents}>
            {data}
          </ReactMarkdown>
        );
      }
      return <p className="text-xs text-neutral-300 leading-relaxed">{data}</p>;
    } else if (Array.isArray(data)) {
      return <p className="text-xs text-neutral-300 leading-relaxed">{(data as string[]).join(", ")}</p>;
    } else {
      return <p className="text-xs text-neutral-300 leading-relaxed">{JSON.stringify(data)}</p>;
    }
  };

  return (
    <Card className="border-none rounded-lg bg-neutral-700 max-h-96">
      <CardHeader>
        <CardDescription className="flex items-center justify-between">
          <div
            className="flex items-center justify-start text-sm w-full cursor-pointer gap-2 text-neutral-100"
            onClick={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
          >
            Research
            {isTimelineCollapsed ? (
              <ChevronDown className="h-4 w-4 mr-2" />
            ) : (
              <ChevronUp className="h-4 w-4 mr-2" />
            )}
          </div>
        </CardDescription>
      </CardHeader>
      {!isTimelineCollapsed && (
        <ScrollArea className="max-h-96 overflow-y-auto">
          <CardContent>
            {isLoading && processedEvents.length === 0 && (
              <div className="relative pl-8 pb-4">
                <div className="absolute left-3 top-3.5 h-full w-0.5 bg-neutral-800" />
                <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-neutral-800 flex items-center justify-center ring-4 ring-neutral-900">
                  <Loader2 className="h-3 w-3 text-neutral-400 animate-spin" />
                </div>
                <div>
                  <p className="text-sm text-neutral-300 font-medium">
                    Searching...
                  </p>
                </div>
              </div>
            )}
            {processedEvents.length > 0 ? (
              <div className="space-y-0">
                {processedEvents.map((eventItem, index) => (
                  <div key={index} className="relative pl-8 pb-4">
                    {index < processedEvents.length - 1 ||
                    (isLoading && index === processedEvents.length - 1) ? (
                      <div className="absolute left-3 top-3.5 h-full w-0.5 bg-neutral-600" />
                    ) : null}
                    <div className="absolute left-0.5 top-2 h-6 w-6 rounded-full bg-neutral-600 flex items-center justify-center ring-4 ring-neutral-700">
                      {getEventIcon(eventItem.title, index)}
                    </div>
                    <div>
                      <p className="text-sm text-neutral-200 font-medium mb-0.5">
                        {eventItem.title}
                      </p>
                      <div className="text-xs text-neutral-300">
                        {renderEventData(eventItem.data)}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && processedEvents.length > 0 && (
                  <div className="relative pl-8 pb-4">
                    <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-neutral-600 flex items-center justify-center ring-4 ring-neutral-700">
                      <Loader2 className="h-3 w-3 text-neutral-400 animate-spin" />
                    </div>
                    <div>
                      <p className="text-sm text-neutral-300 font-medium">
                        Searching...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : !isLoading ? ( // Only show "No activity" if not loading and no events
              <div className="flex flex-col items-center justify-center h-full text-neutral-500 pt-10">
                <Info className="h-6 w-6 mb-3" />
                <p className="text-sm">No activity to display.</p>
                <p className="text-xs text-neutral-600 mt-1">
                  Timeline will update during processing.
                </p>
              </div>
            ) : null}
          </CardContent>
        </ScrollArea>
      )}
    </Card>
  );
}
