import grpc
from concurrent import futures
import time
import redis
import json

import nobel_pb2
import nobel_pb2_grpc

# ---------- Redis connection ----------
REDIS_HOST = "redis-19670.crce174.ca-central-1-1.ec2.redns.redis-cloud.com"
REDIS_PORT = 19670
REDIS_PASSWORD = "21xfyDd0gMXkIwSNlJRDN5q3QXKADod6"

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# ---------- Service Implementation ----------
class NobelServiceServicer(nobel_pb2_grpc.NobelServiceServicer):

    def GetLaureateCountByCategory(self, request, context):

        # Year as TEXT, so we check each year individually
        years = [str(y) for y in range(request.start_year, request.end_year + 1)]
        query = " | ".join(f"@year:{{{y}}}" for y in years)
        q = f"@category:{{{request.category}}} ({query})"
        results = r.ft("idx_prizes").search(q)
        total = 0
        for doc in results.docs:
            laureates = r.json().get(doc.id, "$.laureates")[0]
            total += len(laureates)
        return nobel_pb2.LaureateCountResponse(total_laureates=total)

    def GetLaureateCountByKeyword(self, request, context):
        q = f"@motivation:({request.keyword}*)"
        results = r.ft("idx_prizes").search(q)
        return nobel_pb2.LaureateCountResponse(total_laureates=results.total)

    def GetLaureateInfoByName(self, request, context):
        q = f"@firstname:({request.firstname}) @surname:({request.lastname})"
        results = r.ft("idx_prizes").search(q)
        if results.total == 0:
            return nobel_pb2.LaureateInfoResponse(year="", category="", motivations=[])
        data = r.json().get(results.docs[0].id)
        motivations = [
            l["motivation"] for l in data["laureates"]
            if l.get("firstname") == request.firstname and l.get("surname") == request.lastname
        ]
        return nobel_pb2.LaureateInfoResponse(
            year=data["year"], category=data["category"], motivations=motivations
        )

# ---------- Start Server ----------
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nobel_pb2_grpc.add_NobelServiceServicer_to_server(NobelServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("🚀 gRPC Server running on port 50051 ...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
