import logging
import os
import time
from collections import defaultdict
from prometheus_client import start_http_server, Gauge, Info
import requests
import json

# Configuration variables
LOGGING = os.getenv('LOGGING', 'true').lower() == 'true'

# Configure logging if enabled
if LOGGING:
    logging.basicConfig(level=logging.INFO, filename='/var/log/beammp/beammp_players.log', format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Logging enabled.")
else:
    logging.disable(logging.CRITICAL)  # Disable logging if not enabled

# Get port from environment variable or use default value 9584
PORT = int(os.getenv('PORT', '9584'))

# Get server name filter from environment variable or use default value
SERVER_NAME_FILTER = os.getenv('SERVER_NAME_FILTER')

# Log the value of SERVER_NAME_FILTER
logging.info(f"SERVER_NAME_FILTER: {SERVER_NAME_FILTER}")

def fetch_server_data():
    url = "https://backend.beammp.com/servers"
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
    return []

def update_metrics():
    server_data = fetch_server_data()
    total_players = 0  # Initialize total players counter
    total_max_players = 0  # Initialize total max players counter
    server_map_players = defaultdict(int)  # Initialize dictionary to track players per server map
    for server in server_data:
        sname = server.get('sname')
        if SERVER_NAME_FILTER not in sname:
            continue
        
        players = int(server.get('players'))
        total_players += players  # Add players to total players counter
        
        max_players = int(server.get('maxplayers'))
        total_max_players += max_players  # Add max players to total max players counter
        
        map_name = server.get('map')
        server_map_players[map_name] += players
        
        if sname:
            server_name_metric.labels(sname)
            server_players_metric.labels(sname).set(players)  # Track number of players connected
            server_max_players_metric.labels(sname).set(max_players)  # Track max players
    
        players_list = server.get('playerslist', [])
        
        # Log server data in the desired format if logging is enabled
        if LOGGING:
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {sname}, {players_list}, Players: {players}, Max Players: {max_players}")



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
    
    # Total players metric
    total_players_metric = Gauge('beammp_total_players', 'Total number of players across all servers')
    
    # Total max players metric
    total_max_players_metric = Gauge('beammp_total_max_players', 'Total max number of players across all servers')
    
    # Server map players metric
    server_map_players_metric = Gauge('beammp_server_map_players', 'Total number of players per server map', ['map'])
    
    # Start HTTP server to expose Prometheus metrics
    start_http_server(PORT)  # Use the port defined in the environment variable or default to 9584
    
    # Update metrics and log player information every 60 seconds
    while True:
        update_metrics()
        logging.info("Player information updated.")
        time.sleep(60)  # Updated interval to 60 seconds
