import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('10.13.169.116', 5005)

print("Starting up on %s port %s" % server_address)

sock.bind(server_address)

sock.listen(1)

while True:
	print("Waiting for connection")
	connection, client_address = sock.accept()

	try:
		print("Connection from " + str(client_address))

		while True:
			data = connection.recv(16)
			print("Received %s" % data)
			if data:
				print("Echoing")
				connection.sendall(data)
			else:
				print("No more data to echo")
				break
	finally:
		connection.close()
