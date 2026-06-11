"use client";

import { useState, useEffect, useRef } from "react";
import { useCoAgent } from "@copilotkit/react-core";
import { useLocalStorage } from "../hooks/useLocalStorage";

// Imported Refactored Modules
import { ServerConfig, AgentState } from "./mcp/types";
import { useMCPLogs } from "./mcp/hooks/useMCPLogs";
import { ServerStats } from "./mcp/components/ServerStats";
import { ServerCard } from "./mcp/components/ServerCard";
import { AddEditServerModal } from "./mcp/components/AddEditServerModal";
import { LogsPanel } from "./mcp/components/LogsPanel";

// Local storage key for saving agent state
const STORAGE_KEY = "mcp-agent-state";

/**
 * MCPConfigForm is the main dashboard component for configuring Model Context Protocol (MCP) servers.
 * It provides administrative tools to view statistics, add/edit standard IO or HTTP configurations,
 * export/import JSON configurations, and stream/monitor container, local or CloudWatch server logs.
 */
export function MCPConfigForm() {
  // Use our localStorage hook for persistent storage of server configurations
  const [savedConfigs, setSavedConfigs] = useLocalStorage<Record<string, ServerConfig>>(
    STORAGE_KEY,
    {}
  );

  // Initialize agent state with the data from localStorage to keep the AI Copilot backend synced
  const { state: agentState, setState: setAgentState } = useCoAgent<AgentState>({
    name: "observe_agent",
    initialState: {
      mcp_config: savedConfigs,
    },
  });

  // Simple getter for current configurations
  const configs = agentState?.mcp_config || {};

  // Simple setter wrapper for configs that updates both CoAgent backend state and LocalStorage
  const setConfigs = (newConfigs: Record<string, ServerConfig>) => {
    setAgentState({ ...agentState, mcp_config: newConfigs });
    setSavedConfigs(newConfigs);
  };

  // UI state variables
  const [isLoading, setIsLoading] = useState(true);
  const [showAddServerForm, setShowAddServerForm] = useState(false);
  const [editingServerName, setEditingServerName] = useState<string | null>(null);

  // Logs visibility and target configuration state
  const [showLogs, setShowLogs] = useState(false);
  const [activeLogServerName, setActiveLogServerName] = useState<string | null>(null);
  const [viewLogType, setViewLogType] = useState<"aws" | "docker" | "file" | "none">("docker");
  const [logProfile, setLogProfile] = useState("");
  const [logGroup, setLogGroup] = useState("");
  const [logRegion, setLogRegion] = useState("");
  const [viewDockerContainer, setViewDockerContainer] = useState("");
  const [viewLogFilePath, setViewLogFilePath] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Use the custom hook to manage log stream subscription
  const { logs, setLogs } = useMCPLogs({
    showLogs,
    viewLogType,
    logProfile,
    logRegion,
    logGroup,
    viewDockerContainer,
    viewLogFilePath,
  });

  // Calculate statistics from the configurations
  const totalServers = Object.keys(configs).length;
  const stdioServers = Object.values(configs).filter(
    (config) => config.transport === "stdio"
  ).length;
  const httpServers = Object.values(configs).filter(
    (config) => config.transport === "http"
  ).length;

  // Once the agentState metadata/connection is established, disable loading spinner
  useEffect(() => {
    if (agentState) {
      setIsLoading(false);
    }
  }, [agentState]);

  /**
   * Triggers file download of the current configuration as a JSON file.
   */
  const exportConfigs = () => {
    const dataStr = JSON.stringify(configs, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "mcp-servers-config.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  /**
   * Reads, parses and validates an imported JSON configuration file,
   * prompting the user to either merge with or overwrite the existing configurations.
   */
  const importConfigs = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const parsed = JSON.parse(content);

        if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
          throw new Error("Invalid configuration format.");
        }

        const shouldReplace = window.confirm(
          "Do you want to replace your current configuration with the imported one? Click 'OK' to replace, or 'Cancel' to merge."
        );

        if (shouldReplace) {
          setConfigs(parsed);
        } else {
          setConfigs({ ...configs, ...parsed });
        }
      } catch (error) {
        alert("Error importing configuration. Please make sure the file is a valid JSON.");
        console.error(error);
      }

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    };
    reader.readAsText(file);
  };

  /**
   * Adds or updates a server config within the local & backend sync state.
   */
  const handleSaveConfig = (serverName: string, newConfig: ServerConfig) => {
    const updatedConfigs = { ...configs };

    // If editing and the server name has changed, remove the older key
    if (editingServerName && editingServerName !== serverName) {
      delete updatedConfigs[editingServerName];
    }

    updatedConfigs[serverName] = newConfig;
    setConfigs(updatedConfigs);

    // Reset modal states
    setShowAddServerForm(false);
    setEditingServerName(null);
  };

  /**
   * Removes a server configuration by name.
   */
  const removeConfig = (name: string) => {
    const newConfigs = { ...configs };
    delete newConfigs[name];
    setConfigs(newConfigs);
  };

  /**
   * Pre-populates search/form and opens the editing modal.
   */
  const openEditModal = (name: string) => {
    setEditingServerName(name);
    setShowAddServerForm(true);
  };

  /**
   * Activates log-viewing mode, setting appropriate credentials or identifiers
   * (AWS Logs details, docker container tags, or file paths) based on the config.
   */
  const handleViewLogs = (name: string, config: ServerConfig) => {
    if (showLogs && activeLogServerName === name) {
      setShowLogs(false);
      setActiveLogServerName(null);
      return;
    }

    if (config.logType && config.logType !== "none") {
      setViewLogType(config.logType);
      if (config.awsLogGroup) setLogGroup(config.awsLogGroup);
      if (config.awsLogRegion) setLogRegion(config.awsLogRegion);
      if (config.dockerContainer) setViewDockerContainer(config.dockerContainer);
      if (config.logFilePath) setViewLogFilePath(config.logFilePath);
    }
    setActiveLogServerName(name);
    setShowLogs(true);
    setTimeout(() => {
      document.getElementById("server-logs-section")?.scrollIntoView({ behavior: "smooth" });
    }, 100);
    setShowAddServerForm(false);
  };

  if (isLoading) {
    return <div className="p-4">Loading configuration...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Panel */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-1">
          <div className="flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 mr-2 text-gray-700"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"
              />
            </svg>
            <h1 className="text-3xl sm:text-5xl font-semibold">
              Observe MCP Client
            </h1>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                if (showLogs) {
                  setActiveLogServerName(null);
                }
                setShowLogs(!showLogs);
              }}
              className="w-full sm:w-auto px-3 py-1.5 bg-gray-800 text-white rounded-md text-sm font-medium hover:bg-gray-700 flex items-center gap-1 justify-center transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              {showLogs ? 'Hide Logs' : 'Show Logs'}
            </button>
            <button
              onClick={() => setShowAddServerForm(true)}
              className="w-full sm:w-auto px-3 py-1.5 bg-gray-800 text-white rounded-md text-sm font-medium hover:bg-gray-700 flex items-center gap-1 justify-center transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
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
              Add MCP Server
            </button>
          </div>
        </div>
      </div>

      {/* Server Statistics Section */}
      <ServerStats
        totalServers={totalServers}
        stdioServers={stdioServers}
        httpServers={httpServers}
      />

      {/* Configured Servers Grid Dashboard */}
      <div className="bg-white border rounded-md p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-4">
          <h2 className="text-lg font-semibold">MCP Server List</h2>
          <div className="flex gap-2">
            <input
              type="file"
              accept=".json"
              className="hidden"
              ref={fileInputRef}
              onChange={importConfigs}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-1.5 border border-gray-300 text-gray-700 bg-white rounded-md text-sm font-medium hover:bg-gray-50 flex items-center justify-center transition-colors"
              title="Import configuration JSON"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Import
            </button>
            <button
              onClick={exportConfigs}
              className="px-3 py-1.5 border border-gray-300 text-gray-700 bg-white rounded-md text-sm font-medium hover:bg-gray-50 flex items-center justify-center transition-colors"
              title="Export configuration JSON"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Export
            </button>
          </div>
        </div>

        {totalServers === 0 ? (
          <div className="text-gray-500 text-center py-10">
            No servers configured. Click &quot;Add Server&quot; to get started.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(configs).map(([name, config]) => (
              <ServerCard
                key={name}
                name={name}
                config={config}
                onViewLogs={handleViewLogs}
                onEdit={openEditModal}
                onRemove={removeConfig}
              />
            ))}
          </div>
        )}
      </div>

      {/* Target Server Logs Streamer */}
      <LogsPanel
        showLogs={showLogs}
        activeLogServerName={activeLogServerName}
        onCloseLogs={() => {
          setShowLogs(false);
          setActiveLogServerName(null);
        }}
        viewLogType={viewLogType}
        setViewLogType={setViewLogType}
        logProfile={logProfile}
        setLogProfile={setLogProfile}
        logRegion={logRegion}
        setLogRegion={setLogRegion}
        logGroup={logGroup}
        setLogGroup={setLogGroup}
        viewDockerContainer={viewDockerContainer}
        setViewDockerContainer={setViewDockerContainer}
        viewLogFilePath={viewLogFilePath}
        setViewLogFilePath={setViewLogFilePath}
        logs={logs}
      />

      {/* Add / Edit Server Modal Dialog */}
      <AddEditServerModal
        isOpen={showAddServerForm}
        onClose={() => {
          setShowAddServerForm(false);
          setEditingServerName(null);
        }}
        onSave={handleSaveConfig}
        editingServerName={editingServerName}
        initialConfig={editingServerName ? configs[editingServerName] : null}
      />
    </div>
  );
}
