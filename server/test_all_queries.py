import asyncio
import json
import sys
from app.services.chat_service import chat_service

queries = [
    "Hi",
    "Hotels in Varkala",
    "Nearby waterfalls",
    "Weather today",
    "3-day itinerary for Goa"
]

def safe_str(s):
    return str(s).encode('ascii', 'ignore').decode('ascii')

async def run_tests():
    print("=" * 60)
    print("RUNNING TRIPGENIE BACKEND CHATBOT VERIFICATION SUITE")
    print("=" * 60)
    
    all_passed = True
    results = []

    for idx, query in enumerate(queries, 1):
        print(f"\n[Test {idx}/5] Query: '{query}'")
        try:
            res = await chat_service.process_chat_message(
                message=query,
                trip_id="test_session_1",
                user_info={"id": "user-test-1", "email": "test@tripgenie.ai"}
            )
            reply = res.get("reply", "")
            intent = res.get("intent", "UNKNOWN")
            agents = res.get("agents_used", [])
            
            if reply and len(reply) > 20:
                print(f"[SUCCESS] PASSED | Intent: {safe_str(intent)} | Agents: {safe_str(agents)} | Reply Length: {len(reply)} chars")
                print(f"Preview: {safe_str(reply[:120])}...\n")
                results.append({"query": query, "status": "PASSED", "intent": intent, "reply_len": len(reply)})
            else:
                print(f"[FAIL] FAILED | Empty or short reply returned!")
                all_passed = False
                results.append({"query": query, "status": "FAILED", "reason": "Empty reply"})

        except Exception as e:
            print(f"[ERROR] CRITICAL FAILURE | Uncaught Exception: {safe_str(e)}")
            import traceback
            traceback.print_exc()
            all_passed = False
            results.append({"query": query, "status": "CRITICAL_FAILURE", "error": str(e)})

    print("=" * 60)
    print("TEST SUITE SUMMARY:")
    for r in results:
        status_symbol = "[OK]" if r["status"] == "PASSED" else "[FAIL]"
        print(f"{status_symbol} {r['query']} -> {r['status']} ({safe_str(r.get('intent'))})")
    print("=" * 60)

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_tests())
