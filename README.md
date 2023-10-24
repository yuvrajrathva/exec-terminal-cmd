# exec-terminal-cmd

Uses Python multiprocessing to maintain a pool of worker processes used to execute arbitrary terminal commands.

What we want to do:
1. Establish a connection to the server's socket.
2. Send the command you wish to execute as a string followed by ``\r\n\r\n`` (CRLFCRLF).
3. Receive data back from the connection until the server stops sending back data. The server will close the connection when it's done.
4. JSON decode the data, which contains stdout, stderr, and the return code.
