import React, { useState, useEffect } from "react";
import { ServerConfig, ConnectionType } from "../types";

interface AddEditServerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, config: ServerConfig) => void;
  editingServerName: string | null;
  initialConfig: ServerConfig | null;
}

/**
 * AddEditServerModal handles editing an existing MCP Server or adding a new one.
 * It manages local state for all inputs and properly formats the config before saving.
 */
export function AddEditServerModal({
  isOpen,
  onClose,
  onSave,
  editingServerName,
  initialConfig,
}: AddEditServerModalProps) {
  const [serverName, setServerName] = useState("");
  const [connectionType, setConnectionType] = useState<ConnectionType>("stdio");
  const [command, setCommand] = useState("");
  const [args, setArgs] = useState("");
  const [url, setUrl] = useState("");
  const [headers, setHeaders] = useState<{ key: string; value: string }[]>([]);

  // Logs Config form states
  const [inFormLogType, setInFormLogType] = useState<"none" | "aws" | "docker" | "file">("none");
  const [awsLogGroup, setAwsLogGroup] = useState("");
  const [awsLogRegion, setAwsLogRegion] = useState("");
  const [inFormDockerContainer, setInFormDockerContainer] = useState("");
  const [inFormLogFilePath, setInFormLogFilePath] = useState("");

  // Initialize or reset form state when modal opens or initialConfig changes
  useEffect(() => {
    if (isOpen) {
      if (editingServerName && initialConfig) {
        setServerName(editingServerName);
        setConnectionType(
          initialConfig.transport === "http" ? "streamable_http" : "stdio"
        );

        if (initialConfig.transport === "stdio") {
          setCommand(initialConfig.command);
          setArgs(initialConfig.args.join(" "));
          setUrl("");
          setHeaders([]);
        } else {
          setUrl(initialConfig.url);
          setCommand("");
          setArgs("");
          setHeaders(
            Object.entries(initialConfig.headers || {}).map(([key, value]) => ({
              key,
              value,
            }))
          );
        }

        setInFormLogType(initialConfig.logType || "none");
        setAwsLogGroup(initialConfig.awsLogGroup || "");
        setAwsLogRegion(initialConfig.awsLogRegion || "");
        setInFormDockerContainer(initialConfig.dockerContainer || "");
        setInFormLogFilePath(initialConfig.logFilePath || "");
      } else {
        // Clear all values for a new server
        setServerName("");
        setConnectionType("stdio");
        setCommand("");
        setArgs("");
        setUrl("");
        setHeaders([]);
        setInFormLogType("none");
        setAwsLogGroup("");
        setAwsLogRegion("");
        setInFormDockerContainer("");
        setInFormLogFilePath("");
      }
    }
  }, [isOpen, editingServerName, initialConfig]);

  if (!isOpen) return null;

  const handleAddHeader = () => {
    setHeaders([...headers, { key: "", value: "" }]);
  };

  const handleUpdateHeader = (index: number, field: "key" | "value", val: string) => {
    const updated = [...headers];
    updated[index] = { ...updated[index], [field]: val };
    setHeaders(updated);
  };

  const handleRemoveHeader = (index: number) => {
    setHeaders(headers.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    if (!serverName.trim()) {
      alert("Server name is required.");
      return;
    }

    const baseLogConfig = {
      logType: inFormLogType,
      ...(awsLogGroup.trim() ? { awsLogGroup: awsLogGroup.trim() } : {}),
      ...(awsLogRegion.trim() ? { awsLogRegion: awsLogRegion.trim() } : {}),
      ...(inFormDockerContainer.trim() ? { dockerContainer: inFormDockerContainer.trim() } : {}),
      ...(inFormLogFilePath.trim() ? { logFilePath: inFormLogFilePath.trim() } : {}),
    };

    const headersRecord = headers.reduce<Record<string, string>>(
      (acc, { key, value }) => {
        if (key.trim()) acc[key.trim()] = value;
        return acc;
      },
      {}
    );

    const formattedConfig =
      connectionType === "stdio"
        ? {
            ...baseLogConfig,
            command,
            args: args.split(" ").filter((arg) => arg.trim() !== ""),
            transport: "stdio" as const,
          }
        : {
            ...baseLogConfig,
            url,
            transport: "http" as const,
            ...(Object.keys(headersRecord).length > 0 && { headers: headersRecord }),
          };

    onSave(serverName, formattedConfig);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-5 h-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            {editingServerName ? "Edit Server" : "Add New Server"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="w-5 h-5"
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
        </div>

        {/* Form Fields */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Server Name
            </label>
            <input
              type="text"
              value={serverName}
              onChange={(e) => setServerName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
              placeholder="e.g., api-service, data-processor"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Connection Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setConnectionType("stdio")}
                className={`px-3 py-2 border rounded-md text-center flex items-center justify-center text-sm ${
                  connectionType === "stdio"
                    ? "bg-gray-200 border-gray-400 text-gray-800"
                    : "bg-white text-gray-700"
                }`}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-4 h-4 mr-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                Standard IO
              </button>
              <button
                type="button"
                onClick={() => setConnectionType("streamable_http")}
                className={`px-3 py-2 border rounded-md text-center flex items-center justify-center text-sm ${
                  connectionType === "streamable_http"
                    ? "bg-gray-200 border-gray-400 text-gray-800"
                    : "bg-white text-gray-700"
                }`}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-4 h-4 mr-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                  />
                </svg>
                HTTP
              </button>
            </div>
          </div>

          {connectionType === "stdio" ? (
            <>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Command
                </label>
                <input
                  type="text"
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                  placeholder="e.g., python, node"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  Arguments
                </label>
                <input
                  type="text"
                  value={args}
                  onChange={(e) => setArgs(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                  placeholder="e.g., path/to/script.py"
                />
              </div>
            </>
          ) : (
            <>
              <div>
                <label className="block text-sm font-medium mb-1">URL</label>
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md text-sm"
                  placeholder="e.g., http://localhost:8000/events"
                />
              </div>

              <div className="pt-2 border-t mt-3">
                <label className="block text-md font-semibold text-gray-700 mb-2">
                  Optional parameters
                </label>
              </div>

              {/* Headers */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-sm font-medium">Headers</label>
                  <button
                    type="button"
                    onClick={handleAddHeader}
                    className="text-xs px-2 py-0.5 border rounded hover:bg-gray-50 text-gray-600 flex items-center gap-1"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="w-3 h-3"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                    Add Header
                  </button>
                </div>
                {headers.length === 0 ? (
                  <p className="text-xs text-gray-400 italic">
                    No headers added.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {headers.map((header, index) => (
                      <div key={index} className="flex gap-2 items-center">
                        <input
                          type="text"
                          value={header.key}
                          onChange={(e) =>
                            handleUpdateHeader(index, "key", e.target.value)
                          }
                          className="flex-1 px-2 py-1.5 border rounded-md text-xs font-mono"
                          placeholder="Header name"
                        />
                        <input
                          type="text"
                          value={header.value}
                          onChange={(e) =>
                            handleUpdateHeader(index, "value", e.target.value)
                          }
                          className="flex-1 px-2 py-1.5 border rounded-md text-xs font-mono"
                          placeholder="Value"
                        />
                        <button
                          type="button"
                          onClick={() => handleRemoveHeader(index)}
                          className="text-gray-400 hover:text-red-500 shrink-0"
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
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Logs Configuration Section */}
              <div className="pt-4 border-t mt-4">
                <h3 className="text-sm font-semibold mb-3 text-gray-700">
                  Logs Configuration
                </h3>

                <div className="mb-3">
                  <label className="block text-sm font-medium mb-1">
                    Target Source
                  </label>
                  <select
                    value={inFormLogType}
                    onChange={(e) => setInFormLogType(e.target.value as any)}
                    className="w-full px-3 py-2 border rounded-md text-sm bg-white"
                  >
                    <option value="none">None</option>
                    <option value="aws">AWS CloudWatch</option>
                    <option value="docker">Docker Container</option>
                    <option value="file">Local File (.log)</option>
                  </select>
                </div>

                {inFormLogType === "aws" && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Log Group
                      </label>
                      <input
                        type="text"
                        value={awsLogGroup}
                        onChange={(e) => setAwsLogGroup(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md text-sm"
                        placeholder="e.g., /aws/bedrock-agentcore/runtimes/..."
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Region
                      </label>
                      <input
                        type="text"
                        value={awsLogRegion}
                        onChange={(e) => setAwsLogRegion(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md text-sm"
                        placeholder="e.g., eu-west-1"
                      />
                    </div>
                  </div>
                )}

                {inFormLogType === "docker" && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Container Name / ID
                      </label>
                      <input
                        type="text"
                        value={inFormDockerContainer}
                        onChange={(e) => setInFormDockerContainer(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md text-sm"
                        placeholder="e.g., my-mcp-container"
                      />
                    </div>
                  </div>
                )}

                {inFormLogType === "file" && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Log File Path
                      </label>
                      <input
                        type="text"
                        value={inFormLogFilePath}
                        onChange={(e) => setInFormLogFilePath(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md text-sm"
                        placeholder="e.g., /var/log/mcp.log"
                      />
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-2 pt-4 border-t">
            <button
              onClick={onClose}
              className="px-4 py-2 border text-gray-700 rounded-md hover:bg-gray-50 text-sm font-medium flex items-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-4 h-4 mr-1"
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
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 text-sm font-medium flex items-center"
            >
              {editingServerName ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-4 h-4 mr-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-4 h-4 mr-1"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              )}
              {editingServerName ? "Save Changes" : "Add Server"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
