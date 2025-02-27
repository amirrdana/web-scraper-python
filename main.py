import socket

HOST = 'www.google.com'
PORT = 80

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)

client_socket.connect(server_address)