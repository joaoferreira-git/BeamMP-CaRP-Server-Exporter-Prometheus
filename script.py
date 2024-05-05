from prometheus_client import start_http_server, Gauge, Info
import requests
import json
import time

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
    for server in server_data:
        sname = server.get('sname')
        if "[^b🐟 CaRP^r Test Server]" not in sname:
            continue
        
        players = int(server.get('players', 0))  # Set players to 0 if not present
        players_list = server.get('playerslist', "").split(',')
        ip = server.get('ip')
        port = server.get('port')
        version = server.get('version')
        cversion = server.get('cversion')
        
        if sname:
            server_name_metric.labels(sname)
            server_players_metric.labels(sname).set(players)  # Track number of players connected
            server_ip_metric.labels(sname).info({"ip": ip})  # Update as Info metric
            server_port_metric.labels(sname).info({"port": port})  # Update as Info metric
            server_version_metric.labels(sname).info({"version": version})  # Update as Info metric
            server_cversion_metric.labels(sname).info({"cversion": cversion})  # Update as Info metric
            
            # Track individual players
            for player in players_list:
                player_metric.labels(sname, player).set(1)

if __name__ == '__main__':
    # Define Prometheus metrics
    server_name_metric = Info('beammp_server_name', 'Name of BeamMP servers', ['sname'])
    server_players_metric = Gauge('beammp_server_players', 'Number of players on BeamMP servers', ['sname'])
    server_ip_metric = Info('beammp_server_ip', 'IP address of BeamMP servers', ['sname'])
    server_port_metric = Info('beammp_server_port', 'Port of BeamMP servers', ['sname'])
    server_version_metric = Info('beammp_server_version', 'Version of BeamMP servers', ['sname'])
    server_cversion_metric = Info('beammp_server_cversion', 'Cversion of BeamMP servers', ['sname'])
    
    # Player metric to track individual players
    player_metric = Gauge('beammp_player_list', 'Player List in Each Server', ['sname', 'player'])
    
    # Start HTTP server to expose Prometheus metrics
    start_http_server(9584)  # Changed port to 9584
    
    # Update metrics every 60 seconds
    while True:
        update_metrics()
        time.sleep(60)  # Updated interval to 60 seconds
