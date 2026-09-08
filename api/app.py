from flask import Flask, jsonify, Response

app = Flask(__name__)

DIAG_TOKEN = "IAW301{swagger_exposed_hidden_diagnostics_endpoint}"

OPENAPI = {
    "openapi": "3.0.3",
    "info": {"title": "Nexus Edge Internal API", "version": "1.0.4-staging",
             "description": "Auto-generated docs. STAGING - do not expose publicly."},
    "servers": [{"url": "/"}],
    "paths": {
        "/api/v1/status": {"get": {"summary": "Service status", "responses": {"200": {"description": "ok"}}}},
        "/api/v1/system/diagnostics": {"get": {
            "summary": "Platform diagnostics (operators only)",
            "description": "Returns build metadata and the internal verification token. Not linked from the site.",
            "responses": {"200": {"description": "diagnostics incl. internal_verification_token"}}}},
    },
}

SWAGGER_HTML = """<!DOCTYPE html><html><head><meta charset=utf-8><title>Nexus Edge API - Swagger UI</title>
<style>body{background:#0f172a;color:#e2e8f0;font-family:sans-serif;margin:0}
header{background:#111827;padding:16px 24px;color:#38bdf8}main{max-width:820px;margin:0 auto;padding:24px}
.op{border:1px solid #1f2937;border-radius:8px;margin-bottom:12px}.h{display:flex;gap:10px;padding:12px 16px;background:#111827}
.m{font-weight:700;background:#0e7490;color:#e0f2fe;padding:3px 9px;border-radius:4px;font-size:.75rem}
.p{font-family:monospace}.b{padding:12px 16px;border-top:1px solid #1f2937;color:#cbd5e1;font-size:.9rem}</style></head>
<body><header id=t>Loading...</header><main id=ops></main>
<script>fetch('/openapi.json').then(r=>r.json()).then(s=>{document.getElementById('t').textContent=s.info.title+' v'+s.info.version;
var o=document.getElementById('ops');Object.keys(s.paths).forEach(function(p){var g=s.paths[p].get;var d=document.createElement('div');
d.className='op';d.innerHTML='<div class=h><span class=m>GET</span><span class=p>'+p+'</span></div><div class=b>'+(g.description||g.summary||'')+'</div>';o.appendChild(d);});});</script>
</body></html>"""


@app.route("/openapi.json")
@app.route("/api/openapi.json")
def openapi():
    return jsonify(OPENAPI)


@app.route("/swagger-ui/")
@app.route("/swagger-ui")
def swagger():
    return Response(SWAGGER_HTML, mimetype="text/html")


@app.route("/api/v1/status")
@app.route("/internal-api/status")
def status():
    return jsonify({"service": "nexus-edge-api", "version": "1.0.4-staging", "status": "healthy"})


@app.route("/api/v1/system/diagnostics")
def diagnostics():
    return jsonify({
        "service": "nexus-edge-api", "build": "1.0.4-staging", "node": "edge-alpha-01",
        "internal_verification_token": DIAG_TOKEN,
    })


@app.route("/")
def root():
    return jsonify({"service": "nexus-edge-api", "docs": "/swagger-ui/"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
