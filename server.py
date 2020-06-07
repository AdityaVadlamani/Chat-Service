import socket
import select
import pickle
from datetime import datetime
from bidict import bidict
import os

HOST = '127.0.0.1'       #localhost
PORT = 5001              # Arbitrary non-privileged port

#Function which calls the appropariate helper functions to complete tasks
def executeTask(conn, data, activeUsers):
	#Split the data by | 
	data = data.split("|")
	#User wants to register
	if(data[0] == "register"):
		#Add the user and send the appropriate response back to the client
		if(addNewUser(data[1], data[2])):	
			conn.sendall(b"User successfully registered")
			#Add user to list of active users
			activeUsers[data[1]] = conn
		else:
			resp = "'" + data[1] + "' is already taken"
			conn.sendall(resp.encode())
	#User wants to log in
	elif(data[0] == "login"):
		#Check if the user exists and send the appropriate response back to the client
		rv = checkIfUserExistsForLogin(data[1], data[2], activeUsers)
		if(rv == 1):
			conn.sendall(b"Login successful")
			#Add user to list of active users
			activeUsers[data[1]] = conn
		elif (rv == 2):
			conn.sendall(b"User is logged in on another client")
		else:
			conn.sendall(b"Invalid credentials")
	#User wants to send a message
	elif(data[0] == "send"):
		#Get current time for timestamp of message
		now = datetime.now()
		#Check if username of recipient exists. If so, send the message
		#Send the client an appropriate response in either case
		if(checkIfUserExists(data[1])):
			addMessageToInbox(activeUsers, activeUsers.inverse[conn], data[1], now, data[2])
			conn.sendall(b"Message sent")
		else:
			conn.sendall(b"Unable to send")
	#User wants to log off
	elif(data[0] == "logout"):
		#Delete the user from list of active users
		del activeUsers[data[1]]
		#Send the client back with response
		conn.sendall(b"Logging off... Bye Bye!")
	#User wants to list the active users
	elif(data[0] == "list"):
		#Send the list of the users which are the keys in the activeUsers dictionary	
		if list(activeUsers.keys()):
			conn.sendall(pickle.dumps(list(activeUsers.keys())))
	
	#User wants to read their messages
	elif(data[0] == 'read'):
		#Open their file for reading and send every line in the file
		with open("Users/"+activeUsers.inverse[conn] +".txt", 'r') as f:
			lines = f.readlines()
		if lines:
			conn.sendall(pickle.dumps(lines))

#Function which adds a message to the user's inbox
def addMessageToInbox(activeUsers, sender, recipient, time, msg):
	#Open the recipient's file and write message
	with open("Users/"+ recipient + ".txt", "r+") as f:
		f.write("From: "+ sender+"\t")
		f.write("Sent on: "+time.strftime("%m/%d/%y %I:%M %p")+"\n")
		f.write(msg+"\n")

#Function which adds a new user		
def addNewUser(username, password):
	#Check if username exists already
	with open("listOfUsers.txt", "r") as f:
		lines = f.readlines()
	for line in lines:
		if(line.split(" ")[0] == username):
			return 0
	#If not, then add username and password to running list
	with open("listOfUsers.txt","a") as f:
		f.write(username + " " + password +'\n')	
	#Create a file for the new user for where they can have messages stored
	with open("Users/"+username +".txt", "w") as f: pass
	return 1

#Function which checks if the username and password given exist and thus log the user in
def checkIfUserExistsForLogin(username, password, activeUsers):
	#Check to see if the user is already logged on
	if(username in activeUsers.keys()): return 2
	#Get all the users
	with open("listOfUsers.txt", "r") as f:
		lines = f.readlines()
	#Loop through and check if there is one with correct username and passowrd pair
	for line in lines:
		cred = line.split(" ")
		if(cred[0] == username and cred[1] == password + '\n'):
			return 1
	return 0

#Function which checks if the username and password given exist and thus log the user in
def checkIfUserExists(username):
        #Get all the users
        with open("listOfUsers.txt", "r") as f:
                lines = f.readlines()
        #Loop through and check if there is one with correct username and passowrd pair
        for line in lines:
                cred = line.split(" ")
                if(cred[0] == username):
                        return 1
        return 0

#Main function
def main():
	#A bidirectional dictionary for connecting usernames and socket connection
	activeUsers = bidict({})

	#Check if listOfUsers.txt and Users directory exist, if not create them
	if not os.path.exists("listOfUsers.txt"):
		with open('listOfUsers.txt', 'w'): pass
	if not os.path.exists('Users'):
		os.mkdir('Users')

	#Create a server STREAM socket to HOST and PORT
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
		#Configure server socket to not block, bind to the HOST and PORT,
		#and a buffer of 5 unaccepted connections before accepting new 
		#connections
		server_socket.setblocking(0)
		server_socket.bind((HOST, PORT))
		server_socket.listen(5)
		#Allow socket to reuse address
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#Add server socket to a connection list which'll keep track of the connections
		connectionList = [server_socket]
		while 1:
			#Get the sockets ready for reading from connectionList
			readSd, writeSd, errorSd = select.select(connectionList, [],[],0)
			for sd in readSd:
				if(sd == server_socket):
					#Get a connection to the server
					conn, addr = server_socket.accept()
					#If the file number is non negative then add it to the
					#connectionList and set it to non-blocking
					if sd.fileno() >= 0: 
						connectionList.append(conn)
						conn.setblocking(0)
				else:
					#Try to read data from the (client) socket and
					#call executeTask
					try:
						data = sd.recv(1024)
						if data:
							data = data.decode()
							executeTask(sd, data, activeUsers)		
					except:
						#Handle when data was not received from the socket
						del (activeUsers.inverse[sd])
						sd.close()
						connectionList.remove(sd)
if __name__ == "__main__":
	main()
