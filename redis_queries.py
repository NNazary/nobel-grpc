import redis
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

# *********** Redis Cloud connection **************#
REDIS_HOST = "redis-19670.crce174.ca-central-1-1.ec2.redns.redis-cloud.com"
REDIS_PORT = 19670
REDIS_PASSWORD = "21xfyDd0gMXkIwSNlJRDN5q3QXKADod6"

# ********* Connect to Redis ********#
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# ******** Create Index ********#
try:
    r.ft("idx_prizes").create_index(
        [
            NumericField("$.year", as_name="year"),
            TextField("$.category", as_name="category"),
            TextField("$.laureates[*].firstname", as_name="firstname"),
            TextField("$.laureates[*].surname", as_name="surname"),
            TextField("$.laureates[*].motivation", as_name="motivation"),
        ],
        definition=IndexDefinition(prefix=["prizes:"], index_type=IndexType.JSON)
    )
    print("✅ Index created successfully.")
except Exception as e:
    print("Index already exists or creation failed:", e)

# Optional: verify index
try:
    print("Indexes available:", r.execute_command("FT._LIST"))
except Exception as e:
    print("Could not list indexes:", e)
