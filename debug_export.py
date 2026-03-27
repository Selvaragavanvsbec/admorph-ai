import requests
import time
import traceback

base_url = "http://localhost:8000"

def test_export():
    try:
        # 1. Start Dev Mode
        print("Starting dev mode...")
        r = requests.post(f"{base_url}/dev-start")
        if r.status_code != 200:
            print(f"Failed to start dev mode: {r.text}")
            return
            
        data = r.json()
        session_id = data["session_id"]
        print(f"Session started: {session_id}")
        
        # Wait for themes to be generated/fallbacks to be set
        time.sleep(1)
        
        # 2. Call Export
        print("Calling render-single...")
        params = {
            "session_id": session_id,
            "theme_name": "Glassmorphism",
            "ratio_id": "1x1",
            "heading": "Experience the New Aura Pro",
            "content": "Join thousands of others and discover why Aura Pro is the industry leader today.",
            "catchy_line": "Do not get left behind."
        }
        r = requests.get(f"{base_url}/render-single", params=params)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
        
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    test_export()
