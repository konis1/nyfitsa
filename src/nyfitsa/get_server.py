import requests

from requests import Response

response: Response = requests.get("http://www.google.com", timeout=10)

print(response.headers)
