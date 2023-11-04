# Unix sockets are used to communicate between processes on the same machine.
import sys # which provides access to some variables used or maintained by the Python interpreter and to functions that interact strongly with the interpreter, including the command-line arguments.
import argparse
import importlib

parser = argparse.ArgumentParser(description='Start main.')
parser.add_argument('-t', '--transport', dest='transport', nargs='?',
           default='main.transports.unixsocket.UNIXSocketTransport',
           help='Python path to the transport to use.')
parser.add_argument('--pool-size', dest='pool_size', nargs='?', type=int,
           default=10,
           help='Number of worker processes to use.')
parser.add_argument('--max-accepts', dest='max_accepts', nargs='?', type=int,
           default=5000,
           help='Max number of connections the server will accept.')
parser.add_argument('--max-child-tasks', dest='max_child_tasks', nargs='?', type=int,
           default=100,
           help='Max number of tasks each child process will handle before being replaced.')
parser.add_argument('command', nargs=argparse.REMAINDER) # positional argument that accepts any remaining command line arguments as a list 

def main(argv):
    parsed_args = parser.parse_args(argv[1:])

    mod, klass = parsed_args.transport.rsplit('.', 1)

    transport = getattr(importlib.import_module(mod), klass)()

    command = parsed_args.command

    if not command:
        transport.run_server( pool_size=parsed_args.pool_size,
            max_accepts=parsed_args.max_accepts,
            max_child_tasks=parsed_args.max_child_tasks)
    else:
        stdout, stderr, returncode = transport.run_cmd(' '.join(command))

        sys.stdout.write(stdout)
        sys.stderr.write(stderr)

        sys.exit(returncode)

if __name__ == '__main__':
    main(sys.argv)
