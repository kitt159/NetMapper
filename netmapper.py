import subprocess
import networkx as nx
import matplotlib.pyplot as plt
import re
import threading
from queue import Queue
import os
import socket

def get_result(address, results_queue):
    print(f"running thread for {address}")
    try:
        result = subprocess.run(["traceroute", address], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        results_queue.put(result)
        print(f"thread for {address} stops")
    except:
        print(f"cant run traceroute for {address}")
    

G = nx.Graph()
ipv4_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"

addresses = ["google.com"]
if os.path.exists("addresses.txt"):
    with open("addresses.txt", "r") as file:
        addresses = file.readlines()

results_queue = Queue()
threads = [threading.Thread(target=get_result, args=(address.strip(), results_queue)) for address in addresses]

for thread in threads:
      thread.start()

for thread in threads:
  thread.join()

while not results_queue.empty():
    result = results_queue.get()
    route = result.stdout.decode()
    hops = route.split('\n')
    while len(hops[-1]) < 12:
        hops.pop()
    last_id = "localhost"
    for hop in hops[1:]:
        match = re.search(ipv4_pattern, hop)
        if not match:
            id = "unknown " + str(abs(last_id.__hash__()) % 1000000)
        else:
            hop_ip = match.group()
            try:
                name = socket.gethostbyaddr(hop_ip)[0]
                id = name + '\n' + hop_ip
            except:
                id = hop_ip
        G.add_edge(last_id, id)
        last_id = id

color_map = ['red' if node == "localhost" else 'green' for node in G] 
nx.draw(G, nx.kamada_kawai_layout(G), with_labels=True, node_color=color_map)
plt.show()
