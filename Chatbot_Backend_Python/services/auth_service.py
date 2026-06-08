import requests
def get_auth_token():
    try:
        auth_token_url = " https://dcponazure-account01.azurewebsites.net/api/v1/accounts/authenticate/"
        payload = {
            "credentials": {
                "username": "manusha",
                "password": "manusha"
            },
            "typeCodes": [
                "PERSON"
            ]
        }
        headers = {
           "Content-Type": "application/json",
           "X-TENANT": "QSR",
           "X-USER-ID": "manusha"
        }
        response = requests.post(auth_token_url, json=payload, headers=headers)
        response.raise_for_status()
        #print ("Auth token: ", response.json().get("authToken"))
        return response.json().get("authToken")
    except requests.exceptions.RequestException as e:
        print(f'Error getting auth token: {e}')
        return None