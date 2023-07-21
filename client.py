import socket
import threading
import os

def receive_message(client_socket, client_name):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

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

                print(f"Received file '{file_name}' from the server")
            else:
                message = data.decode()
                print(message)

        except Exception as e:
            print("Error receiving message:", str(e))
            break

def send_file(client_socket, file_path):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    client_socket.send(f"FILE:{file_name},{file_size}".encode())

    # Send the file data in chunks
    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024)
            if not data:
                break
            client_socket.send(data)

def main():
    server_ip = "192.168.1.1"  # Replace with the IP address of the server
    server_port = 43210  # Replace with the server port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    print("Connected to the server")

    # Prompt the user to enter a unique name
    client_name = input("Enter your unique name: ")
    client_socket.send(client_name.encode())

    # Start a new thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_message, args=(client_socket, client_name))
    receive_thread.start()

    while True:
        print("Enter 'text:<message>' to send a text message.")
        print("Enter 'file:<file_path>' to send a file.")
        print("Enter 'bye' to exit.")
        command = input()

        if command.lower() == "bye":
            client_socket.send(command.encode())
            break
        elif command.startswith("text:"):
            message = command[5:]
            client_socket.send(message.encode())
        elif command.startswith("file:"):
            file_path = command[5:]
            if os.path.exists(file_path) and os.path.isfile(file_path):
                send_file(client_socket, file_path)
            else:
                print("Invalid file path. Please try again.")

    client_socket.close()
    print("Connection closed")

if __name__ == "__main__":
    main()
