import React from "react";

interface LogsPanelProps {
  showLogs: boolean;
  activeLogServerName: string | null;
  onCloseLogs: () => void;
  viewLogType: "aws" | "docker" | "file" | "none";
  setViewLogType: (val: "aws" | "docker" | "file" | "none") => void;
  logProfile: string;
  setLogProfile: (val: string) => void;
  logRegion: string;
  setLogRegion: (val: string) => void;
  logGroup: string;
  setLogGroup: (val: string) => void;
  viewDockerContainer: string;
  setViewDockerContainer: (val: string) => void;
  viewLogFilePath: string;
  setViewLogFilePath: (val: string) => void;
  logs: string[];
}

/**
 * LogsPanel renders a section displaying real-time or historical logs
 * of a chosen server configuration. It supports log streaming config
 * for AWS CloudWatch, Docker containers, or local files.
 */
export function LogsPanel({
  showLogs,
  activeLogServerName,
  onCloseLogs,
  viewLogType,
  setViewLogType,
  logProfile,
  setLogProfile,
  logRegion,
  setLogRegion,
  logGroup,
  setLogGroup,
  viewDockerContainer,
  setViewDockerContainer,
  viewLogFilePath,
  setViewLogFilePath,
  logs,
}: LogsPanelProps) {
  if (!showLogs) return null;

  return (
    <div
      id="server-logs-section"
      className="bg-white border rounded-md p-6 mb-8 shadow-sm"
    >
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-2">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5 mr-2 text-gray-700"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Server Logs
          </h2>
          <button
            onClick={onCloseLogs}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            title="Close logs"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
          <select
            value={viewLogType}
            onChange={(e) => setViewLogType(e.target.value as any)}
            className="px-2 py-1.5 border rounded-md text-sm bg-white"
          >
            <option value="aws">AWS CloudWatch</option>
            <option value="docker">Docker Container</option>
            <option value="file">Local File</option>
          </select>
        </div>
        <div className="flex flex-wrap gap-2 w-full sm:w-auto">
          {viewLogType === "aws" && (
            <>
              <input
                type="text"
                value={logProfile}
                onChange={(e) => setLogProfile(e.target.value)}
                placeholder="AWS Profile (e.g. dev)"
                className="px-3 py-1.5 border rounded-md text-sm flex-1 sm:flex-none sm:w-32 focus:ring-2 focus:ring-blue-500 outline-none"
              />
              <input
                type="text"
                value={logRegion}
                onChange={(e) => setLogRegion(e.target.value)}
                placeholder="Region (e.g. eu-west-1)"
                className="px-3 py-1.5 border rounded-md text-sm flex-1 sm:flex-none sm:w-32 focus:ring-2 focus:ring-blue-500 outline-none"
              />
              <input
                type="text"
                value={logGroup}
                onChange={(e) => setLogGroup(e.target.value)}
                placeholder="Log Group Name"
                className="px-3 py-1.5 border rounded-md text-sm flex-1 sm:flex-none sm:w-48 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </>
          )}
          {viewLogType === "docker" && (
            <input
              type="text"
              value={viewDockerContainer}
              onChange={(e) => setViewDockerContainer(e.target.value)}
              placeholder="Container ID or Name"
              className="px-3 py-1.5 border rounded-md text-sm flex-1 sm:flex-none sm:w-64 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          )}
          {viewLogType === "file" && (
            <input
              type="text"
              value={viewLogFilePath}
              onChange={(e) => setViewLogFilePath(e.target.value)}
              placeholder="/var/log/... or C:\logs\..."
              className="px-3 py-1.5 border rounded-md text-sm flex-1 sm:flex-none sm:w-64 focus:ring-2 focus:ring-blue-500 outline-none"
            />
          )}
        </div>
      </div>
      <div className="bg-gray-900 text-green-400 p-4 rounded-md h-64 overflow-y-auto font-mono text-sm shadow-inner whitespace-pre-wrap wrap-break-word">
        {logs.length === 0 ? (
          <span className="text-gray-500 italic text-xs">
            {activeLogServerName
              ? `No logs available for ${activeLogServerName}. Ensure Log Group and Region are correctly configured...`
              : "No logs available. Ensure Log Group and Region are correctly configured..."}
          </span>
        ) : (
          <div className="flex flex-col gap-1">
            {logs.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
