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

class PopenProxy(object):
    # returncode = None

    def __init__(self, transport, args):
        self._transport = transport
        self._args = args

        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.pid = None
        self.returncode = None

        self.connection = self._transport.client_get_connection()

        self._transport.client_send(self.connection, args)

    def communicate(self, input=None):
        if self.returncode is not None:
            raise Exception('Already Returned')

        input = input or ''

        self._transport.client_send(self.connection, input)

        data, returncode = self._transport.split_data(self._transport.client_recv(self.connection))

        self.returncode = int(returncode)
        self._transport.client_close(self.connection)

        stdout = []
        stderr = []

        for line in data.split('\r\n'):
            if ":" in line:
                std_id, msg = line.split(":", 1)
                if std_id == "0":
                    stdout.append(msg)
                if std_id == "1":
                    stderr.append(msg)

        stdout = ''.join(stdout)
        stderr = ''.join(stderr)

        return stdout, stderr
    
def worker(self, connection):
    #logging.debug('worker: %s' % connection)
    return self.server_handle_client(connection)

class BaseTransport(object):
    """
    Usage:
    providing functionality common to all transports.
    """
    SEPERATOR = '\r\n\r\n'
    STDOUT_PREFIX = '0:'
    STDERR_PREFIX = '1:'

    def __init__(self, pool_size=10):
        self.pool_size = pool_size

    # def server_run_process(self, command_string):
    #     logger.debug('Executing: %s' % command_string)

    #     process = subprocess.Popen(
    #         command_string,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         shell=True,
    #         close_fds=True
    #     )
    #     process_stdout, process_stderr = process.communicate()

    #     return process, process_stdout, process_stderr

    def server_get_connection(self):
        pass

    def server_recv(self, connection):
        pass

    def server_send(self, connection, data):
        pass

    def server_send_returncode(self, connection, data):
        pass

    def server_send_stdout_stderr(self, connection, stdout, stderr):
        self.server_send(connection, self.STDOUT_PREFIX+stdout)
        self.server_send(connection, self.STDERR_PREFIX+stderr)

    def server_send_returncode(self, connection, returncode):
        self.server_send(connection, self.SEPERATOR+str(returncode))

    def server_close(self, connection):
        pass

    def split_data(self, data, num=1):
        data = [s for s in data.split(self.SEPERATOR, num) if s]
        remainder = ''

        if len(data) > num:
            data, remainder = data
        else:
            data = data[0]
        
        return data, remainder
    
    def server_split_data(self, data):
        return data.split(self.SEPERATOR, 1)
    
    def server_handle_client(self, connection):
        logging.debug('server_handle_client %s' % connection)
        connection = self.server_deserialize_connection(connection)
        logging.debug('deserialized connection: %s' % connection)

        command_string, process_input = self.server_split_data(self.server_recv(connection))
        logging.debug('received command string: %s' % command_string)

        process = subprocess.Popen(
            command_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            close_fds=True
        )

        process_input = process_input or None

        process_stdout, process_stderr = process.communicate(input=process_input)

        self.server_send_stdout_stderr(connection, process_stdout, process_stderr)

        self.server_send_returncode(connection, process.returncode)

        self.server_close(connection)

    def server_accept(self, serverconnection):
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

    def client_recv(self, connection):
        pass

    def client_close(self, connection):
        pass

    def run_cmd(self, command_string):
        process = self.Popen(command_string)

        stdout = ''
        stderr = ''

        return process, stdout, stderr

    def Popen(self, args, *options, **kwargs):
        return PopenProxy(self, args)
    