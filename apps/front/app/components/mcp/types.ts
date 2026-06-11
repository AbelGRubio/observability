export type ConnectionType = "stdio" | "streamable_http";

export interface StdioConfig {
  command: string;
  args: string[];
  transport: "stdio";
  logType?: "none" | "aws" | "docker" | "file";
  awsLogGroup?: string;
  awsLogRegion?: string;
  dockerContainer?: string;
  logFilePath?: string;
}

export interface HTTPConfig {
  url: string;
  transport: "http";
  headers?: Record<string, string>;
  logType?: "none" | "aws" | "docker" | "file";
  awsLogGroup?: string;
  awsLogRegion?: string;
  dockerContainer?: string;
  logFilePath?: string;
}

export type ServerConfig = StdioConfig | HTTPConfig;

export interface AgentState {
  mcp_config: Record<string, ServerConfig>;
}
