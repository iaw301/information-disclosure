#!/bin/sh
# Redis khong dat mat khau, lang nghe 0.0.0.0 -> ai cung ket noi va dump key duoc.
redis-server --bind 0.0.0.0 --protected-mode no --save '' --appendonly no &
sleep 1
redis-cli set "config:db_password" "S3cr3t-DB-Pass-2026!"
redis-cli set "config:jwt_signing_key" "hunter2-jwt-signing-key-please-rotate"
redis-cli set "session:admin:token" "IAW301{unauthenticated_redis_exposed_key}"
redis-cli set "feature:flags" "beta_admin_panel=1;debug=1"
echo "[seed] redis keys loaded"
wait
