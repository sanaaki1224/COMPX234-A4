import socket
import sys
import base64
import os
print("✅ Client started")

# 重试功能：发送并接收（带超时和重发）
def sendAndReceive(sock, message, server_address):
    timeout = 0.5
    retries = 0
    while retries < 5:
        try:
            sock.settimeout(timeout)
            sock.sendto(message.encode(), server_address)
            response, _ = sock.recvfrom(65535)
            return response.decode()
        except socket.timeout:
            print(f"[TIMEOUT] Retrying ({retries+1})...")
            retries += 1
            timeout *= 2
    print("[FAILED] No response after 5 retries.")
    return None

# 启动方式：python3 UDPclient.py <hostname> <port> files.txt
if len(sys.argv) != 4:
    print("Usage: python3 UDPclient.py <hostname> <port> <filelist>")
    sys.exit(1)

hostname = sys.argv[1]
server_port = int(sys.argv[2])
filelist_path = sys.argv[3]

# 创建 socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (hostname, server_port)

# 读取文件列表

with open(filelist_path, "r") as f:
    files = [line.strip() for line in f if line.strip()]
print("✅ Loaded file list:", files)

for filename in files:
    print(f"\n[DOWNLOAD] Requesting file: {filename}")
    msg = f"DOWNLOAD {filename}"
    response = sendAndReceive(sock, msg, server_address)

    if response is None:
        continue
    if response.startswith("ERR"):
        print(f"[ERROR] {response}")
        continue

    parts = response.split(" ")
    size = int(parts[3])
    port = int(parts[5])
    print(f"[INFO] Size: {size} bytes | Port: {port}")

    # 新的 socket 用于传输数据
    server_ip = socket.gethostbyname(hostname)
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_address = (server_ip, port)

    received_bytes = 0
    block_size = 1000
    file_data = bytearray(size)

    while received_bytes < size:
        start = received_bytes
        end = min(start + block_size - 1, size - 1)
        data_request = f"FILE {filename} GET START {start} END {end}"
        data_response = sendAndReceive(data_socket, data_request, data_address)

        if data_response is None:
            break
        data_parts = data_response.split("DATA ")
        if len(data_parts) != 2:
            break
        encoded_data = data_parts[1]
        binary_data = base64.b64decode(encoded_data)
        file_data[start:end + 1] = binary_data
        received_bytes += len(binary_data)
        print("*", end="", flush=True)

    # 写入文件
    with open(filename, "wb") as f:
        f.write(file_data)

    # 发送关闭请求
    close_msg = f"FILE {filename} CLOSE"
    sendAndReceive(data_socket, close_msg, data_address)
    data_socket.close()
    print(f"\n[FINISHED] File {filename} downloaded.")

sock.close()
