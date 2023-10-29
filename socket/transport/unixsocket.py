import os
import socket
from multiprocessing import reduction
import pickle
import errno

from .base import BaseTransport

class UNIXSocketTransport(BaseTransport):
    """
    Usage:
    
    cmd = 'ls -al'
    
    transport = UNIXSocketTransport()
    
    process, stdout, stderr = transport.run_cmd('ls -al')
    """
    SEPERATOR = '\r\n\r\n'
    STDOUT_PREFIX = '0:'
    STDERR_PREFIX = '1:'

    def __init__(self, socket_path='/tmp/exec-terminal-cmd', listen_backlog=5, **kwargs):
        super(UNIXSocketTransport, self).__init__(**kwargs)

        self.socket_path = socket_path
        # self.seperator = seperator
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

    def server_recv(self, connection):
        clientsocket, address = connection

        data = ''

        while data.count(self.SEPERATOR) < 2:
            new_data = clientsocket.recv(4096)
            data += new_data

        return data

    def server_send(self, connection, data):
        clientsocket, address = connection

        clientsocket.sendall(data)

    def server_close(self, connection):
        clientsocket, address = connection
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

    def client_send(self, connection, data):
        connection.sendall(data+self.SEPERATOR)

    def client_recv(self, connection):
        data = ''

        while data.count(self.SEPERATOR) < 2:
            new_data = connection.recv(4096)
            data += new_data

        return data

    def client_close(self, connection):
        try:
            connection.close()
        except:
            pass
