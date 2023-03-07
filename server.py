import socket
import argparse


def runTCPStopWait(HOST, PORT, BUFFER_SIZE):
    received_bytes = 0
    number_of_messages = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    print(f"Server started on {HOST}:{PORT}")
    print(f'Client with {client_address} is connected')
    message_size_bytes = client_socket.recv(BUFFER_SIZE)
    message_size = int.from_bytes(message_size_bytes, byteorder='big')
    while received_bytes < message_size:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break
        received_bytes += len(data)
        number_of_messages += 1
        client_socket.send(b'OK')
    print(
        f"Protocol: TCP - Stop-Wait, Messages received: {number_of_messages}, Bytes received: {received_bytes}")
    client_socket.send(b'OK')
    print("Client disconnected.")
    server_socket.close()


def runTCPStreaming(HOST, PORT, BUFFER_SIZE):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    print(f"Server started on {HOST}:{PORT}")
    print(f'Client with {client_address} is connected')
    while True:
        message_size_bytes = client_socket.recv(8)
        if not message_size_bytes:
            break
        message_size = int.from_bytes(message_size_bytes, byteorder='big')
        received_bytes = 0
        number_of_messages = 0
        message = b''
        while received_bytes < message_size:
            data = client_socket.recv(BUFFER_SIZE)
            message += data
            received_bytes += len(data)
            number_of_messages += 1
        print(
            f"Protocol: TCP - Streaming, Messages received: {number_of_messages}, Bytes received: {message_size}")
        client_socket.send(b"Message received.")
    print("Client disconnected.")
    server_socket.close()


def runUDPStopWait(HOST, PORT, BUFFER_SIZE):
    done = False
    received_bytes = 0
    number_of_messages = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"Server started on {HOST}:{PORT}")
    while not done:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        received_bytes += len(data)
        number_of_messages += 1
        server_socket.sendto(b"ACK", client_address)
        if data == b'done':
            done = True
        if not data:
            break
    print(
        f"Protocol: UDP - StopWait, Messages received: {number_of_messages}, Bytes received: {received_bytes}")
    print("Client disconnected.")
    server_socket.close()


def runUDPStreaming(HOST, PORT, BUFFER_SIZE):
    done = False
    received_bytes = 0
    number_of_messages = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (HOST, PORT)
    server_socket.bind(server_address)
    print(f"Server started on {HOST}:{PORT}")
    server_socket.setsockopt(
        socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000000)  # 1Gb
    while not done:
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        received_bytes += len(data)
        number_of_messages += 1
        if not data:
            break
        if data == b'done':
            done = True
        server_socket.sendto(b'ack', address)
    print(
        f"Protocol: UDP - Streaming, Messages received: {number_of_messages}, Bytes received: {received_bytes}")
    print("Client disconnected.")
    server_socket.close()


def main():
    runTCPStopWait('localhost', 1235, 32500)
    # runTCPStreaming('localhost', 1235, 32500)
    runUDPStopWait('localhost', 1235, 32500)
    runUDPStreaming('localhost', 1235, 32500)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Server')
    parser.add_argument('-c', '--connection', type=str, choices=[
                        'TCP', 'UDP'], required=True, help='Conexion type: TCP or UDP')
    parser.add_argument('-ip', '--ip_address', type=str,
                        required=True, help='IP address of the server')
    parser.add_argument('-p', '--port', type=int, required=True,
                        help='PORT of the server')
    parser.add_argument('-t', '--transfer_mode', type=str, choices=[
                        'streaming', 'stop-and-wait'], required=True, help='Transfer mechanism: streaming or stop-and-wait')
    parser.add_argument('-b', '--buffer', type=int, required=True,
                        help='The size of buffer')
    args = parser.parse_args()

    if args.connection == 'TCP':
        protocol = 'TCP'
        if args.transfer_mode == 'streaming':
            runTCPStreaming(args.ip_address, args.port,
                            args.buffer)
        elif args.transfer_mode == 'stop-and-wait':
            runTCPStopWait(args.ip_address, args.port,
                           args.buffer)
    elif args.connection == 'UDP':
        protocol = 'UDP'
        if args.transfer_mode == 'streaming':
            runUDPStreaming(args.ip_address, args.port,
                            args.buffer)
        elif args.transfer_mode == 'stop-and-wait':
            runUDPStopWait(args.ip_address, args.port,
                           args.buffer)
