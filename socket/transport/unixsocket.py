import os
import socket
from multiprocessing import reduction
import pickle

from .base import BaseTransport

class UNIXSocketTransport(BaseTransport):
    """
    Usage:
    
    cmd = 'ls -al'
    
    transport = UNIXSocketTransport()
    
    # returns ProcessResult instance.
    result = transport.run_cmd(cmd)
    """
    def __init__(self, socket_path='/tmp/exec-terminal-cmd', seperator='\r\n\r\n', listen_backlog=5, **kwargs):
        super(UNIXSocketTransport, self).__init__(**kwargs)

        self.socket_path = socket_path
        self.seperator = seperator
        self.listen_backlog = listen_backlog

    def server_get_connection(self):
        serversocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            os.remove(self.socket_path)
        except OSError:
            pass

        serversocket.bind(self.socket_path)
        serversocket.listen(self.listen_backlog)

        return serversocket

    def server_receive(self, connection):
        clientsocket, address = connection

        data = ''

        while self.seperator not in data:
            new_data = clientsocket.recv(1024)

            data += new_data

        data = data.split(self.seperator, 1)[0]

        return data

    def server_send(self, connection, data):
        clientsocket, address = connection

        clientsocket.sendall(data)

        try:
            clientsocket.close()
        except:
            pass

    def server_accept(self, connection):
        return connection.accept()

    def server_deserialize_connection(self, connection):
        return reduction.rebuild_socket(*connection[0][1]), connection[1]

    def server_serialize_connection(self, connection):
        return reduction.reduce_socket(connection[0]), connection[1]
    
    def client_get_connection(self):
        clientsocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        clientsocket.connect(self.socket_path)

        return clientsocket

    def client_send(self, connection, command_string):
        connection.sendall(command_string+self.seperator)

    def client_receive(self, connection):
        data = []

        while True:
            new_data = connection.recv(4096)

            if new_data:
                data.append(new_data)
            else:
                break

        data = ''.join(data)

        try:
            clientsocket.close()
        except:
            pass

        return data