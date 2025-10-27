import grpc
import nobel_pb2
import nobel_pb2_grpc

def run():
    with grpc.insecure_channel("nobel-grpc.kindsea-11b108f2.canadacentral.azurecontainerapps.io:50051") as channel:
        stub = nobel_pb2_grpc.NobelServiceStub(channel)

        # ---- Query 1 ----
        print("\n🔹 Query 1: Count by category and year")
        resp1 = stub.GetLaureateCountByCategory(
            nobel_pb2.CategoryYearRequest(category="physics", start_year=2013, end_year=2023)
        )
        print("Total laureates in physics (2013–2023):", resp1.total_laureates)

        # ---- Query 2 ----
        print("\n🔹 Query 2: Keyword search 'quantum'")
        resp2 = stub.GetLaureateCountByKeyword(
            nobel_pb2.KeywordRequest(keyword="quantum")
        )
        print("Mentions of 'quantum':", resp2.total_laureates)

        # ---- Query 3 ----
        print("\n🔹 Query 3: Laureate by name")
        resp3 = stub.GetLaureateInfoByName(
            nobel_pb2.NameRequest(firstname="Peter", lastname="Higgs")
        )
        print("Year:", resp3.year)
        print("Category:", resp3.category)
        print("Motivation(s):", list(resp3.motivations))

if __name__ == "__main__":
    run()
