import { useState, useEffect } from "react";

interface UseMCPLogsProps {
  showLogs: boolean;
  viewLogType: "aws" | "docker" | "file" | "none";
  logProfile: string;
  logRegion: string;
  logGroup: string;
  viewDockerContainer: string;
  viewLogFilePath: string;
}

/**
 * Custom hook to manage the SSE (EventSource) log streaming connection.
 * It connects to the log API and buffers the incoming logs.
 *
 * @param props Log configurations and active visibility/type
 * @returns { logs, isFetchingLogs, setLogs }
 */
export function useMCPLogs({
  showLogs,
  viewLogType,
  logProfile,
  logRegion,
  logGroup,
  viewDockerContainer,
  viewLogFilePath,
}: UseMCPLogsProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [isFetchingLogs, setIsFetchingLogs] = useState(false);

  useEffect(() => {
    let eventSource: EventSource;

    let isValid = false;
    if (viewLogType === "aws" && logGroup && logRegion) isValid = true;
    if (viewLogType === "docker" && viewDockerContainer) isValid = true;
    if (viewLogType === "file" && viewLogFilePath) isValid = true;

    if (showLogs && isValid) {
      setLogs([]); // Clear logs when starting a new stream
      setIsFetchingLogs(true);

      const url = `/api/logs?type=${viewLogType}&group=${encodeURIComponent(
        logGroup
      )}&region=${encodeURIComponent(logRegion)}&profile=${encodeURIComponent(
        logProfile
      )}&container=${encodeURIComponent(
        viewDockerContainer
      )}&path=${encodeURIComponent(viewLogFilePath)}`;

      eventSource = new EventSource(url);

      eventSource.onmessage = (event) => {
        setIsFetchingLogs(false);
        try {
          const parsed = JSON.parse(event.data);
          // Keep last 100 logs
          setLogs((prev) => [...prev.slice(-99), parsed.log]);
        } catch (err) {
          console.error("Error parsing log stream", err);
        }
      };

      // Server sends 'done' before closing so we can shut down cleanly,
      // avoiding the EventSource onerror that fires on a server-side stream close
      eventSource.addEventListener("done", () => {
        eventSource.close();
        setIsFetchingLogs(false);
      });

      eventSource.onerror = (error) => {
        // Only fires on a genuine connection error (e.g. network failure),
        // not when the server closes after sending the 'done' event
        console.error("EventSource connection error:", error);
        eventSource.close();
        setIsFetchingLogs(false);
      };
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [
    showLogs,
    viewLogType,
    logGroup,
    logRegion,
    logProfile,
    viewDockerContainer,
    viewLogFilePath,
  ]);

  return {
    logs,
    setLogs,
    isFetchingLogs,
  };
}
