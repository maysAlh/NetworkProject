from socket import *
import time

host = "127.0.0.1"
port = 8888

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))

url = input("Enter URL: ")
site = url.split("/")[2]

req = "GET " + url + " HTTP/1.1\r\n"
req += "Host: " + site + "\r\n\r\n"

start = time.time()

sock.send(req.encode())

res = b""
while True:
    data = sock.recv(1024)
    if not data:
        break
    res += data

end = time.time()
total = end - start

text = res.decode()

print("\n--- HTTP response ---")
print(text[:500])

if "Source: cache" in text:
    print("\nresponse from cache")
elif "Source: server" in text:
    print("\nresponse from server")
else:
    print("\nresponse source not identified")

print("\ntime taken:", total, "seconds")

sock.close()