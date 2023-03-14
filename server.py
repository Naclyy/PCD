import socket
import argparse


def runTCPStopWait(HOST, PORT, BUFFER_SIZE):
    received_bytes = 0
    number_of_messages = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    # print(f"Server started on {HOST}:{PORT}")
    # print(f'Client with {client_address} is connected')
    
    # to make sure we don't have data loss
    message_size_bytes = client_socket.recv(BUFFER_SIZE)
    message_size = int.from_bytes(message_size_bytes, byteorder='big')
    
    
    while received_bytes < message_size:
        data = client_socket.recv(BUFFER_SIZE)
        if not data:
            break
        received_bytes += len(data)
        number_of_messages += 1
        client_socket.send(b'ACK')
    print(
        f"Protocol: TCP - Stop-Wait, Messages received: {number_of_messages}, Bytes received: {received_bytes}")
    
    # We send ACK before closing the server in case the client is stuck in loop
    client_socket.send(b'ACK')
    # print("Client disconnected.")
    server_socket.close()


def runTCPStreaming(HOST, PORT, BUFFER_SIZE):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    client_socket, client_address = server_socket.accept()
    # print(f"Server started on {HOST}:{PORT}")
    # print(f'Client with {client_address} is connected')
    number_of_messages = 0
    recieved_data = 0
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        if not data or data == b'done':
            break
        recieved_data += len(data)
        number_of_messages += 1
    print(
        f"Protocol: TCP - Streaming, Messages received: {number_of_messages}, Bytes received: {recieved_data}")
    client_socket.send(b"Message received.")
    print("Client disconnected.")
    server_socket.close()

def runUDPStopWait(HOST, PORT, BUFFER_SIZE):
    received_bytes = 0
    number_of_messages = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    # print(f"Server started on {HOST}:{PORT}")
    while True:
        data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        received_bytes += len(data)
        number_of_messages += 1
        server_socket.sendto(b"ACK", client_address)
        if data == b'done':
            break
        if not data:
            break
    print(
        f"Protocol: UDP - StopWait, Messages received: {number_of_messages}, Bytes received: {received_bytes}")
    print("Client disconnected.")
    server_socket.close()

def runUDPStreaming(HOST, PORT, BUFFER_SIZE):
    received_bytes = 0
    number_of_messages = 0
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (HOST, PORT)
    server_socket.bind(server_address)
    # print(f"Server started on {HOST}:{PORT}")
    server_socket.setsockopt(
        socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000000)  # 1Gb
    while True:
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        received_bytes += len(data)
        number_of_messages += 1
        if not data:
            break
        if data == b'done':
            break
        server_socket.sendto(b'ack', address)
    print(
        f"Protocol: UDP - Streaming, Messages received: {number_of_messages}, Bytes received: {received_bytes}")
    print("Client disconnected.")
    server_socket.close()


def test():
    BUFFER = 65000
    MESSAGE_SIZE = [10 * 1024 * 1024, 100 * 1024 * 1024, 500 * 1024 * 1024, 1000 * 1024 * 1024, 2000 * 1024 * 1024]
    avg_number_of_messages = 0 
    avg_received_bytes = 0
    nr = 100
    for j in MESSAGE_SIZE:
        print(j)
        for i in range(0, nr):
            number_of_messages, received_bytes = runUDPStreaming('localhost', 1235, BUFFER)
            avg_number_of_messages += number_of_messages
            avg_received_bytes += received_bytes
        print(" 100 runs ")
        print(avg_number_of_messages / nr, avg_received_bytes / nr)
        avg_number_of_messages1 = 0 
        avg_received_bytes1 = 0
        nr1 = 10
        for i in range(0, nr1):
            number_of_messages1, received_bytes1 = runUDPStreaming('localhost', 1235, BUFFER)
            avg_number_of_messages1 += number_of_messages1
            avg_received_bytes1 += received_bytes1
        print("10 runs " )
        print(avg_number_of_messages1 / nr1, avg_received_bytes1 / nr1)
    
    # runTCPStreaming('localhost', 1235, 65000)
    # runUDPStopWait('localhost', 1235, 65000)
    # runUDPStreaming('localhost', 1235, 65000)


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
