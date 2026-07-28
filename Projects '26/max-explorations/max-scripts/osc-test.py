import math
import time
from pythonosc import udp_client
ip = "127.0.0.1"
# port = 7400 not sure what is the right port
port = 2
client = udp_client.SimpleUDPClient(ip, port)

client.send_message("/source/1/xyz", [1, 1, 1])

"""
out = 0
for i in range(0, 360):
    x, y = math.sin(i), math.cos(i)
    client.send_message("/source/1/xyz", [x+out, y, out])
    out += 0.01
    time.sleep(1)
"""


# each osc command feeds into either spat5.oper or spat5.viewer
# use udpreceive 7400 to communicate with max, then connect it to place you want message to be sent
# curious about other port

viewer_client, wfs_client, buffer_client = udp_client.SimpleUDPClient(ip, 100), udp_client.SimpleUDPClient(ip, 200), udp_client.SimpleUDPClient(ip, 300)
viewer_client.send_message("/source/number", 6)
wfs_client.send_message("/source/number", 3)
# wfs client can't take, so need to run v8 patcher to remake spat5.wfs object and connect
# to correct spots
filepath = "/Users/bu26229/Downloads/dragon-studio-free-dog-bark-419014.wav"
buffer_client.send_message("/buffer", filepath)


