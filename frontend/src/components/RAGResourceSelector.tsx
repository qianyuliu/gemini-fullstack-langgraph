import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Database, X, Plus, AlertCircle, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";

interface RAGResource {
  uri: string;
  title: string;
  description: string;
}

interface RAGResourceSelectorProps {
  selectedResources: string[];
  onResourcesChange: (resources: string[]) => void;
  isEnabled: boolean;
}

export const RAGResourceSelector: React.FC<RAGResourceSelectorProps> = ({
  selectedResources,
  onResourcesChange,
  isEnabled,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [availableResources, setAvailableResources] = useState<RAGResource[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ragConfig, setRagConfig] = useState<any>(null);

  // Fetch RAG configuration when component is enabled
  useEffect(() => {
    if (isEnabled) {
      fetchRAGConfig();
    }
  }, [isEnabled]);

  // Fetch available resources when component is enabled
  useEffect(() => {
    if (isEnabled) {
      fetchResources();
    }
  }, [isEnabled, searchQuery]);

  const fetchRAGConfig = async () => {
    try {
      const apiUrl = import.meta.env.DEV
        ? "http://localhost:2024"
        : "http://localhost:8123";
      
      const response = await fetch(`${apiUrl}/api/rag/config`);
      if (response.ok) {
        const data = await response.json();
        setRagConfig(data);
        console.log("RAG Config:", data);
      } else {
        console.error("Failed to fetch RAG config:", response.status);
      }
    } catch (error) {
      console.error("Error fetching RAG config:", error);
    }
  };

  const fetchResources = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const apiUrl = import.meta.env.DEV
        ? "http://localhost:2024"
        : "http://localhost:8123";
      
      const params = new URLSearchParams();
      if (searchQuery) {
        params.append("query", searchQuery);
      }
      
      console.log(`Fetching RAG resources from: ${apiUrl}/api/rag/resources?${params}`);
      
      const response = await fetch(`${apiUrl}/api/rag/resources?${params}`);
      console.log("RAG resources response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("RAG resources data:", data);
        setAvailableResources(data.resources || []);
      } else {
        const errorText = await response.text();
        console.error("Failed to fetch RAG resources:", response.status, errorText);
        setError(`Failed to fetch resources: ${response.status}`);
      }
    } catch (error) {
      console.error("Error fetching RAG resources:", error);
      setError(`Network error: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResourceToggle = (uri: string) => {
    const newResources = selectedResources.includes(uri)
      ? selectedResources.filter(r => r !== uri)
      : [...selectedResources, uri];
    onResourcesChange(newResources);
  };

  const handleResourceRemove = (uri: string) => {
    onResourcesChange(selectedResources.filter(r => r !== uri));
  };

  const getResourceTitle = (uri: string) => {
    const resource = availableResources.find(r => r.uri === uri);
    return resource?.title || uri;
  };

  // Don't render if RAG is not enabled
  if (!isEnabled) {
    return (
      <div className="flex items-center gap-2 text-sm text-neutral-500">
        <AlertCircle className="h-4 w-4" />
        <span>RAG is not enabled. Configure RAG_PROVIDER in your environment.</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {/* RAG Status */}
      <div className="flex items-center gap-2 text-sm text-neutral-400">
        <Database className="h-4 w-4" />
        <span>RAG Provider: {ragConfig?.provider || 'Unknown'}</span>
      </div>

      {/* Selected Resources */}
      {selectedResources.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedResources.map((uri) => (
            <Badge
              key={uri}
              variant="secondary"
              className="bg-blue-500/20 text-blue-300 border-blue-500/30 px-2 py-1 rounded-md flex items-center gap-1"
            >
              <Database className="h-3 w-3" />
              {getResourceTitle(uri)}
              <Button
                variant="ghost"
                size="sm"
                className="h-4 w-4 p-0 hover:bg-transparent"
                onClick={() => handleResourceRemove(uri)}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          ))}
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 p-2 rounded">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Resource Selector */}
      <Popover>
        <PopoverTrigger>
          <Button
            variant="outline"
            className="bg-neutral-700 border-neutral-600 text-neutral-300 hover:bg-neutral-600 justify-start"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add RAG Resources
            {isLoading && <Loader2 className="h-4 w-4 ml-2 animate-spin" />}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-80 bg-neutral-800 border-neutral-700 text-neutral-300">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              <span className="text-sm font-medium">Select RAG Resources</span>
            </div>
            
            <Input
              placeholder="Search resources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-neutral-700 border-neutral-600 text-neutral-300"
            />
            
            <div className="max-h-60 overflow-y-auto space-y-1">
              {isLoading ? (
                <div className="flex items-center justify-center py-4 text-neutral-500">
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Loading resources...
                </div>
              ) : error ? (
                <div className="text-center py-4 text-red-400">
                  <AlertCircle className="h-4 w-4 mx-auto mb-2" />
                  {error}
                </div>
              ) : availableResources.length === 0 ? (
                <div className="text-center py-4 text-neutral-500">
                  <Database className="h-4 w-4 mx-auto mb-2" />
                  No resources found
                  <div className="text-xs mt-1">
                    Make sure RAGFlow is running and configured
                  </div>
                </div>
              ) : (
                availableResources.map((resource) => (
                  <div
                    key={resource.uri}
                    className="flex items-center gap-2 p-2 rounded hover:bg-neutral-700 cursor-pointer"
                    onClick={() => handleResourceToggle(resource.uri)}
                  >
                    <input
                      type="checkbox"
                      checked={selectedResources.includes(resource.uri)}
                      onChange={() => handleResourceToggle(resource.uri)}
                      className="rounded border-neutral-600 bg-neutral-700"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">
                        {resource.title}
                      </div>
                      {resource.description && (
                        <div className="text-xs text-neutral-500 truncate">
                          {resource.description}
                        </div>
                      )}
                      <div className="text-xs text-neutral-600 truncate">
                        {resource.uri}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
            
            {/* Debug Info */}
            {import.meta.env.DEV && (
              <div className="text-xs text-neutral-600 border-t border-neutral-700 pt-2">
                <div>Debug Info:</div>
                <div>Provider: {ragConfig?.provider || 'N/A'}</div>
                <div>Resources: {availableResources.length}</div>
                <div>Selected: {selectedResources.length}</div>
              </div>
            )}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}; 