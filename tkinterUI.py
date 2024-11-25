import argparse
import asyncio
import sys
import os
from customtkinter import filedialog # type: ignore
import tkinter
import tkinter.messagebox
import customtkinter # type: ignore
import time
import threading
from client import Client,P2P
from tracker import Tracker


# Create an asyncio queue
queue = {}

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")



# Apply the font to all widgets


class Ui(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        default_font = customtkinter.CTkFont(family="Helvetica", size=15,weight="bold")
        # configure window
        self.title("Shal Thein Peer Terminal")
        self.geometry(f"{980}x{500}")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Shal Thein", font=customtkinter.CTkFont(size=23, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.list_file_btn = customtkinter.CTkButton(self.sidebar_frame, text="List Files", command=self.list_file_btn_event,state="disabled")
        self.list_file_btn.grid(row=1, column=0, padx=20, pady=10)
        
        self.upload_btn = customtkinter.CTkButton(self.sidebar_frame, text="Upload File",command=self.upload_btn_event,state="disabled")
        self.upload_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.download_btn = customtkinter.CTkButton(self.sidebar_frame, text="Download File",command=self.download_btn_event,state="disabled")
        self.download_btn.grid(row=3, column=0, padx=20, pady=10)
        
        self.host = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Host")
        self.host.grid(row=5, column=0, padx=(20), pady=(10), sticky="nsew")

        self.port = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="port")
        self.port.grid(row=6, column=0, padx=(20), pady=(10), sticky="nsew")

        self.connect_btn = customtkinter.CTkButton(self.sidebar_frame, text="connect",command=self.connect_btn_event)
        self.connect_btn.grid(row=7, column=0, padx=20, pady=10)

        # create textbox
        self.listFiles = customtkinter.CTkTextbox(self, width=250,font = default_font)
        self.listFiles.grid(row=0, column=1, padx=(20), pady=(20), sticky="nsew")
        
        self.infoTab = customtkinter.CTkTextbox(self, width=250,font = default_font)
        self.infoTab.grid(row=1, column=1, padx=(20), pady=(10), sticky="nsew")
        self.infoTab.insert(1.0,f"Please connect to a network first by entering a tracker's host and port")

    def list_file_btn_event(self):
            print("List File Btn : from GUI")
            queue["request"]="LIST_FILE"

            time.sleep(3)
            self.listFiles.delete("1.0", "end")
            if "reply" in queue:
                reply = queue.pop('reply')
                if reply.startswith("OK"):
                    # Sample input
                    print(f"Reply after removing 'OK': {reply[3:].strip()}")
                    data = reply[3:].strip()

                    def format_data(data):
                        if not data.strip():
                            return "No files available currently on the network."

                        # Split the input into lines and process each line
                        lines = data.strip().split('\n')
                        #print(lines)
                        # Parse the lines into tuples of (filename, chunks)
                        entries = []
                        for line in lines:
                            if ':' in line:
                                filename, chunks = line.split(':', 1)  # Limit split to 1 to handle filenames with ':'
                                filename = filename.strip()
                                chunks = chunks.strip()
                                entries.append((filename, chunks))
                            #print(entries)

                        if not entries:
                            return "No files avaiable on the network."

                        # Determine the maximum width for the file names column
                        max_filename_length = max(len(filename) for filename, _ in entries)
                        max_filename_length = max(max_filename_length, len('file name'))  # Ensure it fits the header

                        # Generate the table header
                        output = f"{'file name':<{max_filename_length}} {'chunks':>7}\n"

                        # Add each entry to the output
                        for filename, chunks in entries:
                            output += f"{filename:<{max_filename_length}} {chunks:>7}\n"

                        return output.strip()

                    # Call the function and print the result
                    formatted_output = format_data(data)
                    self.listFiles.insert(1.0,formatted_output)

                
                elif reply == "FAIL":
                    self.listFiles.insert(1.0, f"Cant retrieve files.")
            else:
                self.listFiles.insert(1.0, f"Cant retrieve files.")



    def download_btn_event(self):
            print("Download Btn : from GUI")
            filename=self.filename.get()
            queue["request"]=f"DOWNLOAD {filename}"

            self.infoTab.delete("1.0", "end")
            self.infoTab.insert(1.0,f"Trying to download {filename} on the network........") 

            time.sleep(3)
            self.infoTab.delete("1.0", "end")
            if "reply" in queue:
                reply = queue.pop('reply')
                if reply.startswith("OK"):
                    self.infoTab.insert(1.0,f"File downloaded successfully to device.")
                    return
                elif reply.startswith("FAIL"):
                    self.infoTab.insert(1.0,f"An Error occured in downloading file.")
                    return
            elif not "reply" in queue:
                time.sleep(3)
            if "reply" in queue:
                reply = queue.pop('reply')
                if reply.startswith("OK"):
                    self.infoTab.insert(1.0,f"File downloaded successfully to device.")
                    return
                elif reply.startswith("FAIL"):
                    self.infoTab.insert(1.0,f"An Error occured in downloading file.")
                    return
            elif not "reply" in queue:
                self.infoTab.insert(1.0,f"An Error occured in downloading file.")


    def upload_btn_event(self):
        # Open a file dialog and get the selected file path
        file_path = filedialog.askopenfilename(
            title="Select a file to upload",
            filetypes=[("All files", "*.*")],
            initialdir="/" 
        )
        
        # Check if a file was selected
        if file_path:
            # Construct the command with the file path
            command = f"UPLOAD {file_path}"
            print(f"Command: {command}")
            # Assuming `queue` is an instance variable (you should adapt it to your actual use case)
            queue["request"] = command
            self.infoTab.delete("1.0", "end")
            self.infoTab.insert(1.0,f"Trying to upload file {file_path} on the network.")            
            
            time.sleep(3)
            
            self.infoTab.delete("1.0", "end")
            if "reply" in queue:
                reply = queue.pop('reply')
                if reply.startswith("OK"):
                    self.infoTab.insert(1.0,f"File uploaded successfully on network.")
                    return
                elif reply.startswith("FAIL"):
                    self.infoTab.insert(1.0,f"An error occured in uploading file.")
                    return
            elif not "reply" in queue:
                time.sleep(3)
            if "reply" in queue:
                reply = queue.pop('reply')
                if reply.startswith("OK"):
                    self.infoTab.insert(1.0,f"File uploaded successfully on network.")
                    return
                elif reply.startswith("FAIL"):
                    self.infoTab.insert(1.0,f"An error occured in uploading file.")
                    return
            elif not "reply" in queue:
                self.infoTab.insert(1.0,f"An error occured in uploading file.")
            

    def connect_btn_event(self):
            print("Connect Btn : from GUI")
            
            host=self.host.get()
            port=self.port.get()
            queue["request"]=f"CONNECT {host} {port}"
            
            time.sleep(4)

            self.infoTab.delete("1.0", "end")

            if "reply" in queue:
                reply = queue.pop('reply')
                if reply.startswith("OK"):
                    self.infoTab.insert(1.0,f"Connected successfully to tracker at {host}:{port} \n\n You can on the network now.")
                    self.download_btn.configure(state="normal")
                    self.upload_btn.configure(state="normal")
                    self.list_file_btn.configure(state="normal")
                    self.host.configure(placeholder_text=host)
                    self.port.configure(placeholder_text=port)
                    self.filename = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Enter File name from available files to download")
                    self.filename.grid(row=4, column=0, padx=(20), pady=(10), sticky="nsew")
                    self.list_file_btn_event()
                
                elif reply == "FAIL":
                    self.infoTab.insert(1.0, f"Cant connect to host {host} at port {port} \n\n There is no tracker started with {host}:{port}")
            else:
                self.infoTab.insert(1.0, f"Cant connect to host {host} at port {port} \n\n The host takes too long to respond.")



async def get_terminal_input(prompt):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)


async def listen_for_gui_requests(p2p,client):
    print("GUI Listener started")

    while True:
        if 'request' in queue:
            request = queue.pop('request')
            print(f"Request received: {request}")  # Print request received
            if request.startswith("LIST_FILE"):
                try:
                    result = await client.ask_list_files()
                    #print(f"b4 qing{result}")
                    queue["reply"]=f"OK {result}"
                except Exception as e:
                     print(f"Error occured retrieving files : {e}")
                     queue["reply"]="FAIL"
            
            elif request.startswith("DOWNLOAD"):
                try:
                    _,filename = request.split(maxsplit=1)
                    total_chunk=await p2p.fetch_chunks(await client.ask_chunk_info(filename))
                    await p2p.combine_chunks(filename,total_chunk)
                    queue["reply"]="OK"
                except Exception as e:
                    print(f"Error downloading file : {e}")
                    queue["reply"]="FAIL"
            
            elif request.startswith("UPLOAD"):
                _,file_path = request.split(maxsplit=1)
                try:
                    await p2p.send_file_chunks(file_path,await client.please_chunk(file_path))
                    queue["reply"]="OK"
                except Exception as e:
                    print(f"Error in sending file on network : {e}")
            
            elif request.startswith("CONNECT"):
                _, host, port = request.split()
                try:
                    await client.connect_tracker(host, port)
                    queue["reply"]="OK"
                except Exception as e:
                     print(f"Error connecting to tracker :{e}")
                     queue["reply"]="FAIL"
                
            else:
                 queue["reply"]="UNKNOWN"

def run_async(func,p2p,client):
    """Helper function to run an async function in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func(p2p,client))

def run_async_serve(func):
    """Helper function to run an async function in a new event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func())

def run_ui():
        app = Ui()
        app.mainloop()

async def main(role):
    if role == 'client':
        # Start the tae_test function in a separate thread
        p2p=P2P()
        client=Client()
        
        listenerthread = threading.Thread(target=run_async, args=(listen_for_gui_requests,p2p,client), daemon=True)
        listenerthread.start()
        
        peerthread = threading.Thread(target=run_async_serve, args=(p2p.peer_start_serving,), daemon=True)
        peerthread.start()
        # Run the tkinter UI in the main thread
        run_ui()
    
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
  
    else :
        print("Unknown role. Please specify 'client' or 'tracker'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the application as a client or tracker.')
    parser.add_argument('role', choices=['client', 'tracker'], help="Specify whether to run as 'client' or 'tracker'")
    args = parser.parse_args()
    asyncio.run(main(args.role))