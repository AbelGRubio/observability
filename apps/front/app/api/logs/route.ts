import { NextRequest } from "next/server";
import { spawn } from "child_process";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const type = searchParams.get("type") || "aws"; // "aws", "docker", "file"
  const region = searchParams.get("region");
  const group = searchParams.get("group");
  const profile = searchParams.get("profile") || "";
  const container = searchParams.get("container") || "";
  const path = searchParams.get("path") || "";

  // Set up a streaming response (Server-Sent Events)
  const stream = new ReadableStream({
    start(controller) {
      let commandString = "";

      if (type === "aws") {
        if (!region || !group) {
          controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: "[ERROR] Missing region or group for AWS logs" })}\n\n`));
          controller.close();
          return;
        }
        const intro = `Connected to CloudWatch logs for group: ${group} in ${region}${profile ? ` using profile ${profile}` : ""}\n`;
        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: intro })}\n\n`));
        const awsProfileFlag = profile ? `--profile ${profile}` : "";
        commandString = `aws logs tail ${group} --region ${region} ${awsProfileFlag} --follow --since 10m`;
      } else if (type === "docker") {
        if (!container) {
          controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: "[ERROR] Missing container name/ID for Docker logs" })}\n\n`));
          controller.close();
          return;
        }
        const intro = `Connected to Docker logs for container: ${container}\n`;
        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: intro })}\n\n`));
        commandString = `docker logs -f --tail 100 ${container}`;
      } else if (type === "file") {
        if (!path) {
          controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: "[ERROR] Missing file path for local logs" })}\n\n`));
          controller.close();
          return;
        }
        const intro = `Tailing local file: ${path}\n`;
        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: intro })}\n\n`));
        // tail -F works robustly for log rotation on macOS/Linux
        commandString = `tail -n 100 -F ${path}`;
      } else {
        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: `[ERROR] Unknown log type: ${type}` })}\n\n`));
        controller.close();
        return;
      }

      const tailProcess = spawn("zsh", ["-c", commandString]);

      // Stream stdout to the client
      tailProcess.stdout.on("data", (data) => {
        const lines = data.toString().split("\n");
        for (const line of lines) {
          if (line.trim()) {
            const payload = `data: ${JSON.stringify({ log: line })}\n\n`;
            controller.enqueue(new TextEncoder().encode(payload));
          }
        }
      });

      // Stream stderr to the client as well so we can see auth/awsume errors in the UI
      tailProcess.stderr.on("data", (data) => {
        const errorLine = `[ERROR] ${data.toString()}`;
        console.error(`AWS Logs Tail Error: ${errorLine}`);
        const payload = `data: ${JSON.stringify({ log: errorLine })}\n\n`;
        try {
          controller.enqueue(new TextEncoder().encode(payload));
        } catch (e) {
          // Ignore stream already closed errors
        }
      });

      tailProcess.on("close", (code) => {
        console.log(`AWS tail process exited with code ${code}`);
        try {
          if (code !== 0 && code !== null) {
            controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ log: `[STREAM ENDED] Process exited with code ${code}` })}

`));
          }
          // Send a named 'done' event so the browser can close the EventSource
          // cleanly without triggering its onerror handler
          controller.enqueue(new TextEncoder().encode(`event: done\ndata: {}\n\n`));
          controller.close();
        } catch (e) {
          console.log(` -> AWS tail process exited with error ${e}`);
          // Stream might already be closed
        }
      });

      // Clean up when the connection is closed
      request.signal.addEventListener("abort", () => {
        tailProcess.kill(); // Important: Kill the child process so it doesn't leak
        try {
          controller.close();
        } catch (e) {
          console.log(`AWS tail process exited with error ${e}`);
          // Stream might already be closed
        }
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
