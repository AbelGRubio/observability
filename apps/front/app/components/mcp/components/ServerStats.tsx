import React from "react";

interface ServerStatsProps {
  totalServers: number;
  stdioServers: number;
  httpServers: number;
}

/**
 * ServerStats displays quick cards with metrics on the registered servers
 * (total number of servers, stdio-based, and HTTP-based).
 */
export function ServerStats({
  totalServers,
  stdioServers,
  httpServers,
}: ServerStatsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
      <div className="bg-white border rounded-md p-4">
        <div className="text-sm text-gray-500">Total Servers</div>
        <div className="text-3xl font-bold">{totalServers}</div>
      </div>
      <div className="bg-white border rounded-md p-4">
        <div className="text-sm text-gray-500">Stdio Servers</div>
        <div className="text-3xl font-bold">{stdioServers}</div>
      </div>
      <div className="bg-white border rounded-md p-4">
        <div className="text-sm text-gray-500">HTTP Servers</div>
        <div className="text-3xl font-bold">{httpServers}</div>
      </div>
    </div>
  );
}
