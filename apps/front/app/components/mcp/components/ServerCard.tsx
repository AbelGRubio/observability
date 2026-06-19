import React from "react";
import { ServerConfig } from "../types";

interface ServerCardProps {
  name: string;
  config: ServerConfig;
  onViewLogs: (name: string, config: ServerConfig) => void;
  onEdit: (name: string, config: ServerConfig) => void;
  onRemove: (name: string) => void;
}

/**
 * ServerCard renders individual server configurations, showing transport details
 * (such as Stdio command/args or HTTP URL/Headers) and actions to edit, delete or view logs.
 */
export function ServerCard({
  name,
  config,
  onViewLogs,
  onEdit,
  onRemove,
}: ServerCardProps) {
  const isStdio = config.transport === "stdio";

  return (
    <div className="border rounded-md overflow-hidden bg-white shadow-sm">
      <div className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-semibold">{name}</h3>
            <div className="inline-flex items-center px-2 py-0.5 bg-gray-100 text-xs rounded mt-1 text-gray-700">
              {isStdio ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-3 h-3 mr-1"
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
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-3 h-3 mr-1"
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
              )}
              {config.transport}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onViewLogs(name, config)}
              className="text-gray-400 hover:text-green-500 transition-colors"
              title="View logs"
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </button>
            <button
              onClick={() => onEdit(name, config)}
              className="text-gray-400 hover:text-blue-500 transition-colors"
              title="Edit server"
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
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
            <button
              onClick={() => onRemove(name)}
              className="text-gray-400 hover:text-red-500 transition-colors"
              title="Remove server"
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
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
        <div className="mt-3 text-sm text-gray-600">
          {isStdio ? (
            <>
              <p className="truncate">
                <span className="font-semibold">Command:</span> {(config as any).command}
              </p>
              <p className="truncate">
                <span className="font-semibold">Args:</span>{" "}
                {(config as any).args ? (config as any).args.join(" ") : ""}
              </p>
            </>
          ) : (
            <>
              <p className="truncate">
                <span className="font-semibold">URL:</span> {(config as any).url}
              </p>
              {(config as any).headers && Object.keys((config as any).headers).length > 0 && (
                <div className="mt-1">
                  <p className="text-xs font-semibold text-gray-500 mb-0.5">
                    Headers:
                  </p>
                  {Object.entries((config as any).headers).map(([k, v]) => (
                    <p key={k} className="truncate text-xs">
                      <span className="font-mono">{k}:</span>{" "}
                      <span className="font-mono text-gray-500">
                        {v as string}
                      </span>
                    </p>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
