import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

access_token = utils.load_config("access_token")
headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

payload = {
    "name": "Admin Created User",
    "email": "admincreated@example.com",
    "password": "password123",
    "role": "user"
}

utils.send_and_print(
    url=f"{BASE_URL}/users",
    method="POST",
    headers=headers,
    body=payload,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)