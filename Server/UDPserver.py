import socket
import threading
import os
import random
import sys
import base64
def handleFileTransmission(filename, client_address, port):
    try:
        # ✅ 创建新的 socket 并绑定新端口
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.bind(("", port))
        print(f"[THREAD] Serving {filename} to {client_address} on port {port}")

        with open(filename, "rb") as f:
            while True:
                request_data, _ = data_socket.recvfrom(4096)
                request = request_data.decode().strip()
                parts = request.split(" ")

                if parts[0] == "FILE" and parts[2] == "CLOSE":
                    # ✅ 收到关闭请求
                    msg = f"FILE {filename} CLOSE_OK"
                    data_socket.sendto(msg.encode(), client_address)
                    print(f"[CLOSE] File transfer of {filename} completed.")
                    break

                if len(parts) >= 8 and parts[0] == "FILE" and parts[2] == "GET":
                    # ✅ 收到数据块请求
                    start = int(parts[5])
                    end = int(parts[7])
                    f.seek(start)
                    data = f.read(end - start + 1)
                    encoded_data = base64.b64encode(data).decode()
                    msg = f"FILE {filename} OK START {start} END {end} DATA {encoded_data}"
                    data_socket.sendto(msg.encode(), client_address)
    except Exception as e:
        print(f"[THREAD ERROR] {e}")
    finally:
        data_socket.close()

# 🚀 启动方式：python3 UDPserver.py 51234
if len(sys.argv) != 2:
    print("Usage: python3 UDPserver.py <port>")
    sys.exit(1)

server_port = int(sys.argv[1])

# 🧱 创建主 UDP socket，监听客户端的 DOWNLOAD 请求
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", server_port))

print(f"[SERVER] Listening on port {server_port}...")

# ✅ 循环监听请求
while True:
    try:
        request_data, client_address = server_socket.recvfrom(4096)
        message = request_data.decode().strip()
        request = request_data.decode().strip()
        print(f"[RECEIVED REQUEST] {request} from {client_address}")
        parts = request.split(" ")

        if len(parts) != 2 or parts[0] != "DOWNLOAD":
            print("[ERROR] Invalid request format.")
            continue

        filename = parts[1]
        if not os.path.exists(filename):
            error_msg = f"ERR {filename} NOT_FOUND"
            server_socket.sendto(error_msg.encode(), client_address)
            print(f"[ERROR] {filename} not found.")
            continue

        file_size = os.path.getsize(filename)
        new_port = random.randint(50000, 51000)

        ok_msg = f"OK {filename} SIZE {file_size} PORT {new_port}"
        server_socket.sendto(ok_msg.encode(), client_address)
        print(f"[OK] Sent file info for {filename} with size {file_size} bytes on port {new_port}")
        threading.Thread(
            target=lambda: handleFileTransmission(filename, client_address, new_port)
        ).start()

    except Exception as e:
        print(f"[EXCEPTION] {e}")

