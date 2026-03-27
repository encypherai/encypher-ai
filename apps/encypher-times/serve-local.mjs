/**
 * Local dev server that proxies /api/* to the live API (avoiding CORS)
 * and delegates all other requests to `npx serve` for correct static file serving.
 *
 * Usage: node serve-local.mjs [port]   (default 3060)
 */
import { createServer, request as httpRequest } from "node:http";
import { request as httpsRequest } from "node:https";
import { spawn } from "node:child_process";

const PORT = parseInt(process.argv[2] || "3060", 10);
const SERVE_PORT = PORT + 1; // internal port for npx serve
const API_HOST = "api.encypher.com";

// Start npx serve on the internal port
const serve = spawn("npx", ["serve", "out", "-l", String(SERVE_PORT), "--no-clipboard"], {
  cwd: import.meta.dirname,
  stdio: "pipe",
});
serve.stderr.on("data", (d) => process.stderr.write(d));
serve.on("exit", (code) => {
  console.error(`serve exited with code ${code}`);
  process.exit(1);
});

function proxyToApi(req, res) {
  const opts = {
    hostname: API_HOST,
    port: 443,
    path: req.url,
    method: req.method,
    headers: { ...req.headers, host: API_HOST },
  };
  delete opts.headers["origin"];
  delete opts.headers["referer"];

  const proxy = httpsRequest(opts, (upstream) => {
    const h = { ...upstream.headers };
    delete h["access-control-allow-origin"];
    res.writeHead(upstream.statusCode, h);
    upstream.pipe(res);
  });
  proxy.on("error", (e) => {
    res.writeHead(502);
    res.end(`Proxy error: ${e.message}`);
  });
  req.pipe(proxy);
}

function proxyToServe(req, res) {
  const opts = {
    hostname: "127.0.0.1",
    port: SERVE_PORT,
    path: req.url,
    method: req.method,
    headers: req.headers,
  };
  const proxy = httpRequest(opts, (upstream) => {
    res.writeHead(upstream.statusCode, upstream.headers);
    upstream.pipe(res);
  });
  proxy.on("error", (e) => {
    res.writeHead(502);
    res.end(`Static server error: ${e.message}`);
  });
  req.pipe(proxy);
}

// Wait for serve to be ready, then start the proxy
function waitForServe(retries = 20) {
  const check = httpRequest({ hostname: "127.0.0.1", port: SERVE_PORT, path: "/", method: "HEAD" }, () => {
    createServer((req, res) => {
      if (req.url.startsWith("/api/")) {
        proxyToApi(req, res);
      } else {
        proxyToServe(req, res);
      }
    }).listen(PORT, () => {
      console.log(`Encypher Times demo: http://localhost:${PORT}`);
      console.log(`API proxy: /api/* -> https://${API_HOST}`);
    });
  });
  check.on("error", () => {
    if (retries > 0) {
      setTimeout(() => waitForServe(retries - 1), 500);
    } else {
      console.error("Failed to connect to internal serve process");
      process.exit(1);
    }
  });
  check.end();
}

waitForServe();
