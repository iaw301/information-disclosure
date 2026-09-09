#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chay Recon Range o che do KHONG CAN DOCKER (chi phan WEB).

Dung cho sinh vien khong cai duoc Docker: van luyen duoc content-discovery
(ffuf/feroxbuster), doc file de lo (.env/.bak/.sql/robots), /.git + git-dumper,
va Swagger + endpoint an. CHI cần Python 3 (va 'git' CLI cho phan /.git).

Cac dich vu can cho nmap (FTP anonymous, Redis khong auth, banner SSH/SMTP)
KHONG chay o che do nay -> dung ban Docker (`docker compose up`) hoac instance
chung do giao vien host.

Chay:  python serve_nodocker.py        (mac dinh port 8080)
       PORT=9000 python serve_nodocker.py
"""
import http.server
import socketserver
import functools
import shutil
import subprocess
import tempfile
import zipfile
import json
import os

PORT = int(os.environ.get("PORT", "8080"))
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "web", "html")

OPENAPI = {
    "openapi": "3.0.3",
    "info": {"title": "Nexus Edge Internal API", "version": "1.0.4-staging",
             "description": "Auto-generated docs. STAGING - do not expose publicly."},
    "paths": {
        "/api/v1/status": {"get": {"summary": "Service status"}},
        "/api/v1/system/diagnostics": {"get": {
            "summary": "Platform diagnostics (operators only)",
            "description": "Returns build metadata and the internal verification token. Not linked from the site."}},
    },
}
SWAGGER_HTML = ("<!DOCTYPE html><meta charset=utf-8><title>Nexus Edge API - Swagger UI</title>"
                "<body style='font-family:sans-serif'><h2 id=t>Loading...</h2><div id=o></div>"
                "<script>fetch('/openapi.json').then(r=>r.json()).then(s=>{document.getElementById('t')"
                ".textContent=s.info.title+' v'+s.info.version;var o=document.getElementById('o');"
                "Object.keys(s.paths).forEach(function(p){var g=s.paths[p].get;o.innerHTML+="
                "'<p><b>GET</b> <code>'+p+'</code> — '+(g.description||g.summary||'')+'</p>';});});</script>")
DIAG = "IAW301{swagger_exposed_hidden_diagnostics_endpoint}"


def build_webroot():
    """Copy web/html sang thu muc tam va tao lich su .git ro ri (giong seed_git.sh)."""
    tmp = tempfile.mkdtemp(prefix="reconrange_")
    root = os.path.join(tmp, "html")
    shutil.copytree(SRC, root)
    try:
        cfg = os.path.join(root, "config.py")
        with open(cfg, "w", encoding="utf-8") as f:
            f.write('DB_PASS = "S3cr3t-DB-Pass-2026!"\n'
                    'SECRET_KEY = "IAW301{git_history_leaked_hardcoded_secret}"\n')
        with zipfile.ZipFile(os.path.join(root, "backup.zip"), "w") as z:
            for fn in ("index.html", "config.py", "robots.txt"):
                p = os.path.join(root, fn)
                if os.path.exists(p):
                    z.write(p, fn)

        def g(*a):
            subprocess.run(["git", "-C", root, *a], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        g("init", "-q")
        g("config", "user.email", "dev@nexus.local")
        g("config", "user.name", "nexus-dev")
        g("add", "-A")
        g("commit", "-qm", "initial edge portal with config")
        g("rm", "-q", "config.py")
        with open(os.path.join(root, ".gitignore"), "w") as f:
            f.write("config.py\n.env\n")
        g("add", "-A")
        g("commit", "-qm", "move secrets out of source, load from env")
        print("[+] .git history + backup.zip ready (git-dumper OK)")
    except Exception as e:
        print("[!] 'git' khong san sang -> phan /.git bo qua (van dung ffuf cho cac file khac):", e)
    return root


class Handler(http.server.SimpleHTTPRequestHandler):
    # Gia banner nginx cu (thay vi lo "SimpleHTTP/Python") -> banner disclosure van hoc duoc
    server_version = "nginx/1.18.0"
    sys_version = ""
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".php": "text/html", ".env": "text/plain", ".bak": "text/plain",
        ".sql": "text/plain", ".js": "application/javascript",
        ".map": "application/json", "": "application/octet-stream",
    }

    def end_headers(self):
        self.send_header("X-Powered-By", "PHP/5.6.40")
        super().end_headers()

    def _send(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/openapi.json", "/api/openapi.json"):
            return self._send(json.dumps(OPENAPI).encode(), "application/json")
        if p.startswith("/swagger-ui"):
            return self._send(SWAGGER_HTML.encode(), "text/html")
        if p in ("/api/v1/status", "/internal-api/status"):
            return self._send(json.dumps({"service": "nexus-edge-api", "version": "1.0.4-staging",
                                          "status": "healthy"}).encode(), "application/json")
        if p == "/api/v1/system/diagnostics":
            return self._send(json.dumps({"service": "nexus-edge-api", "build": "1.0.4-staging",
                                          "internal_verification_token": DIAG}).encode(), "application/json")
        if p == "/server-status":
            return self._send(b"Active connections: 3\nserver accepts handled requests\n 42 42 91\n",
                              "text/plain")
        if p == "/admin/" or p == "/admin":
            self.send_error(403, "Forbidden")
            return
        return super().do_GET()

    def log_message(self, *a):
        pass  # im lang cho do nhieu khi bi ffuf/feroxbuster na


if __name__ == "__main__":
    root = build_webroot()
    handler = functools.partial(Handler, directory=root)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"[+] Recon Range (WEB, no-Docker) chay tai http://0.0.0.0:{PORT}/  (Ctrl+C de dung)")
        print(f"    webroot tam: {root}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[+] Dung.")
