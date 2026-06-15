import json
from fastapi.testclient import TestClient
from spin10_enterprise_core import app

def run_api_test():
    print("Wykonanie automated calls REST API w silniku Enterprise FastAPI...\n")
    print('Request: curl -X POST "https://cloud.shz-quantum.com/enterprise/simulate-gauge-graph?nodes=100000&sweeps=10"')
    
    # Creating a virtual HTTP test client
    client = TestClient(app)
    
    # Executing a real POST request to our microservice
    response = client.post("/enterprise/simulate-gauge-graph?nodes=100000&sweeps=10")
    
    print("\nJSON Server Response (SaaS Cloud):")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    run_api_test()
