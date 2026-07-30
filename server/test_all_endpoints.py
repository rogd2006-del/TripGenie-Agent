import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "http://localhost:8000"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req_headers = {"Content-Type": "application/json", **headers}
    body = json.dumps(data).encode("utf-8") if data is not None else None
    
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw_body = resp.read()
            if "application/json" in content_type:
                return resp.status, json.loads(raw_body.decode("utf-8"))
            elif "text/event-stream" in content_type:
                return resp.status, raw_body.decode("utf-8")
            else:
                return resp.status, raw_body
    except urllib.error.HTTPError as e:
        raw_err = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw_err)
        except Exception:
            return e.code, raw_err
    except Exception as err:
        return 0, str(err)

def run_all_tests():
    print("=" * 65)
    print("TripGenie Automated End-to-End API Endpoint Verification Test")
    print("=" * 65)

    passed = 0
    total = 16
    token = None
    created_trip_id = None

    # 1. GET /
    status, res = make_request(f"{BASE_URL}/")
    if status == 200 and "status" in res:
        print(f"[OK] 1/{total} GET / -> PASSED (Status: {status}, Service: {res.get('title')})")
        passed += 1
    else:
        print(f"[FAIL] 1/{total} GET / -> FAILED (Status: {status}, Res: {res})")

    # 2. GET /health
    status, res = make_request(f"{BASE_URL}/health")
    if status == 200 and "status" in res:
        print(f"[OK] 2/{total} GET /health -> PASSED (Status: {status}, DB: {res.get('database')})")
        passed += 1
    else:
        print(f"[FAIL] 2/{total} GET /health -> FAILED (Status: {status}, Res: {res})")

    # 3. GET /docs (Swagger UI)
    status, res = make_request(f"{BASE_URL}/docs")
    if status == 200:
        print(f"[OK] 3/{total} GET /docs -> PASSED (Status: {status}, Swagger UI loaded)")
        passed += 1
    else:
        print(f"[FAIL] 3/{total} GET /docs -> FAILED (Status: {status})")

    # 4. POST /api/v1/auth/register
    test_email = f"testuser_{int(time.time())}@tripgenie.ai"
    reg_payload = {
        "full_name": "Test Traveler",
        "email": test_email,
        "password": "Password123!"
    }
    status, res = make_request(f"{BASE_URL}/api/v1/auth/register", method="POST", data=reg_payload)
    if status == 200 and "access_token" in res:
        print(f"[OK] 4/{total} POST /api/v1/auth/register -> PASSED (User registered)")
        passed += 1
    else:
        print(f"[FAIL] 4/{total} POST /api/v1/auth/register -> FAILED (Status: {status}, Res: {res})")

    # 5. POST /api/v1/auth/login
    login_payload = {"email": test_email, "password": "Password123!"}
    status, res = make_request(f"{BASE_URL}/api/v1/auth/login", method="POST", data=login_payload)
    if status == 200 and "access_token" in res:
        token = res["access_token"]
        print(f"[OK] 5/{total} POST /api/v1/auth/login -> PASSED (JWT Token obtained)")
        passed += 1
    else:
        print(f"[FAIL] 5/{total} POST /api/v1/auth/login -> FAILED (Status: {status}, Res: {res})")

    auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 6. GET /api/v1/auth/profile
    status, res = make_request(f"{BASE_URL}/api/v1/auth/profile", method="GET", headers=auth_headers)
    if status == 200 and "email" in res:
        print(f"[OK] 6/{total} GET /api/v1/auth/profile -> PASSED (User: {res.get('email')})")
        passed += 1
    else:
        print(f"[FAIL] 6/{total} GET /api/v1/auth/profile -> FAILED (Status: {status}, Res: {res})")

    # 7. PUT /api/v1/user/preferences
    pref_payload = {"currency": "INR", "diet": "Vegetarian", "luxury_level": "Moderate", "model_provider": "openai"}
    status, res = make_request(f"{BASE_URL}/api/v1/user/preferences", method="PUT", data=pref_payload, headers=auth_headers)
    if status == 200 and res.get("status") == "success":
        print(f"[OK] 7/{total} PUT /api/v1/user/preferences -> PASSED (Preferences updated)")
        passed += 1
    else:
        print(f"[FAIL] 7/{total} PUT /api/v1/user/preferences -> FAILED (Status: {status}, Res: {res})")

    # 8. POST /api/v1/planner/start (Planner API / Generate Plan SSE Stream)
    plan_payload = {
        "prompt": "4-day trip to Goa under 20000 with vegetarian food and adventure sports",
        "destination": "Goa, India",
        "budget": 20000,
        "duration_days": 4,
        "travelers": 2,
        "food_preference": "Vegetarian",
        "luxury_level": "Moderate",
        "adventure_level": "High"
    }
    status, res = make_request(f"{BASE_URL}/api/v1/planner/start", method="POST", data=plan_payload, headers=auth_headers)
    if status == 200 and isinstance(res, str) and "data: " in res:
        for line in res.split("\n\n"):
            if line.startswith("data: "):
                try:
                    ev_data = json.loads(line.replace("data: ", ""))
                    if "trip_id" in ev_data:
                        created_trip_id = ev_data["trip_id"]
                except Exception:
                    pass
        print(f"[OK] 8/{total} POST /api/v1/planner/start -> PASSED (Planner API stream verified, Trip ID: {created_trip_id})")
        passed += 1
    else:
        print(f"[FAIL] 8/{total} POST /api/v1/planner/start -> FAILED (Status: {status})")

    if not created_trip_id:
        created_trip_id = "trip-demo-1234"

    # 9. POST /api/v1/planner/chat (Chat API)
    chat_payload = {"message": "Can you suggest vegetarian restaurants near Baga beach?", "trip_id": created_trip_id}
    status, res = make_request(f"{BASE_URL}/api/v1/planner/chat", method="POST", data=chat_payload, headers=auth_headers)
    if status == 200 and "reply" in res:
        print(f"[OK] 9/{total} POST /api/v1/planner/chat -> PASSED (Chat API response received)")
        passed += 1
    else:
        print(f"[FAIL] 9/{total} POST /api/v1/planner/chat -> FAILED (Status: {status}, Res: {res})")

    # 10. GET /api/v1/planner/hotels (Hotel API)
    status, res = make_request(f"{BASE_URL}/api/v1/planner/hotels?destination=Goa,%20India&luxury_level=Moderate&budget=20000", method="GET")
    if status == 200 and "hotels" in res:
        print(f"[OK] 10/{total} GET /api/v1/planner/hotels -> PASSED (Hotel API returned {res.get('total')} hotels)")
        passed += 1
    else:
        print(f"[FAIL] 10/{total} GET /api/v1/planner/hotels -> FAILED (Status: {status}, Res: {res})")

    # 11. GET /api/v1/planner/weather (Weather API)
    status, res = make_request(f"{BASE_URL}/api/v1/planner/weather?destination=Goa,%20India&duration_days=4", method="GET")
    if status == 200 and "forecast" in res:
        print(f"[OK] 11/{total} GET /api/v1/planner/weather -> PASSED (Weather API returned forecast: {res.get('temp_celsius')}°C, {res.get('condition')})")
        passed += 1
    else:
        print(f"[FAIL] 11/{total} GET /api/v1/planner/weather -> FAILED (Status: {status}, Res: {res})")

    # 12. GET /api/v1/trip/history (Trip History)
    status, res = make_request(f"{BASE_URL}/api/v1/trip/history", method="GET", headers=auth_headers)
    if status == 200 and isinstance(res, list):
        print(f"[OK] 12/{total} GET /api/v1/trip/history -> PASSED (History returned {len(res)} trips)")
        passed += 1
    else:
        print(f"[FAIL] 12/{total} GET /api/v1/trip/history -> FAILED (Status: {status}, Res: {res})")

    # 13. GET /api/v1/trip/{trip_id} (Trip Details: Map, Hotels, Weather, Transport)
    status, res = make_request(f"{BASE_URL}/api/v1/trip/{created_trip_id}", method="GET", headers=auth_headers)
    if status == 200 and ("title" in res or "destination" in res):
        print(f"[OK] 13/{total} GET /api/v1/trip/{created_trip_id} -> PASSED (Trip components loaded)")
        passed += 1
    else:
        print(f"[FAIL] 13/{total} GET /api/v1/trip/{created_trip_id} -> FAILED (Status: {status}, Res: {res})")

    # 14. POST /api/v1/trip/save/{trip_id} (Bookmark Trip)
    status, res = make_request(f"{BASE_URL}/api/v1/trip/save/{created_trip_id}", method="POST", data={}, headers=auth_headers)
    if status == 200 and res.get("status") == "saved":
        print(f"[OK] 14/{total} POST /api/v1/trip/save/{created_trip_id} -> PASSED (Trip saved)")
        passed += 1
    else:
        print(f"[FAIL] 14/{total} POST /api/v1/trip/save/{created_trip_id} -> FAILED (Status: {status}, Res: {res})")

    # 15. GET /api/v1/trip/{trip_id}/pdf (Download PDF Report)
    status, res = make_request(f"{BASE_URL}/api/v1/trip/{created_trip_id}/pdf", method="GET", headers=auth_headers)
    if status == 200 and isinstance(res, bytes) and res.startswith(b"%PDF"):
        print(f"[OK] 15/{total} GET /api/v1/trip/{created_trip_id}/pdf -> PASSED (PDF stream generated: {len(res)} bytes)")
        passed += 1
    else:
        print(f"[FAIL] 15/{total} GET /api/v1/trip/{created_trip_id}/pdf -> FAILED (Status: {status})")

    # 16. DELETE /api/v1/trip/{trip_id} (Delete Trip)
    status, res = make_request(f"{BASE_URL}/api/v1/trip/{created_trip_id}", method="DELETE", headers=auth_headers)
    if status == 200 and res.get("status") == "deleted":
        print(f"[OK] 16/{total} DELETE /api/v1/trip/{created_trip_id} -> PASSED (Trip deleted)")
        passed += 1
    else:
        print(f"[FAIL] 16/{total} DELETE /api/v1/trip/{created_trip_id} -> FAILED (Status: {status}, Res: {res})")

    # 17. POST /api/v1/booking/create (Create Booking)
    created_booking_id = None
    booking_payload = {
        "trip_id": created_trip_id,
        "destination": "Goa, India",
        "duration_days": 4
    }
    status, res = make_request(f"{BASE_URL}/api/v1/booking/create", method="POST", data=booking_payload, headers=auth_headers)
    if status == 200 and "booking_id" in res:
        created_booking_id = res["booking_id"]
        print(f"[OK] 17/21 POST /api/v1/booking/create -> PASSED (Booking created: {created_booking_id})")
        passed += 1
    else:
        print(f"[FAIL] 17/21 POST /api/v1/booking/create -> FAILED (Status: {status}, Res: {res})")

    if not created_booking_id:
        created_booking_id = "BK-TEST1234"

    # 18. GET /api/v1/booking/{booking_id}
    status, res = make_request(f"{BASE_URL}/api/v1/booking/{created_booking_id}", method="GET")
    if status == 200 and "booking_id" in res:
        print(f"[OK] 18/21 GET /api/v1/booking/{created_booking_id} -> PASSED (Status: {res.get('status')})")
        passed += 1
    else:
        print(f"[FAIL] 18/21 GET /api/v1/booking/{created_booking_id} -> FAILED (Status: {status})")

    # 19. POST /api/v1/booking/{booking_id}/pay (Simulate Payment)
    status, res = make_request(f"{BASE_URL}/api/v1/booking/{created_booking_id}/pay", method="POST", data={"payment_method": "UPI"})
    if status == 200 and res.get("status") == "Paid":
        print(f"[OK] 19/21 POST /api/v1/booking/{created_booking_id}/pay -> PASSED (Paid ID: {res.get('payment_id')})")
        passed += 1
    else:
        print(f"[FAIL] 19/21 POST /api/v1/booking/{created_booking_id}/pay -> FAILED (Status: {status}, Res: {res})")

    # 20. GET /api/v1/booking/{booking_id}/pdf/ticket (Download Ticket PDF)
    status, res = make_request(f"{BASE_URL}/api/v1/booking/{created_booking_id}/pdf/ticket", method="GET")
    if status == 200 and isinstance(res, bytes) and res.startswith(b"%PDF"):
        print(f"[OK] 20/21 GET /api/v1/booking/{created_booking_id}/pdf/ticket -> PASSED (Ticket PDF generated: {len(res)} bytes)")
        passed += 1
    else:
        print(f"[FAIL] 20/21 GET /api/v1/booking/{created_booking_id}/pdf/ticket -> FAILED (Status: {status})")

    # 21. GET /api/v1/booking/{booking_id}/pdf/receipt (Download Receipt PDF)
    status, res = make_request(f"{BASE_URL}/api/v1/booking/{created_booking_id}/pdf/receipt", method="GET")
    if status == 200 and isinstance(res, bytes) and res.startswith(b"%PDF"):
        print(f"[OK] 21/21 GET /api/v1/booking/{created_booking_id}/pdf/receipt -> PASSED (Receipt PDF generated: {len(res)} bytes)")
        passed += 1
    else:
        print(f"[FAIL] 21/21 GET /api/v1/booking/{created_booking_id}/pdf/receipt -> FAILED (Status: {status})")

    print("=" * 65)
    print(f"SUMMARY: {passed}/21 API Endpoints Verified Successfully!")
    print("=" * 65)
    
    return passed == 21

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

