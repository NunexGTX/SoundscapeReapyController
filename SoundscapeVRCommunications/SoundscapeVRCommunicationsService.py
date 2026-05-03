import asyncio
import socket
import logging
from jsonUtils.SoundscapeReapyControllerConfig import SoundscapeReapyControllerConfig

logging.basicConfig(level=logging.INFO)

class SoundscapeVRCommunicationsService:
    def __init__(self, config: SoundscapeReapyControllerConfig):
        self.__communication_port = config.SoundscapeVRUnityCommunicationPort
        self.__host = '0.0.0.0' #Any client can connect
        self.__reapy_controller_ip = self.__get_this_server_addr()
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__buffer_size = 4096 #TODO: verificar buffer size ideal
        self.__server_socket: socket.socket | None = None
        self.__client_socket: socket.socket | None = None
        self.__is_connected = False

    async def start(self):
        """Entry point — binds the server and waits for the first client."""
        self.__bind_server()
        await self.__wait_for_connection()

    '''ReceiveRequest gets what unity is asking so we can do it on reaper'''
    async def receiveRequest(self) -> str:
        """
        Blocks until a full message arrives from the connected Unity client.
        Returns the decoded message string.
        Raises ConnectionResetError if the client disconnects mid-stream.
        """
        if not self.__is_connected or self.__client_socket is None:
            raise RuntimeError("No client is currently connected.")

        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                None,
                lambda: self.__client_socket.recv(self.__buffer_size)
            )
            if not data:
                raise ConnectionResetError("Client closed the connection.")

            message = data.decode('utf-8').strip()
            self.__logger.info(f"[RX] Received from Unity: {message}")
            return message

        except (ConnectionResetError, OSError) as e:
            self.__logger.warning(f"Connection lost while receiving: {e}")
            await self.__on_connection_lost()
            raise

    '''Function called to deliever the response that the action gave back to the server
    Some of them might need to be dealt with in unity's side'''
    async def sendResponse(self, response: str):
        """Sends a UTF-8 encoded response back to the Unity client."""
        if not self.__is_connected or self.__client_socket is None:
            raise RuntimeError("No client is currently connected.")

        loop = asyncio.get_event_loop()
        try:
            encoded = (response + '\n').encode('utf-8')
            await loop.run_in_executor(
                None,
                lambda: self.__client_socket.sendall(encoded)
            )
            self.__logger.info(f"[TX] Sent to Unity: {response}")

        except OSError as e:
            self.__logger.warning(f"Connection lost while sending: {e}")
            await self.__on_connection_lost()
            raise

    '''Disconnect closes the server correctly'''        
    def disconnect(self):
        """Gracefully closes both sockets and resets state."""
        self.__close_client()
        if self.__server_socket:
            try:
                self.__server_socket.close()
            except OSError:
                pass
            self.__server_socket = None
        self.__logger.info("Server shut down.")

    def __bind_server(self):
        """Creates and binds the TCP server socket (call once on startup)."""
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.__server_socket.setblocking(False) # non-blocking allows for async use and the rest of the code to run instead of being stuck waiting for new instructions
        self.__server_socket.bind((self.__host, self.__communication_port))
        self.__server_socket.listen(1) # only one Unity client at a time
        self.__logger.info(f"Server bound on {self.__host}:{self.__communication_port}, awaiting connection…")

    async def __wait_for_connection(self):
        """
        Non-blocking accept loop — yields control to the event loop until
        a Unity client connects, then marks the service as connected.
        """
        loop = asyncio.get_event_loop()
        self.__logger.info("Waiting for Unity client to connect…")
        self.__where_to_connect_message()

        client_socket, address = await loop.run_in_executor(
            None,
            self.__server_socket.accept          # blocks the thread-pool, not the event loop
        )
        self.__client_socket = client_socket
        self.__client_socket.setblocking(True)   # recv/send are wrapped in executor anyway
        self.__is_connected = True
        self.__logger.info(f"Unity client connected from {address}")

    def __where_to_connect_message(self):
        print()
        print(f"Connect to Sounscape Reapy Controller at: {self.__reapy_controller_ip}:{self.__communication_port}")
        print()

    def __get_this_server_addr(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            #By using a non existent ip, it fails to connect but we can still know the name of the interface
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
            self.__logger.warning("It was not possible to get this server's ip. Check the network interface or get the server's ip manually")
        finally:
            s.close()
        return ip

    async def __on_connection_lost(self):
        """
        Called whenever a send/receive detects a dropped connection.
        Cleans up the dead socket and re-enters the wait-for-connection loop
        so the service is ready for the next Unity session automatically.
        """
        self.__logger.info("Connection lost — resetting and waiting for a new client…")
        self.__close_client()
        await self.__wait_for_connection() # blocks until Unity reconnects

    def __close_client(self):
        """Shuts down and disposes the client socket, resets the connected flag."""
        if self.__client_socket:
            try:
                self.__client_socket.shutdown(socket.SHUT_RDWR)
                self.__client_socket.close()
            except OSError:
                pass
            self.__client_socket = None
        self.__is_connected = False