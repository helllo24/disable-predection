import socket

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        res = s.connect_ex((host, int(port)))
        s.close()
        return res == 0
    except Exception as e:
        return False

print("Port 3306 on 127.0.0.1 open?", check_port("127.0.0.1", 3306))
print("Port 3306 on localhost open?", check_port("localhost", 3306))
