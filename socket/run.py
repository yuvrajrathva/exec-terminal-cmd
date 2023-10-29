# Unix sockets are used to communicate between processes on the same machine.
import sys # which provides access to some variables used or maintained by the Python interpreter and to functions that interact strongly with the interpreter, including the command-line arguments.

def main(argv):
    from transport.unixsocket import UNIXSocketTransport

    transport = UNIXSocketTransport()


    if len(argv) == 1: # sys.argv is a list in Python, which contains the command-line arguments passed to the script.
        transport.run_server() #start a Unix socket server
    else:
        process, stdout, stderr = transport.run_cmd(' '.join(argv[1:]))

        sys.stdout.write(stdout)
        sys.stderr.write(stderr)

        sys.exit(process.returncode)

if __name__ == '__main__':
    main(sys.argv)
