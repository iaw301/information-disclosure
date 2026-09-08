#!/bin/sh
# Build-time: tao lich su .git ro ri secret + goi backup.zip chua source.
set -e
cd /usr/share/nginx/html

# --- Ma nguon ung dung gia co secret hardcode (cho /.git history + backup.zip) ---
cat > config.py <<'EOF'
# Nexus Edge - application configuration (INTERNAL - do not commit)
DB_HOST = "db.internal.nexus.local"
DB_USER = "nexus_app"
DB_PASS = "S3cr3t-DB-Pass-2026!"
SECRET_KEY = "IAW301{git_history_leaked_hardcoded_secret}"
STRIPE_KEY = "<redacted-lab-placeholder-rotate-leaked-payment-key>"
EOF

# backup.zip = ban sao luu source (con nguyen config.py co secret) -> vector source disclosure
zip -rq backup.zip index.html config.py robots.txt 2>/dev/null || true

# --- Lich su git: commit secret, roi "xoa" (van con trong history) ---
git init -q
git config user.email "dev@nexus.local"
git config user.name "nexus-dev"
git add -A
git commit -qm "initial edge portal with config" >/dev/null

git rm -q config.py >/dev/null
printf "config.py\n.env\n*.bak\n" > .gitignore
git add -A
git commit -qm "move secrets out of source, load from env instead" >/dev/null

# config.py da bi xoa khoi working tree (ffuf khong thay truc tiep) nhung
# git-dumper / git log --all khoi phuc lai duoc tu /.git.
echo "[seed_git] done: .git history + backup.zip ready"
