import requests
import json
from datetime import datetime

url = "https://api.github.com/users/octocat"
response = requests.get(url)
data = response.json()

# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# filename = f"data/raw/octocat_{timestamp}.json"

# with open(filename, "w") as f:
#     json.dump(data, f, indent=2)

# print(f"Status Code: {response.status_code}")
# print(f"Data: {response.json()}")
# print(f"First few fields:")
# print(f"Login: {data.get('login')}")
# print(f"Name: {data.get('name')}")
# print(f"Public repos: {data.get('public_repos')}")

login = data.get('login')
name = data.get('name')
repos = data.get('public_repos')
followers = data.get('followers')
created = data.get('created_at')
company = data.get('company')
location = data.get('location')


print("=" * 30)
print("GITHUB USER INFO")
print("=" * 30)
print(f"Login: {login}")
print(f"Name: {name}")
print(f"Repos: {repos}")
print(f"Followers: {followers}")
print(f"Created: {created}")
print(f"Company: {company}")
print(f"Location: {location}")