import requests

def call_ica_db(url, payload, token):
    try:
        headers = {
        "Content-Type": "application/json",
        "X-TENANT": "QSR",
        "X-USER-ID": "manusha",
        "X-AUTHORIZATION": token
        }
        # print(f"Making POST request to {url} with body: {json.dumps(req_body, indent=2)}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
       
        # print('External API Response:', response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Error calling API: {e}')
        return None