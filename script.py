from prometheus_client import start_http_server, Gauge, Info
import requests
import json
import time
from collections import defaultdict
import os

# Get port from environment variable or use default value 9584
PORT = int(os.getenv('PORT', '9584'))

def fetch_server_data():
    url = "https://backend.beammp.com/servers"
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return []

def update_metrics():
    server_data = fetch_server_data()
    total_players = 0  # Initialize total players counter
    total_max_players = 0  # Initialize total max players counter
    server_map_players = defaultdict(int)  # Initialize dictionary to track players per server map
    for server in server_data:
        sname = server.get('sname')
        if "[^b🐟 CaRP^r Test Server]" not in sname:
            continue
        
        players = int(server.get('players', 0))  # Set players to 0 if not present
        total_players += players  # Add players to total players counter
        
        max_players = int(server.get('maxplayers', 0))  # Set max players to 0 if not present
        total_max_players += max_players  # Add max players to total max players counter
        
        players_list = server.get('playerslist', "").split(',')
        ip = server.get('ip')
        port = server.get('port')
        version = server.get('version')
        cversion = server.get('cversion')
        
        map_name = server.get('map')
        server_map_players[map_name] += players
        
        if sname:
            server_name_metric.labels(sname)
            server_players_metric.labels(sname).set(players)  # Track number of players connected
            server_max_players_metric.labels(sname).set(max_players)  # Track max players
            server_ip_metric.labels(sname).info({"ip": ip})  # Update as Info metric
            server_port_metric.labels(sname).set(port)  # Set port directly
            server_version_metric.labels(sname).info({"version": version})  # Update as Info metric
            server_cversion_metric.labels(sname).set(cversion)  # Set cversion directly
            
            # Track individual players
            for player in players_list:
                player_metric.labels(sname, player).set(1)
    
    # Set the total players metric
    total_players_metric.set(total_players)
    
    # Set the total max players metric
    total_max_players_metric.set(total_max_players)
    
    # Set the server map players metric
    for map_name, map_players in server_map_players.items():
        server_map_players_metric.labels(map_name).set(map_players)

if __name__ == '__main__':
    # Define Prometheus metrics
    server_name_metric = Info('beammp_server_name', 'Name of BeamMP servers', ['sname'])
    server_players_metric = Gauge('beammp_server_players', 'Number of players on BeamMP servers', ['sname'])
    server_max_players_metric = Gauge('beammp_server_max_players', 'Max players on BeamMP servers', ['sname'])
    server_ip_metric = Info('beammp_server_ip', 'IP address of BeamMP servers', ['sname'])
    server_port_metric = Gauge('beammp_server_port', 'Port of BeamMP servers', ['sname'])
    server_version_metric = Info('beammp_server_version', 'Version of BeamMP servers', ['sname'])
    server_cversion_metric = Gauge('beammp_server_cversion', 'Cversion of BeamMP servers', ['sname'])
    
    # Player metric to track individual players
    player_metric = Gauge('beammp_player_list', 'Player List in Each Server', ['sname', 'player'])
    
    # Total players metric
    total_players_metric = Gauge('beammp_total_players', 'Total number of players across all servers')
    
    # Total max players metric
    total_max_players_metric = Gauge('beammp_total_max_players', 'Total max number of players across all servers')
    
    # Server map players metric
    server_map_players_metric = Gauge('beammp_server_map_players', 'Total number of players per server map', ['map'])
    
    # Start HTTP server to expose Prometheus metrics
    start_http_server(PORT)  # Use the port defined in the environment variable or default to 9584
    
    # Update metrics every 60 seconds
    while True:
        update_metrics()
        time.sleep(60)  # Updated interval to 60 seconds
