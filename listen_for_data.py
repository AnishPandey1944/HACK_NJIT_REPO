import socket

# Use 0.0.0.0 to bind to all available interfaces, or replace with your local IP
host, port = '10.196.232.1', 12345  
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))
sock.listen(1)
print("Waiting for connection...")

conn, addr = sock.accept()
print(f"Connected to {addr}")
while True:
    data = conn.recv(1024).decode('utf-8')
    if not data:
        break
    x, y = map(int, data.strip().split(','))
    print(f"Received coordinates: x={x}, y={y}")
conn.close()
sock.close()
