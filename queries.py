import redis
import requests
import json
from redis.commands.json.path import Path
from redis.commands.search.field import TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

# ------------------ Redis Cloud connection ------------------ #
REDIS_HOST = "redis-19670.crce174.ca-central-1-1.ec2.redns.redis-cloud.com"
REDIS_PORT = 19670
REDIS_PASSWORD = "21xfyDd0gMXkIwSNlJRDN5q3QXKADod6"

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# ------------------ Step 1 : Clean old keys ------------------ #
print("🧹 Deleting old STRING keys ...")
old_keys = r.keys("prizes:*")
if old_keys:
    r.delete(*old_keys)
    print(f"Deleted {len(old_keys)} old keys.")
else:
    print("No existing keys found.")

# ------------------ Step 2 : Fetch Nobel API ------------------ #
print("\n🌐 Fetching Nobel Prize data ...")
url = "https://api.nobelprize.org/v1/prize.json"
response = requests.get(url)
data = response.json()["prizes"]

filtered = [p for p in data if p.get("year").isdigit() and 2013 <= int(p["year"]) <= 2023]
print(f"Loaded {len(filtered)} prize entries for 2013–2023.")

# ------------------ Step 3 : Store as JSON ------------------ #
for prize in filtered:
    year = prize["year"]
    category = prize["category"]
    key = f"prizes:{year}:{category}"
    r.json().set(key, Path.root_path(), prize)
print(f"✅ Stored {len(filtered)} JSON documents in Redis Cloud.")

# ------------------ Step 4 : Create / Re-create Index ------------------ #
print("\n⚙️ Creating RediSearch index ...")
try:
    r.ft("idx_prizes").dropindex(delete_documents=False)
    print("Old index dropped.")
except Exception:
    pass

r.ft("idx_prizes").create_index(
    [
        TextField("$.year", as_name="year"),
        TextField("$.category", as_name="category"),
        TextField("$.laureates[*].firstname", as_name="firstname"),
        TextField("$.laureates[*].surname", as_name="surname"),
        TextField("$.laureates[*].motivation", as_name="motivation"),
    ],
    definition=IndexDefinition(prefix=["prizes:"], index_type=IndexType.JSON)
)
print("✅ Index 'idx_prizes' created successfully.")

# ------------------ Step 5 : Verify ------------------ #
count = len(r.keys("prizes:*"))
print(f"\n📦 Redis now contains {count} JSON documents.")
print("Use Redis Insight → Browser → Key Type = JSON to confirm structure.")
print("You can now run queries.py — results will appear correctly 🎉")
