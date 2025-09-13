import socket

HOST = "0.0.0.0"  # Listen on all available network interfaces
PORT = 9000


def request(conn, addr):
    """Handles a single, long-lasting client connection."""
    print(f"[NEW CLIENT] Connected by {addr}")

    # Wrap the socket in file-like objects for easier, buffered I/O
    # 'rb' for reading binary, 'wb' for writing binary
    rfile = conn.makefile('rb')
    wfile = conn.makefile('wb')

    try:
        # Main loop to continuously request frames
        while True:
            print("\n-------------------------")
            # 1. Send the request for a frame
            print("Requesting a new frame from ESP32...")
            wfile.write(b'GET_FRAME\n')
            wfile.flush()  # Ensure the request is sent immediately

            # 2. Read the size header line from the client
            # The rfile.readline() correctly reads just one line
            size_line = rfile.readline()
            if not size_line:
                print("Client disconnected.")
                break

            size_line = size_line.strip().decode('utf-8')
            print(f"Received header: '{size_line}'")

            # 3. Parse the size from the header
            if size_line.startswith("SIZE"):
                try:
                    size = int(size_line.split()[1])
                    print(f"Expecting {size} bytes of image data...")
                except (ValueError, IndexError):
                    print(f"⚠️ Invalid size format: {size_line}")
                    continue
            else:
                print(f"⚠️ Invalid header received: {size_line}")
                continue

            # 4. Read exactly that many bytes for the image
            image_data = rfile.read(size)

            if len(image_data) < size:
                print("⚠️ Connection closed before full image was received.")
                break

            print(f"Successfully received {len(image_data)} bytes.")

            # 5. Save the image data to a file
            with open("received_frame.jpg", "wb") as f:
                f.write(image_data)
            print("✅ Frame saved successfully as received_frame.jpg")

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally:
        print(f"[CONNECTION CLOSED] {addr}")
        rfile.close()
        wfile.close()
        conn.close()


class ESP32Server:
    def __init__(self, host = "0.0.0.0", port = 9000):
        self.host = host
        self.port = port
        self.conn = None
        self.addr = None
        self.rfile = None
        self.wfile = None

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen()
            print(f"✅ [LISTENING] Server is listening on {HOST}:{PORT}")

            self.conn, self.addr = server.accept()
            print(f"[NEW CLIENT] Connected by {self.addr}")

            self.rfile = self.conn.makefile('rb')
            self.wfile = self.conn.makefile('wb')

    def request_frame(self):
        """Handles a single, long-lasting client connection."""
        # Wrap the socket in file-like objects for easier, buffered I/O
        # 'rb' for reading binary, 'wb' for writing binary

        try:
            # Main loop to continuously request frames
            print("\n-------------------------")
            # 1. Send the request for a frame
            print("Requesting a new frame from ESP32...")
            self.wfile.write(b'GET_FRAME\n')
            self.wfile.flush()  # Ensure the request is sent immediately

            # 2. Read the size header line from the client
            # The rfile.readline() correctly reads just one line
            size_line = self.rfile.readline()
            if not size_line:
                print("Client disconnected.")
                raise Exception("Client disconnected.")

            size_line = size_line.strip().decode('utf-8')
            print(f"Received header: '{size_line}'")

            # 3. Parse the size from the header
            if size_line.startswith("SIZE"):
                try:
                    size = int(size_line.split()[1])
                    print(f"Expecting {size} bytes of image data...")
                except (ValueError, IndexError):
                    raise Exception("Invalid size format")
            else:
                raise Exception("Invalid header received")

            # 4. Read exactly that many bytes for the image
            image_data = self.rfile.read(size)

            if len(image_data) < size:
                raise Exception("Connection closed before full image was received")

            print(f"Successfully received {len(image_data)} bytes.")

            # 5. Save the image data to a file
            with open("received_frame.jpg", "wb") as f:
                f.write(image_data)
            print("✅ Frame saved successfully as received_frame.jpg")

        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
        finally:
            print(f"[CONNECTION CLOSED] {self.addr}")
            self.close()

    def close(self):
        self.conn.close()
        self.rfile.close()
        self.wfile.close()


if __name__ == "__main__":
    s = ESP32Server()
    s.start()
    s.request_frame()
    s.close()