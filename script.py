from prometheus_client import start_http_server, Gauge
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
        server_ident = server.get('ident')
        players = int(server.get('players', 0))  # Set players to 0 if not present
        if server_ident:
            server_players_metric.labels(server_ident).set(players)

if __name__ == '__main__':
    # Define Prometheus metrics
    server_players_metric = Gauge('beammp_server_players', 'Number of players on BeamMP servers', ['server_ident'])
    
    # Start HTTP server to expose Prometheus metrics
    start_http_server(9584)
    
    # Update metrics every 30 seconds
    while True:
        update_metrics()
        time.sleep(60)
