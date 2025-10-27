import redis
import requests
import json

# ***********redis-db conn**************#
REDIS_HOST = "redis-19670.crce174.ca-central-1-1.ec2.redns.redis-cloud.com"
REDIS_PORT = 19670
REDIS_PASSWORD = "21xfyDd0gMXkIwSNlJRDN5q3QXKADod6"

# *********redis connection cred ******#
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

###*******nobel api conn ****##
url = "https://api.nobelprize.org/v1/prize.json"
response = requests.get(url)
data = response.json()

prizes = data["prizes"]

# ************* 2013–2023***#
filtered = [p for p in prizes if p.get("year").isdigit() and 2013 <= int(p["year"]) <= 2023]



#****************** loading nobel into redis cloud db ***********
for prize in filtered:
    year = prize["year"]
    category = prize["category"]
    key = f"prizes:{year}:{category}"

    # Convert dict to string before storing
    r.set(key, json.dumps(prize), nx=True)
    print(f"Stored {key}")
