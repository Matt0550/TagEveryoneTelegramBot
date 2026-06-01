import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

openapi_schema = app.openapi()
with open(os.path.join(os.path.dirname(__file__), "openapi.json"), "w") as f:
    json.dump(openapi_schema, f, indent=2)

print("openapi.json generated successfully.")
