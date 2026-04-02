import socket
import os
import hashlib

HOST= "127.0.0.1"
PORT= 8888

class Server:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.cache_dir = "cache_data"
        self.blocked_sites = ["ads", "social"] 
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK.STREAM (TCP)
        server_sock.bind((self.HOST, self.PORT))
        server_sock.listen(5)
        print(f"[*] Proxy Server started on {self.HOST}:{self.PORT}")

        try:
            while True:
                client_conn, addr = server_sock.accept()
                self.handle_request(client_conn)
        except KeyboardInterrupt:
            print("\n[*] Stopping Server...")
        finally:
            server_sock.close()

    def handle_request(self, client_conn):
        try:
            request = client_conn.recv(4096).decode()
            if not request: return
            
            first_line = request.split('\n')[0]
            url = first_line.split(' ')[1]
            print(f"[>] Request for: {url}")

            # Firewall
            if any(site in url for site in self.blocked_sites):
                print(f"[!] Blocked: {url}")
                response = "HTTP/1.1 403 Forbidden\r\n\r\nBlocked by Firewall"
                client_conn.send(response.encode())
                return

            # Caching
            filename = hashlib.md5(url.encode()).hexdigest() + ".txt"
            filepath = os.path.join(self.cache_dir, filename)

            if os.path.exists(filepath):
                # Cache HIT
                print(f"[*] Cache HIT for: {url}")
                with open(filepath, "rb") as f:
                    data = f.read()
                client_conn.send(b"HTTP/1.1 200 OK\r\nX-Source-Cache: HIT\r\n\r\n" + data)
            else:
                # Cache MISS
                print(f"[*] Cache MISS for: {url}")
                remote_data = self.fetch_from_internet(url)
                
                if remote_data:
                    with open(filepath, "wb") as f:
                        f.write(remote_data)
                    client_conn.send(b"HTTP/1.1 200 OK\r\nX-Source-Cache: MISS\r\n\r\n" + remote_data)

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            client_conn.close()

    def fetch_from_internet(self, url):
        try:
            host = url.replace("http://", "").split("/")[0]
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.connect((host, 80))
            
            request = f"GET {url} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            remote_sock.send(request.encode())

            response = b""
            while True:
                data = remote_sock.recv(4096)
                if not data: break
                response += data
            
            remote_sock.close()
            if b"\r\n\r\n" in response:
                return response.split(b"\r\n\r\n", 1)[1]
            return response
        except:
            return None

if __name__ == "__main__":
    proxy = Server(HOST , PORT)
    proxy.start()