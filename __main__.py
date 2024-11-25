import argparse
import asyncio
import sys
import os
from client import Client,P2P
from tracker import Tracker

async def get_terminal_input(prompt):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)

async def main(role):

    if role == 'client':
        p2p = P2P()
        client = Client()
        print("Welcome to peer terminal ....")
        client_task = asyncio.create_task(p2p.peer_start_serving())
        
        while True:
            sys.stdout.flush()
            user_input = await get_terminal_input("\nCommand : ")
            
            if user_input == 'connect':
                host = await get_terminal_input("\nEnter tracker host: ")
                port = int(await get_terminal_input("Enter tracker port: "))
                await client.connect_tracker(host, port)
            
            elif user_input == 'upload':
                file_path = await get_terminal_input("\nEnter file path: ")
                await p2p.send_file_chunks(file_path,await client.please_chunk(file_path))
            
            elif user_input == 'files':
                await client.ask_list_files()
            
            elif user_input == 'peers':
                await client.ask_list_peers()
            
            elif user_input == 'download':
                file_name = await get_terminal_input("\nEnter file name you want to download: ")
                total_chunk=await p2p.fetch_chunks(await client.ask_chunk_info(file_name))
                await p2p.combine_chunks(file_name,total_chunk)
            
            elif user_input == 'exit':
                await client.close_connection()
                break
            else:
                print("Unknown command. Please try again.")
    
    elif role == 'tracker':
        print("Welcome to Tracker Terminal :")
        tracker = Tracker()
        while True:
            sys.stdout.flush()
            user_input = await get_terminal_input("\nCommand : ")
            
            # Implement tracker-specific commands here
            if user_input == 'start':
                tracker_task = asyncio.create_task(tracker.tracker_start_serving())
            elif user_input == 'files':
                await tracker.tracker_files()
            elif user_input == 'peers':
                await tracker.tracker_peers()

            elif user_input == 'exit':
                break
            
            else:
                print("Unknown command. Please try again.")
    
    else:
        print("Unknown role. Please specify 'client' or 'tracker'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the application as a client or tracker.')
    parser.add_argument('role', choices=['client', 'tracker'], help="Specify whether to run as 'client' or 'tracker'")
    args = parser.parse_args()
    asyncio.run(main(args.role))
