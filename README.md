# Nexus Recon Range — Sân tập Trinh sát & Lộ lọt Thông tin

Một **sandbox nhiều dịch vụ** để sinh viên **thỏa sức** dùng `nmap`, `ffuf`, `feroxbuster`,
`git-dumper`, `redis-cli`, FTP… mà **không sợ hỏng gì**: mọi thứ trong Docker, không có
rate-limit / WAF / ban, reset một nốt nhạc. Mỗi lỗ hổng có **marker** `IAW301{...}` để **tự chấm**.

> Đây là **range luyện tập** (không phải bài CTF chấm điểm).

---

## 0. Chạy thế nào? — 3 chế độ (có / không Docker)

> **Điểm mấu chốt:** range này là **mục tiêu (target)**, không phải thứ mỗi sinh viên phải tự
> dựng. Lớp có bạn có Docker, bạn không — vẫn ổn, xem 3 chế độ dưới.

| Chế độ | Cần gì | Có được gì |
| :--- | :--- | :--- |
| **A. Đầy đủ (Docker)** | Docker + `docker compose` | **Toàn bộ 5 dịch vụ**: nmap (nhiều port) + ffuf/ferox + git-dumper + redis + ftp |
| **B. Target chung** ⭐ | Giáo viên host **1 instance** (Docker trên 1 máy/VM/VPS) | Cả lớp chĩa tool vào `<host>:port` — **không sinh viên nào cần Docker** |
| **C. Web-only không Docker** | Python 3 (+ `git`) | Phần **web**: ffuf/ferox + git-dumper + đọc file lộ + Swagger. **Không** có ftp/redis/ssh (phần nmap-multi-service) |

**A — Docker (đầy đủ):**
```bash
docker compose up -d --build      # khoi dong
docker compose down               # dung
docker compose down && docker compose up -d --build   # RESET sach
```

**B — Target chung (khuyến nghị cho lớp học hỗn hợp):**
Giáo viên chạy chế độ A trên **một** máy/VM/VPS rồi phát `IP:port` cho lớp. Mọi sinh viên
(kể cả máy **không** có Docker) chỉ cần cài `nmap` / `ffuf` / `feroxbuster` và chĩa vào host đó.
→ Docker chỉ cần trên **một** máy host, không phải mỗi máy sinh viên.

**C — Không Docker, web-only (chạy cục bộ trên máy sinh viên):**
```bash
python serve_nodocker.py          # http://localhost:8080  (chi can Python 3 + git)
# PORT=9000 python serve_nodocker.py
```
Covers ffuf/feroxbuster + git-dumper + `.env`/`.bak`/`.sql`/`robots` + `/uploads/` listing +
Swagger + `/server-status` + banner qua header. Các dịch vụ cho nmap (FTP/Redis/SSH) thì dùng A hoặc B.

> **Đổi port (chế độ A) nếu trùng:** `WEB_PORT=18080 API_PORT=18000 FTP_PORT=2121 SSH_PORT=12222 SMTP_PORT=12525 REDIS_PORT=16379 docker compose up -d`.

**Bản đồ dịch vụ (mục tiêu cho `nmap`):**

| Dịch vụ | Port mặc định | Ghi chú | Có ở chế độ |
| :--- | :---: | :--- | :---: |
| web (nginx 1.18) | 8080 | banner phiên bản cũ, autoindex, `/.git` để hở | A, B, **C** |
| api (Flask) | 8000 | HTTP thứ 2, Swagger, endpoint ẩn | A, B (C gộp vào 8080) |
| ftp (vsftpd, anonymous) | 21 | `ftp-anon` → backup chứa credentials | A, B |
| ssh banner | 2222 | `OpenSSH_7.2p2` (cũ → tra CVE) | A, B |
| smtp banner | 2525 | `Postfix` (cũ) | A, B |
| redis (no-auth) | 6379 | dump key chứa secret | A, B |

---

## 1. Nhiệm vụ (cho sinh viên — Black-box)

> Bạn được cấp host `nexus-edge`. Hãy **trinh sát toàn diện**: quét cổng & dịch vụ, fuzz
> thư mục/file, khai thác cấu hình sai và file để lộ. Mục tiêu: thu **~16 marker `IAW301{...}`**.

### Bộ công cụ (đủ cho chủ đề này)

```bash
# 1) Quet cong + dich vu + NSE
nmap -sV -sC -p- --min-rate 2000 <host>
nmap -p 8080 --script http-enum,http-git,http-headers,http-robots.txt <host>
nmap -p 21   --script ftp-anon <host>

# 2) Content discovery (ffuf hoac feroxbuster) - wordlist SecLists chuan
ffuf -u http://<host>:8080/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt \
     -e .bak,.old,.zip,.sql,.env -mc 200,301,403 -t 100
feroxbuster -u http://<host>:8080 -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x bak,old,zip,sql

# 3) Khoi phuc source tu /.git
git-dumper http://<host>:8080/.git/ ./loot && (cd loot && git log --all -p | grep -i secret)

# 4) Redis khong xac thuc / FTP anonymous
redis-cli -h <host> -p 6379 KEYS '*'; redis-cli -h <host> -p 6379 GET session:admin:token
curl ftp://<host>:21/backup/credentials.txt
```

**Mẹo:** phân biệt status-code — `200` (thấy), `403` (**tồn tại** nhưng bị chặn, khác `404`!),
`301` (redirect). Luyện lọc `-mc/-fc/-fs` của ffuf.

> Vài vector không fuzz được bằng tool (comment `View Source`, `console.log`, source map
> `.js.map`) — dùng trình duyệt/DevTools.

---

## 2. LEAKS CATALOG (đáp án — cho giảng viên / tự chấm)

<details><summary>Bấm để xem toàn bộ lời giải</summary>

| # | Vector | Đường vào | Marker | Chế độ |
| :---: | :--- | :--- | :--- | :---: |
| 1 | Version/banner | header `Server: nginx/1.18.0` + `X-Powered-By: PHP/5.6.40` | *(banner)* | A,B,C |
| 2 | Robots.txt | `/robots.txt` | `robots_txt_recon_roadmap` | A,B,C |
| 3 | `.env` | `/.env` | `env_file_public_credentials` | A,B,C |
| 4 | Backup config | `/config.php.bak` | `backup_config_db_password_exposed` | A,B,C |
| 5 | SQL dump (MD5) | `/db.sql` → crack MD5 (`admin/password/123456`) | `sql_dump_unsalted_md5_hashes_leaked` | A,B,C |
| 6 | Backup archive | `/backup.zip` → `config.py` | `git_history_leaked_hardcoded_secret` | A,B,C |
| 7 | `.git` để hở | `git-dumper …/.git/` → history `config.py` | `git_history_leaked_hardcoded_secret` | A,B,C |
| 8 | Directory listing | `/uploads/` → `internal_memo.txt` | `directory_listing_leaked_internal_memo` | A,B,C |
| 9 | phpinfo | `/phpinfo.php` (env vars) | `phpinfo_environment_variable_disclosure` | A,B,C |
| 10 | security.txt | `/.well-known/security.txt` | `security_txt_information_disclosure` | A,B,C |
| 11 | Swagger + endpoint ẩn | `/swagger-ui/` → `/api/v1/system/diagnostics` | `swagger_exposed_hidden_diagnostics_endpoint` | A,B,C |
| 12 | nginx status | `/server-status` | *(config info)* | A,B,C |
| 13 | Admin 403 | `/admin/` → 403 ≠ 404 | *(recon)* | A,B,C |
| 14 | Anonymous FTP | `ftp` anon → `/backup/credentials.txt` | `anonymous_ftp_readable_backup_credentials` | **A,B** |
| 15 | Redis no-auth | `redis-cli … GET session:admin:token` | `unauthenticated_redis_exposed_key` | **A,B** |
| 16 | SSH/SMTP version cũ | `nmap -sV -p 2222,2525` | *(→ tra CVE)* | **A,B** |

**Dây chuyền dạy học:** `db.sql` (MD5 không salt) → crack ra mật khẩu → tái sử dụng;
`employee_directory.csv` (email) → phục vụ password spraying → **nối sang chuyên đề Authentication**.

</details>

---

## 3. Vì sao "chịu đấm" & an toàn
- nginx phục vụ tĩnh cho toàn bộ bề mặt discovery → chịu `ffuf -t 200` / feroxbuster.
- **Không** rate-limit / WAF / lockout; dữ liệu giả (mock creds + `IAW301{...}`); không gọi ra ngoài.
- Bẩn state → `docker compose down && up` (chế độ A) là sạch.

> **Lưu ý target chung (chế độ B):** Redis **ghi được** (không auth) → một sinh viên có thể
> `FLUSHALL`/sửa key làm ảnh hưởng cả lớp. Nếu host chung, giáo viên **restart định kỳ**
> (`docker compose restart redis`), hoặc cấp mỗi đội một instance (đổi port).
