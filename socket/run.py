# Unix sockets are used to communicate between processes on the same machine.
import sys # which provides access to some variables used or maintained by the Python interpreter and to functions that interact strongly with the interpreter, including the command-line arguments.

if __name__ == '__main__':
    from .transports.unixsocket import UNIXSocketTransport

    transport = UNIXSocketTransport()


    if sys.argv[1] == 'server': # sys.argv is a list in Python, which contains the command-line arguments passed to the script.
        transport.run_server() #start a Unix socket server
    else:
        print(transport.run_cmd(sys.argv[1]).to_json(indent=4)) 