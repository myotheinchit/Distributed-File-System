import asyncio
import os
import random
import json

serving_port=0

class Client:
    def __init__(self):
        #self.chunkmap={}
        #self.chunkmap_to_download={}
        global serving_port
        self.serving_port= serving_port
        pass

    async def connect_tracker(self,host,port):
        self.reader, self.writer = await asyncio.open_connection(host, port)
        print(f"Connected to server at {host}:{port}")

        message = f"{self.serving_port}\n"  # Add newline for easier parsing on the server side
        self.writer.write(message.encode())  # Send the random port
        await self.writer.drain()

#sending file info to server for chunking purpose
########################
    async def please_chunk(self, file_path):
        try:    
            filename = os.path.basename(file_path)  # Get the filename from the path
            filesize = os.path.getsize(file_path)
        except Exception as e:
            print(f'Error in finding file : doesnt exist :{e}')

        self.writer.write(b'PLEASE_CHUNK\n')
        await self.writer.drain()
        
        info_message = f"{filename}\n{filesize}\n"
        self.writer.write(info_message.encode())
        await self.writer.drain()
        print(f"Sending file info to server to get chunked : {info_message}")

        # Expecting JSON chunk map reply from tracker
        data = await self.reader.read(4096)  # Adjust buffer size as needed
        chunk_map_str = data.decode()
        print(f"chunk_map_str : {chunk_map_str}")
        return json.loads(chunk_map_str)  # Convert JSON string to Python dictionary

        #print(f"Received chunk map: {self.chunkmap}")

#requesting file_list
#############
    async def ask_list_files(self):
        self.writer.write(b'LIST_FILES\n')
        await self.writer.drain()

        # Receive and print file list
        data = await self.reader.read(1000)  # Adjust buffer size as needed
        print("File List:")
        return data.decode()

#requesting peer_list
###############
    async def ask_list_peers(self):
        self.writer.write(b'LIST_PEERS\n')
        await self.writer.drain()

        # Receive and print peer list
        data = await self.reader.read(1000)  # Adjust buffer size as needed
        print("Peer List:")
        print(data.decode())

#requesting chunk_info
#############
    async def ask_chunk_info(self, filename):
        # Send GET_CHUNK request
        self.writer.write(b'GET_CHUNK\n')
        await self.writer.drain()

        # Send the filename
        self.writer.write(filename.encode() + b'\n')
        await self.writer.drain()
        
        # Receive chunk map response
        chunk_map_data = await self.reader.read(4096) # Adjust the buffer size as needed
        return json.loads(chunk_map_data.decode())

#closing connection with tracker
#########################
    async def close_connection(self):
        if self.writer:
            self.writer.write(b'EXIT\n')
            await self.writer.drain()
            self.writer.close()
            await self.writer.wait_closed()


######p2p section#########
#connection open to each client
##############
class P2P: 
    def __init__(self) -> None:
        self.serving_port=random.randint(1024,65535)
        global serving_port
        serving_port = self.serving_port
        pass

    async def peer_start_serving(self):
        server = await asyncio.start_server(self.handle_file_request, host="0.0.0.0", port=self.serving_port)
        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f"listening on {addrs} for p2p file requests.....")

        async with server:
            await server.serve_forever()

#handling all p2p request
################
    async def handle_file_request(self,reader,writer):
        try:
            # Read the request from the peer
            request = await reader.readuntil(b'\n')  # Adjust buffer size as needed
            request = request.decode().strip()
            print(f"Received request: {request}")
            #self.reader=reader
            #self.writer=writer

            if request.startswith("REQUEST_CHUNK"):
                # Extract the filename from the request
                _, filename = request.split(maxsplit=1)
                print(f"Requested file chunk: {filename}")

                # Check if the file exists
                if not os.path.exists(filename):
                    print(f"File {filename} does not exist.")
                    writer.write(b"ERROR: File does not exist")  # Inform peer of error
                    await writer.drain()
                    return

                # Send the file chunk
                with open(filename, 'rb') as f:
                    while chunk := f.read(1024):
                        writer.write(chunk)
                        await writer.drain()
                print(f"File chunk {filename} sent successfully.")
            
                        # Extract the filename from the request
            elif request.startswith("UPLOAD_FILE"):
                _, filename = request.split(maxsplit=1)

                directory = "chunk_storage"
                os.makedirs(directory, exist_ok=True)
                print(f"Receiving file: {filename} into the folder {directory}")
                
                await self.receive_file_chunk(f"{directory}/{filename}",reader,writer)

            else:
                print(f"Unknown request type: {request}")
                writer.write(b"ERROR: Unknown request type")  # Inform peer of unknown request
                await writer.drain()

        except Exception as e:
            print(f"Error handling file request: {e}")
            writer.write(b"ERROR: An error occurred while handling the request")  # Inform peer of error
            await writer.drain()

        finally:
            writer.close()
            await writer.wait_closed()

#connecting peer to peer
########################
    async def bridge_peer(self, host, port):
        try:
            # Establish a connection to the specified peer
            reader,writer = await asyncio.open_connection(host, port)
            print(f"Connected to peer at {host}:{port}")
            return reader,writer
        
        except Exception as e:
            print(f"Failed to connect to peer at {host}:{port}. Error: {e}")
            return None

#####requesting chunk from folder chunk_storage
#################
    async def request_file_chunk(self,filename,reader,writer):
        try:
            # Request the specific chunk of the file
            request_message = f"REQUEST_CHUNK chunk_storage/{filename}\n"
            writer.write(request_message.encode())
            await writer.drain()
            
            directory = "temp"
            os.makedirs(directory, exist_ok=True)

            # Add the 'temp' folder before the filename
            chunk_filename = f"{directory}/{filename}"
            await self.receive_file_chunk(chunk_filename,reader,writer)

        except Exception as e:
            print(f"Error requesting file chunk {filename}: {e}")

#receiving single file chunk for various purpose
################
    async def receive_file_chunk(self, filename, reader, writer):
        try:
            print(f"Receiving file chunk for: {filename}")

            # Open the file in binary write mode
            with open(filename, 'wb') as f:
                while True:
                    # Read incoming data in chunks (1024 bytes at a time)
                    chunk = await reader.read(1024)

                    # If no more data is coming in, break the loop
                    if not chunk:
                        break

                    # Write the chunk to the file
                    f.write(chunk)

            print(f"File chunk {filename} received successfully.")
            
        except Exception as e:
            print(f"Error receiving file chunk: {e}")
        
        finally:
            writer.close()
            await writer.wait_closed()  # Ensure the writer closes properly

#combine chunks
####################
    async def combine_chunks(self, filename, total_chunks):
        try:
            # Ensure the 'temp' directory exists (if you are also writing the combined file there)
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)

            save_dir = "files"
            os.makedirs(save_dir, exist_ok=True)
            
            # Open the output file 
            with open(f"{save_dir}/{filename}", 'wb') as output_file:
                for i in range(1, total_chunks + 1):  # Use total_chunks + 1 to include the last chunk
                    # Prepend 'temp/' to the chunk filename
                    chunk_filename = f"{temp_dir}/{filename}.{i}"
                    
                    # Check if the chunk file exists
                    if os.path.exists(chunk_filename):
                        # Open the chunk file and write its content to the combined file
                        with open(chunk_filename, 'rb') as chunk_file:
                            output_file.write(chunk_file.read())
                        
                        # Optionally remove the chunk file after combining
                        os.remove(chunk_filename)
                    else:
                        print(f"Chunk file {chunk_filename} not found.")
                        
            print(f"File {filename} combined successfully.")
            
        except Exception as e:
            print(f"Error combining file chunks: {e}")


######################
    async def fetch_chunks(self, chunkmap):
        tasks = []
        filename = chunkmap.get("filename")
        
        # Iterate over peers in the chunkmap (it's a list, not a dictionary)
        for i, peer in enumerate(chunkmap.get("chunkmap", [])):
            host, port = peer.split(':')
            port = int(port)
            chunk_filename = f"{filename}.{i+1}"
            
            # Append the task for fetching and saving the chunk
            tasks.append(self.fetch_and_save_chunk(host, port, chunk_filename))
        
        # Wait for all fetch tasks to complete
        await asyncio.gather(*tasks)
        
        # Return the total number of chunks
        return len(chunkmap.get("chunkmap", []))


###############################
    async def fetch_and_save_chunk(self, host, port, filename):
        reader,writer=await self.bridge_peer(host, port)
        if writer:
            await self.request_file_chunk(filename,reader,writer)

#distributing file chunks according to chunk map
###################
    async def send_file_chunks(self, filename, chunkmap):
        # Constants
        CHUNK_SIZE = 1024 * 1024  # 1 MB in bytes

        async def send_chunk(i, chunk_data, host, port, chunk_name):
            """Helper function to send a single chunk to a peer."""
            try:
                reader, writer = await self.bridge_peer(host, port)

                upload_request = f"UPLOAD_FILE {chunk_name}\n"
                writer.write(upload_request.encode())
                await writer.drain()

                # Send the chunk data
                writer.write(chunk_data)
                await writer.drain()

                print(f"Sent chunk {i+1} to peer at {host}:{port}")

                writer.close()
                await writer.wait_closed()

            except Exception as e:
                print(f"Failed to send chunk {i+1} to peer at {host}:{port}: {e}")

        try:
            tasks = []  # List to store tasks for asyncio.gather

            # Open the file to be split
            with open(filename, 'rb') as f:
                # Use the length of the chunkmap to determine the number of chunks
                num_chunks = len(chunkmap['chunkmap'])

                # Iterate through the chunks
                for i in range(num_chunks):
                    # Read a chunk of data from the file
                    chunk_data = f.read(CHUNK_SIZE)

                    # Get the peer address from the chunk map
                    assigned_peer = chunkmap['chunkmap'][i]
                    host, port = assigned_peer.split(':')
                    port = int(port)

                    # Construct the chunk name by appending the chunk number
                    chunk_name = f"{os.path.basename(filename)}.{i+1}"

                    # Create a task to send each chunk
                    task = send_chunk(i, chunk_data, host, port, chunk_name)
                    tasks.append(task)

            # Run all chunk-sending tasks in parallel
            await asyncio.gather(*tasks)

        except Exception as e:
            print(f"\nError sending file chunks: {e}")
        finally:
            print(f"\nAll chunks sent successfully, file is registered on network.")