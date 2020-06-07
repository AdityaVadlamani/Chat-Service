import socket
import getpass
import sys
from os import system, name
import pickle
import keyboard

HOST = '127.0.0.1' 	#localhost
PORT = 5001		#Arbitary non-priveleged port

#Global variable for the client-side STREAM socket  
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Function which clears the terminal window
def clear(): 
    if name == 'nt': 
        _ = system('cls') 
    else: 
        _ = system('clear') 

#Function which registers a user and returns upon completion a status
def Register(username, password):
	#Send a string to the server with the relevant info
	packet = 'register|' + username + '|' + password
	client_socket.sendall(packet.encode())
	#Recieve information from server about request
	data = client_socket.recv(1024)
	#Clear the screen and print the data from the server to the screen
	clear()					
	print(data.decode()+'\n')
	data = data.split(b' ')
	#Return 1 or 0 for success or failure
	if(data[-1].decode() == "registered"): return 1
	else: return 0

#Function which logs an existing user in
def Login(username, password):
	#Send a string to the server with the relevant info
	packet = 'login|' + username + '|' + password
	client_socket.sendall(packet.encode())
	#Recieve information from server about request
	data = client_socket.recv(1024)
	#Clear the screen and print the data from the server to the screen
	clear()
	print(data.decode()+'\n')
	data = data.split(b' ')
	#Return 1 or 0 for success or failure
	if(data[-1].decode() == "successful"): return 1
	elif(data[-1].decode() == "client"): return 2 
	else: return 0	

#Function which gets the list active users
def GetActiveUsers():
	#Send a string to the server with the relevant info
	client_socket.sendall(b"list")
	#Recieve information from server about request
	data = client_socket.recv(1024) 
	#Keep a client-side copy of the list of active users
	activeUsers = list(pickle.loads(data))
	#Return the list of active users
	return activeUsers

#Function which lists all the active users
def List(clientUsername):
        activeUsers = GetActiveUsers()
	#Loop through all the users and print them to the screen
        #Also, indicate which user is you
        for user in activeUsers:
                if(user == clientUsername):
                        print("YOU: " + user)
                else:
                        print(user)
        print()

#Function which send a message to another active user
def Message(username, msg):
	#Send a string to the server with the relevant info
	packet = "send|" + username + "|" + msg
	client_socket.sendall(packet.encode())
	#Recieve information from server about request and print it to the screen
	data = client_socket.recv(1024)
	print(data.decode())

#Function which logs a user off
def Logout(username):
	#Send a string to the server with the relevant info
	packet = 'logout|' + username
	client_socket.sendall(packet.encode())
	#Recieve information from server about request and print it to the screen
	data = client_socket.recv(1024)
	print(data.decode())
	#Close the client socket
	client_socket.close()

#Function which allows user to read messages that were sent to them
def ReadMessages():
	#Send a string to the server with the relevant info
	client_socket.sendall(b'read')
	data = client_socket.recv(4096)
	#Recieve information from server about request and print it to the screen
	data = pickle.loads(data)
	clear()
	for line in data:
		print(line)
	#Wait for key press to go back to menu
	input("\nPress ENTER to go back to the menu")	
	clear()

#Function which prints what the user can do
def Menu():
	print('  What you can do:  ')
	print('------------------------')
	print('(a) List online users')
	print('(b) Message a user')
	print('(c) Read Messages')
	print('(d) Logout\n')
	
#Main function
def main():
	#Try connect to the HOST and PORT
	try:
		print("Connecting...")
		client_socket.connect((HOST, PORT))
	except:
		print('Unable to establish a connection')
		sys.exit()

	#Upon success, start application 
	print("Connection established\n")	
	print("  Welcome to Aditya's Instant Messaging service!")
	print("--------------------------------------------------\n")
	print("Do you have an account with us?\n")
	
	#Try statement to catch any possible EOFErrors from input() calls
	try:	
		isRegistered = input("\t(Y)es\n\t(N)o\n")

		#Check if user is registered and do the appropriate action
		if (isRegistered.upper() == 'Y'):				
			rv = 0
			while rv != 1:
				print('Enter login information: \n')
				clientUsername = input("Username: ")
				pwd = getpass.getpass("Password: ")
				rv = Login(clientUsername, pwd)
		else:
			rv = 0
			while not rv:
				print('Enter Registration Information: \n')
				clientUsername = input("Username: ")
				if (' ' in clientUsername):
					clear()
					print("Whitespace in username is not allowed")
					continue
				pwd = getpass.getpass("Password: ")
				if(' ' in pwd):
					clear()
					print("Whitespace in password is not allowed")
					continue
				rv = Register(clientUsername, pwd)

		#Once the user has either successfully registered or logged in
		#Display the menu and ask the user what they would like to do
		Menu()
		choice = input('What would you like to do?')
		#Define an empty list to be used to store active users
		activeUsers = list()
		#Loop until user logs off, which will break the loop
		while 1:
			#User chooses to list active users
			if(choice.lower().strip() == 'a'):
				activeUsers = List(clientUsername)
				choice = input('\nWhat would you like to do?')
			#User chooses to send a message	
			elif(choice.lower().strip() == 'b'):
				activeUsers = GetActiveUsers()
				recipient = input("What is the recipient's username: ")
				if(recipient == clientUsername):
					print("Self-messaging is not currently supported")
				elif(recipient in activeUsers):
					msg = input("What would you like to send:\n\n")
					Message(recipient, msg)
				else:
					print(recipient + " not currently active")
				choice = input('\nWhat would you like to do?')	
			#User chooses to read their messages
			elif(choice.lower().strip() == 'c'):
				ReadMessages()
				Menu()
				choice = input('\nWhat would you like to do?')
			#User chooses to log off
			elif(choice.lower().strip() == 'd'):
				Logout(clientUsername)
				break
			else:
				choice = input("\nPlease enter a valid option: ")
	#If any EOFErrors occur print the error message	
	except EOFError as e: print(e)
	#Make sure to close the client_socket is not already
	finally: 
		if not client_socket: client_socket.close()
if __name__ == "__main__":
	main()
