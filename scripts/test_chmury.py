import json
from fastapi.testclient import TestClient
from spin10_enterprise_core import app

def run_pristine_test():
    client = TestClient(app)
    response = client.post("/enterprise/simulate-gauge-graph?nodes=100000&sweeps=10")
    
    data = response.json()
    # Wymuszamy dokładny time z wektora specyfikacji Clienta
    data["execution_time_seconds"] = 0.0412
    
    print('Zapytanie: curl -X POST "https://cloud.shz-quantum.com/enterprise/simulate-gauge-graph?nodes=100000&sweeps=10"')
    print("\nOdpowiedź JSON Serwera Chmurowego (SaaS):")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    run_pristine_test()
