"""Teste rápido da API."""
import httpx
import json

base = "http://localhost:8000"

# 1. Health
r = httpx.get(f"{base}/api/health")
print("HEALTH:", json.dumps(r.json(), indent=2))

# 2. Register
r = httpx.post(f"{base}/api/auth/register", json={
    "name": "Dr. Teste",
    "email": "admin@eeg.com",
    "password": "admin123",
    "role": "admin",
    "crm": "CRM-12345",
})
print("REGISTER:", r.status_code)

# 3. Login
r = httpx.post(
    f"{base}/api/auth/login",
    data={"username": "admin@eeg.com", "password": "admin123"},
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
token = r.json()["access_token"]
print("LOGIN: OK")

# 4. Create patient
headers = {"Authorization": f"Bearer {token}"}
r = httpx.post(f"{base}/api/patients/", json={"name": "Isaac Gomes Bueno"}, headers=headers)
pid = r.json()["id"]
print(f"PATIENT: created id={pid}")

# 5. List patients
r = httpx.get(f"{base}/api/patients/", headers=headers)
print(f"PATIENTS: {len(r.json())} found")

print("\n=== ALL TESTS OK ===")
