import socket
import threading
import os

clients = {}

def handle_client(client_socket, client_addr):
    print(f"New connection from {client_addr}")

    try:
        # Prompt the client to enter their unique name
        client_name = client_socket.recv(1024).decode()
        clients[client_socket] = client_name

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            # Check if the data is a file or a text message
            if data.startswith(b"FILE:"):
                # Extract the file name and size from the data
                file_info = data[5:].decode()
                file_name, file_size = file_info.split(",")

                # Receive the file data in chunks and save it to a new file
                file_size = int(file_size)
                received_size = 0
                with open(file_name, "wb") as file:
                    while received_size < file_size:
                        data = client_socket.recv(1024)
                        file.write(data)
                        received_size += len(data)

                print(f"Received file '{file_name}' from {client_name}")
            else:
                message = data.decode()
                print(f"Received message from {client_name}: {message}")

                # Broadcast the message to all other connected clients
                broadcast_message(f"{client_name}: {message}", client_socket)

    except Exception as e:
        print(f"Error handling connection with {client_name}: {str(e)}")

        # Remove the client from the clients dictionary
        del clients[client_socket]

    client_socket.close()
    print(f"Connection with {client_name} closed")

def broadcast_message(message, sender_socket):
    for client_socket in clients:
        if client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except Exception as e:
                print(f"Error broadcasting message to a client: {str(e)}")
                client_socket.close()
                del clients[client_socket]

def main():
    server_ip ="192.168.43.237"  # Replace with the static IP of the server
    server_port = 43210  # Replace with the desired server port number

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)

    print("Server is listening for incoming connections...")

    while True:
        client_socket, client_addr = server_socket.accept()

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
        client_thread.start()

if __name__ == "__main__":
    main()
