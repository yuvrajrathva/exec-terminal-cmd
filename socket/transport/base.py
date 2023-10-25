import collections
import json
import subprocess
import multiprocessing
import logging # allows you to track events that occur while your program is running
# import socket

logger = logging.getLogger(__name__)

class ProcessResult(collections.namedtuple('ProcessResult', ['command_string', 'returncode', 'stdout', 'stderr'])):
    """
    command_string - The command that was run.
    returncode - The return code of the process.
    stdout - The stdout of the process.
    stderr - The stderr of the process.
    """
    def to_json(self, *args, **kwargs):
        return json.dumps(self._asdict(), *args, **kwargs)

def worker(self, connection):
    #logging.debug('worker: %s' % connection)
    return self.server_handle_client(connection)

class BaseTransport(object):
    """
    Usage:
    providing functionality common to all transports.
    """

    def __init__(self, pool_size=10):
        self.pool_size = pool_size

    def server_run_process(self, command_string):
        logger.debug('Executing: %s' % command_string)

        process = subprocess.Popen(
            command_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            close_fds=True
        )
        process_stdout, process_stderr = process.communicate()

        return process, process_stdout, process_stderr

    def server_get_connection(self):
        pass

    def server_receive(self, connection):
        pass

    def server_send(self, connection, data):
        pass

    def server_handle_client(self, connection):
        logging.debug('server_handle_client %s' % connection)
        connection = self.server_deserialize_connection(connection)
        logging.debug('deserialized connection: %s' % connection)

        command_string = self.server_receive(connection)
        logging.debug('received command string: %s' % command_string)

        process, process_stdout, process_stderr = self.server_run_process(command_string)

        ret_data = ProcessResult(
            command_string,
            process.returncode,
            process_stdout,
            process_stderr,
        )

        ret_data = ret_data.to_json()

        self.server_send(connection, ret_data)

    def server_accept(self, connection):
        pass

    def server_deserialize_connection(self, connection):
        return connection

    def server_serialize_connection(self, connection):
        return connection
    
    def run_server(self, max_accepts=1000):
        serverconnection = self.server_get_connection()

        logger.info('Accepting connections: %r' % (serverconnection,))

        pool = multiprocessing.Pool(self.pool_size)

        connections = []

        while max_accepts:
            connection = self.server_accept(serverconnection)

            logger.info('Accepted connection from: %r' % (connection,))

            result = pool.apply_async(worker, [self, self.server_serialize_connection(connection)])
            connection = None

            max_accepts -= 1

    def client_get_connection(self):
        pass

    def client_send(self, connection, command_string):
        pass

    def client_receive(self, connection):
        pass

    def run_cmd(self, command_string):
        connection = self.client_get_connection()

        self.client_send(connection, command_string)

        data = self.client_receive(connection)

        data = json.loads(data)

        return ProcessResult(**data)
    