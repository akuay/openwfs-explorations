from pythonosc import udp_client
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
import csv

# listen for /error, append end of error message to string
"""
dispatcher = Dispatcher()
dispatcher.map("/error", filter_handler)

listening_port = 111

server = AsyncIOOSCUDPServer((local_ip, listening_port), dispatcher, asyncio.get_event_loop())
server.serve()

def filter_handler(address, *args):
    print(f"{address}: {args}")
"""

local_ip = "127.0.0.1"

# intializing viewer clients
upload_client = udp_client.SimpleUDPClient(local_ip, 1)
play_client = udp_client.SimpleUDPClient(local_ip, 2)
spatialize_client = udp_client.SimpleUDPClient(local_ip, 3)
gain_client = udp_client.SimpleUDPClient(local_ip, 4)

soundsource_paths = input("Upload the path to your sound sources: ")
# /Users/administrator/Documents/sum26_projs/max-explorations/max-scripts/file_list.txt

print("The max patch is now live.")
# should be able to type /gain blah or /source/x/xyz blah and get it routed without worrying about port? 

# need to be able to receive error messages for loading in sound
def parsed_osc(osc_message):
    list_osc = osc_message.split(" ")
    address, arguments = list_osc[0], list_osc[1:]
    for idx, arg in enumerate(arguments):
        arguments[idx] = int(arg)
    list_osc = [address, arguments]
    return list_osc

with open(soundsource_paths, newline = '') as file:
    soundsource_reader = csv.reader(file) # what else do i need here 
    for line in soundsource_reader:
        upload_client.send_message(line[0], line[1])
        print(f"Audio file {line[1]} loaded into {line[0]}")

while True:
    incoming_osc = input("Type an OSC message: ")
    if not incoming_osc or incoming_osc[0] != "/":
        print("Invalid OSC message! Must begin with a /")
        continue
    parse1 = parsed_osc(incoming_osc)
    parse2 = parse1[0].split("/")
    formatted_osc = (parse1[0], parse1[1])
    if parse2[1] == "gain":
        gain_client.send_message(*formatted_osc)
    elif parse2[1] == "source":
        spatialize_client.send_message(*formatted_osc)
    elif parse2[1] == "play":
        play_client.send_message(*formatted_osc)
    elif incoming_osc == "quit":
        break
    else:
        print("Invalid OSC message! Try again.")
        continue
    print(f"Sent {parse1[0], parse1[1]} to patch ")
