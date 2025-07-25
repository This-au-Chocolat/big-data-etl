import requests

def fetch_json(url, params=None):
    print(f"Fetching URL: {url} with params: {params}")
    try:
        response = requests.get(url, params=params)
        print(f"Status code: {response.status_code}")
        response.raise_for_status()
        json_data = response.json()
        print(f"Received data: {str(json_data)[:500]}")  # Muestra los primeros 500 caracteres
        return json_data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        raise