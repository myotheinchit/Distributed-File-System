import random
import json
import asyncio
import os

async def create_chunk_map(reader, writer, clients):
    # Constants
    CHUNK_SIZE = 1024 * 1024  # 1 MB in bytes
    
    try:
        # Read file name and size from the reader
        chunk_data = await reader.readuntil(b'\n')  # Read until newline
        file_name = chunk_data.decode().strip()

        chunk_data = await reader.readuntil(b'\n')  # Read next line for file size
        file_size = int(chunk_data.decode().strip())
        
        # Calculate number of chunks
        num_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE  # Ceiling division

        # Randomly select up to num_chunks addresses from the clients list
        client_addresses = list(clients.values())  # Extract just the addresses
        random.shuffle(client_addresses)
        selected_clients = client_addresses[:num_chunks]

        # Create a mapping of addresses to chunk numbers
        chunk_map = {addr: str(i + 1) for i, addr in enumerate(selected_clients)}

        # Prepare the data to be stored in JSON
        new_chunk_data = {
            "filename": file_name,
            "chunkmap": chunk_map,
            "total_chunk_num": num_chunks
        }

        # File path
        json_file_path = "chunk_map.json"

        # Read existing data from JSON file
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                existing_data = json.load(json_file)
        else:
            existing_data = []

        # Append new data
        existing_data.append(new_chunk_data)

        # Write updated data back to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

        print(f"Chunk map data appended and saved to {json_file_path}")

        # Serialize the data to JSON and send it to the writer
        json_data = json.dumps(new_chunk_data)
        writer.write(json_data.encode())
        await writer.drain()  # Ensure data is sent

        print(f"Chunk data sent to client.")

    except Exception as e:
        print(f"Error creating or appending chunk map: {e}")

    finally:
        # Close the writer only if you want to end the connection
        writer.close()
        # await writer.wait_closed()  # Remove this line if connection should remain open
        pass

    # Write the data to a JSON file


# Example usage
async def main():
    clients = {
        "<StreamWriter ...>": "192.168.1.4",
        "<StreamWriter ...>": "192.168.1.5",
        "<StreamWriter ...>": "192.168.1.3"
    }
    await create_chunk_map(clients)

if __name__ == "__main__":
    asyncio.run(main())
