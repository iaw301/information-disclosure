import socket
import threading
import time

# Banner phien ban CU co chu dich -> nmap -sV doc duoc -> tra CVE.
BANNERS = {
    2222: b"SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.10\r\n",
    2525: b"220 mail.nexus-core.local ESMTP Postfix (Ubuntu 2.11.0-1ubuntu1)\r\n",
}


def serve(port, banner):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    s.listen(50)
    while True:
        try:
            conn, _ = s.accept()
        except OSError:
            continue
        try:
            conn.sendall(banner)
            conn.settimeout(2)
            try:
                conn.recv(1024)
            except OSError:
                pass
        except OSError:
            pass
        finally:
            conn.close()


if __name__ == "__main__":
    for p, b in BANNERS.items():
        threading.Thread(target=serve, args=(p, b), daemon=True).start()
    print("[banners] serving fake service banners on", list(BANNERS.keys()), flush=True)
    while True:
        time.sleep(3600)
