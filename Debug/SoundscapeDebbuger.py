import socket
import json
import uuid
import time

class SoundscapeDebugger:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Establishes connection to the SoundscapeVRCommunicationsService."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"Successfully connected to {self.host}:{self.port}")
        except Exception as e:
            print(f"Connection failed: {e}")

    def disconnect(self):
        if self.sock:
            self.sock.close()
            print("Disconnected.")

    def _send_and_receive(self, payload: dict):
        """Helper to send JSON and wait for the response."""
        if not self.sock:
            print("Error: Not connected.")
            return

        try:
            # Convert dict to JSON string and encode
            message = json.dumps(payload)
            self.sock.sendall(message.encode('utf-8'))
            print(f"\n[TX] Sent: {message}")

            # Wait for response
            data = self.sock.recv(4096)
            if data:
                print(f"[RX] Received: {data.decode('utf-8').strip()}")
            else:
                print("[RX] No data received (Connection closed by server).")
        except Exception as e:
            print(f"Communication error: {e}")

    # --- Test Cases ---

    def test_new_track(self, audio_id="drums_01", track_uuid=None, loop=True):
        """Tests the 'new_track' command."""
        track_uuid = track_uuid or str(uuid.uuid4())
        payload = {
            "command": "new_track",
            "AudioID": audio_id,
            "SoundUUID": track_uuid,
            "Loop": loop
        }
        self._send_and_receive(payload)
        return track_uuid

    def test_source_position(self, track_uuid, azim, elev, distance):
        """Tests the 'source_position' command."""
        payload = {
            "command": "source_position",
            "SoundUUID": track_uuid,
            "position": (azim, elev),
            "distance": distance
        }
        self._send_and_receive(payload)

    def test_delete_track(self, track_uuid):
        """Tests the 'delete_track' command."""
        payload = {
            "command": "delete_track",
            "SoundUUID": track_uuid
        }
        self._send_and_receive(payload)

    def test_invalid_command(self):
        """Tests error handling for unknown commands."""
        payload = {"command": "buhahahah", "data": "unknown"}
        self._send_and_receive(payload)

# --- Execution Script ---
if __name__ == "__main__":
    # 1. Initialize the debugger (adjust IP/Port if needed)
    debugger = SoundscapeDebugger(host='127.0.0.1', port=5000)
    
    debugger.connect()

    # 2. Run a sequence of tests
    # First, create a track and capture the UUID
    my_uuid = debugger.test_new_track(audio_id="ambient_wind", loop=False)
    
    # Wait a moment to simulate real-time interaction
    time.sleep(1)

    # Move that track in 3D space
    debugger.test_source_position(my_uuid, azim=180.0, elev=15.0, distance=10.5)

    time.sleep(1)

    # Delete the track
    debugger.test_delete_track(my_uuid)

    # Test an error case
    debugger.test_invalid_command()

    debugger.disconnect()