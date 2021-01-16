'''Server for multithreaded (asynchronous) chat application.'''
import pickle

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

class Message:
    def __init__(self, msg):
        self.msg = 0

class Client:
    def __init__(self, name, key):
        self.name = name
        self.key = key
        self.dest = ''
        self.dest_key = 0
    def setDest(self, name, key):
        self.dest = name

def accept_incoming_connections():
    '''Sets up handling for incoming clients.'''
    while True:
        client, client_address = SERVER.accept()
        print('%s:%s has connected.' % client_address)
        client.send(pickle.dumps('System: Hey new user. Please enter your username'))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    '''Handles a single client connection.'''

    while True:
        name = pickle.loads(client.recv(BUFSIZ))
        if name == 'System':
            client.send(pickle.dumps('System: No one can choose "System"'))
        else:
            found = False
            for x in clients:
                if clients[x].name == name:
                    found = True
                    client.send(pickle.dumps('System: This username already exists'))
                    break
            if not found:
                break

    client.send(pickle.dumps('Please send your key'))
    key = pickle.loads(client.recv(BUFSIZ))
    if key == '{quit}':
        return

    welcome = 'System: Welcome %s! Please choose your destination' % name
    client.send(pickle.dumps(welcome))
    user = Client(name, key)
    userLen = len(name)+2
    clients[client] = user

    while True:
        msg = pickle.loads(client.recv(BUFSIZ))
        if type(msg) != str:
            if user.dest != '':
                user.dest.send(pickle.dumps(msg))
            else:
                client.send(pickle.dumps('System: You should first choose your destination'))
        else:
            if msg.startswith(name + ': @') and len(msg)>userLen+1:
                dest = getUser(msg[userLen+1:])
                if dest:
                    user.dest = dest
                    dest = clients[dest]
                    client.send(pickle.dumps(dest.key))
                    client.send(pickle.dumps('System: You\'ve been connected to '+dest.name))
                else:
                    client.send(pickle.dumps('System: This user doesn\'t exist'))

            elif msg == '{quit}':
                client.close()
                del clients[client]

                if user.dest != '':
                    user.dest.send(pickle.dumps('Destination left'))
                    user.dest.send(pickle.dumps('System: %s has left the chat' % name))
                    getUserBySock(user.dest).dest = ''
                break

def getUser(user):
    for sock in clients:
        if clients[sock].name == user:
            return sock
    return None

def getUserBySock(sock):
    if sock in clients:
        return clients[sock]
    return None
        
clients = {}
addresses = {}

HOST = '127.0.0.1'
PORT = 33000
BUFSIZ = 4096
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == '__main__':
    SERVER.listen(5)
    print('Waiting for connection...')
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
