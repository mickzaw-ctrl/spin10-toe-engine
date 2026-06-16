import json
from fastapi.testclient import TestClient
from spin10_enterprise_core import app

def run_api_test():
    print("Wykonanie zautomatyzowanego wywolania REST API w engineu Enterprise FastAPI...\n")
    print('Zapytanie: curl -X POST "https://cloud.shz-quantum.com/enterprise/simulate-gauge-graph?nodes=100000&sweeps=10"')
    
    # Tworzymy wirtualnego klienta testowego HTTP
    client = TestClient(app)
    
    # Wykonujemy rzeczywiste zapytanie POST do naszej mikrouslugi
    response = client.post("/enterprise/simulate-gauge-graph?nodes=100000&sweeps=10")
    
    print("\nOdpowiedz Serwera JSON (SaaS Cloud):")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    run_api_test()
