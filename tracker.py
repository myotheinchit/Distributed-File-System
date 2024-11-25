import asyncio
import os
import random
import json

class Tracker:

    def __init__(self):
        self.connected_clients = {}

    # Reading chunkmap.json for various purposes
    #################
    async def read_chunk_map(self):
        try:
            with open('chunk_map.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading chunk_map.json: {e}")
            return {}

    # Returning file list to client
    #################
    async def list_files(self,reader,writer):
        chunk_map = await self.read_chunk_map()
        response_lines = [f"{entry['filename']}: {entry['total_chunk_num']}" for entry in chunk_map]
        response_message = "\n".join(response_lines)
        writer.write(response_message.encode())
        await writer.drain()
        print(f"Sent file list to client: {response_message}")
    
    async def tracker_files(self):
        chunk_map = await self.read_chunk_map()
        response_lines = [f"{entry['filename']}: {entry['total_chunk_num']}" for entry in chunk_map]
        response_message = "\n".join(response_lines)

        print(f"\nFiles currently published : {response_message}")
        return

    # Returning peer list to client
    #############
    async def list_peers(self,reader,writer):
        response_lines = [f"{ip}:{port}" for writer, (ip, port) in self.connected_clients.items()]
        response_message = "\n".join(response_lines)
        writer.write(response_message.encode())
        await writer.drain()
        print(f"Sent peer list to client: {response_message}")
    
    async def tracker_peers(self):
        response_lines = [f"{ip}:{port}" for writer, (ip, port) in self.connected_clients.items()]
        response_message = "\n".join(response_lines)

        print(self.connected_clients)
        print(f"\nCurrently connected peers:\n\n{response_message}")
        return
    
    # Returning chunkmap
    ###################
    async def send_chunk_map_for_file(self,filename,reader,writer):
        
        try:
            # Read the chunk map JSON file
            chunk_map = await self.read_chunk_map()

            # Iterate through all entries to find the chunk map for the specified filename
            file_chunk_map = None
            for entry in chunk_map:
                if entry.get("filename") == filename:
                    file_chunk_map = entry
                    break
            
            if not file_chunk_map:
                # If no chunk map is found for the filename, notify the client
                writer.write(b'ERROR: File chunk map not found\n')
                await writer.drain()
                return

            # Convert the chunk map to a JSON string
            file_chunk_map_json = json.dumps(file_chunk_map)

            # Send the JSON string to the client
            writer.write(file_chunk_map_json.encode())
            await writer.drain()

            print(f"Sent chunk map for file {filename} to client.")
        
        except Exception as e:
            print(f"Error sending chunk map for file {filename}: {e}")
            writer.write(b'ERROR: An error occurred while sending the chunk map\n')
            await writer.drain()


    # Processing requests
    ###############
    async def process_req(self,reader,writer):
        try:
            request = await reader.readline()
            if not request:
                return
            request = request.decode().strip()
            print(f"Received request: {request}")

            if request == "LIST_FILES":
                await self.list_files(reader,writer)
            
            elif request == "LIST_PEERS":
                await self.list_peers(reader,writer)
            
            elif request == "PLEASE_CHUNK":
                await self.create_chunk_map(reader,writer)
            
            elif request == "GET_CHUNK":
                #await reader.read()
                filename = (await reader.read(1024)).decode().strip()
                await self.send_chunk_map_for_file(filename,reader,writer)
            
            elif request == "EXIT":
                if writer in self.connected_clients:
                    print(f"\nClient {self.connected_clients[writer]} removed from dictionary.")
                    del self.connected_clients[writer]
                
                writer.close()
                await writer.wait_closed()
            
            else:
                response_message = "Unknown command"
                writer.write(response_message.encode())
                await writer.drain()
                print(f"Sent unknown command response to client: {response_message}")
        
        except (ConnectionResetError, asyncio.IncompleteReadError):
            print(f"\nClient disconnected abruptly.")
            if writer in self.connected_clients:
                del self.connected_clients[writer]
                print(f"\nClient removed from dictionary.")
            writer.close()
            #await writer.wait_closed()
            pass
        except Exception as e:
            print(f"Error processing request: {e}")
            pass

    # Starting the tracker server
    ###############
    async def tracker_start_serving(self):
        server = await asyncio.start_server(self.handle_client, host="0.0.0.0", port=5001)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f"\nServer listening on {addrs}......")

        async with server:
            await server.serve_forever()

    # Handling new client connection
    ###############
    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"\nClient connected: {addr}")

        data = await reader.read(100)
        serving_port = data.decode().strip()
        
        self.connected_clients[writer] = (addr[0], serving_port)
        #print(f"Current connected clients: {self.connected_clients}")

        try:
            while True:
                await self.process_req(reader,writer)
                await asyncio.sleep(1)
        
        except asyncio.CancelledError:
            pass
        except (ConnectionResetError, asyncio.IncompleteReadError):
            print(f"\nClient {addr} disconnected abruptly.")
            if writer in self.connected_clients:
                del self.connected_clients[writer]
                print(f"\nClient {addr} removed from dictionary.")
            writer.close()
            await writer.wait_closed()
        finally:
            if writer in self.connected_clients:
                del self.connected_clients[writer]
                print(f"\nClient {addr} removed from dictionary.")
            writer.close()
            await writer.wait_closed()
            print(f"\nCurrent connected clients: {self.connected_clients}")

#ping client for availability
##################

    async def ping_client(self,ip, port):
        """Pings the client to check if it's reachable."""
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            writer.close()
            await writer.wait_closed()
            return True
        except Exception as e:
            print(f"Failed to ping {ip}:{port}: {e}")
            return False

    # Creating chunk mapping and saving it in a JSON file
    #################
    async def create_chunk_map(self,reader,writer):
        CHUNK_SIZE = 1024 * 1024  # 1 MB in bytes
        try:
            # Read file name and size from client
            chunk_data = await reader.readuntil(b'\n')
            file_name = chunk_data.decode().strip()

            chunk_data = await reader.readuntil(b'\n')
            file_size = int(chunk_data.decode().strip())

            num_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE

            # List of client addresses in "ip:port" format
            client_addresses = [f"{ip}:{port}" for ip, port in self.connected_clients.values()]

            if not client_addresses:
                raise Exception("No clients connected to assign chunks.")
            print(client_addresses)
            # Check each client and remove unreachable ones
            reachable_clients = []
            for addr in client_addresses:
                ip, port = addr.split(":")
                print(ip,port)
                if await self.ping_client(ip, port):
                    reachable_clients.append(addr)
                else:
                    # Remove unreachable clients from connected_clients
                    client_tuple = (ip, port)
                    self.connected_clients = {k: v for k, v in self.connected_clients.items() if v != client_tuple}

            # If no reachable clients are left, raise an exception
            if not reachable_clients:
                raise Exception("No reachable clients to assign chunks.")

            # Assign chunks to reachable clients in a round-robin manner
            chunk_map = []
            for i in range(num_chunks):
                assigned_client = reachable_clients[i % len(reachable_clients)]
                chunk_map.append(assigned_client)

            # Create the chunk map entry
            new_chunk_data = {
                "filename": file_name,
                "chunkmap": chunk_map,
                "total_chunk_num": num_chunks
            }

            # Save the chunk map to a JSON file
            json_file_path = "chunk_map.json"
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as json_file:
                    existing_data = json.load(json_file)
            else:
                existing_data = []

            existing_data.append(new_chunk_data)

            with open(json_file_path, 'w') as json_file:
                json.dump(existing_data, json_file, indent=4)

            print(f"Chunk map data appended and saved to {json_file_path}")

            # Send the chunk map data to the client
            json_data = json.dumps(new_chunk_data)
            writer.write(json_data.encode())
            await writer.drain()

            print(f"Chunk data sent to client.")

        except Exception as e:
            print(f"Error creating or appending chunk map: {e}")