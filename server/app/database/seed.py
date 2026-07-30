import asyncio
from datetime import datetime
from app.utils.security import get_password_hash
from app.database.connection import db_manager
from app.utils.logger import logger

SEED_USERS = [
    {
        "_id": "user-demo-1",
        "email": "demo@tripgenie.ai",
        "full_name": "Alex Traveler",
        "password": get_password_hash("password123"),
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        "preferences": {
            "currency": "INR",
            "diet": "Vegetarian",
            "luxury_level": "Moderate",
            "model_provider": "openai"
        },
        "created_at": datetime.utcnow().isoformat()
    }
]

SEED_TRIPS = [
    {
        "_id": "trip-goa-demo",
        "user_id": "user-demo-1",
        "title": "4-Day Tropical Goa Adventure & Beach Escape",
        "destination": "Goa, India",
        "budget": 20000,
        "estimated_total": 18500,
        "currency": "INR",
        "duration_days": 4,
        "travelers": 2,
        "food_preference": "Vegetarian",
        "luxury_level": "Moderate",
        "adventure_level": "High",
        "cover_image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
        "is_saved": True,
        "summary": "A high-energy 4-day trip to North & South Goa featuring sun-drenched beaches, vibrant night markets, heritage Portuguese walks, water sports, and delicious local vegetarian thalis.",
        "itinerary": [
            {
                "day": 1,
                "title": "Baga & Calangute Beach Exploration + Water Sports",
                "weather": "30°C Sunny with coastal breeze",
                "activities": [
                    {"time": "09:00 AM", "activity": "Arrival in North Goa & Check-in at Sea Breeze Resort", "location": "Calangute"},
                    {"time": "11:30 AM", "activity": "Parasailing & Banana Boat Rides at Baga Beach", "location": "Baga Beach"},
                    {"time": "02:00 PM", "activity": "Lunch at Bean Me Up (Organic Vegetarian Bistro)", "location": "Anjuna"},
                    {"time": "05:30 PM", "activity": "Sunset views & coconut water at Fort Aguada", "location": "Candolim"},
                    {"time": "08:00 PM", "activity": "Evening dinner at Blue Planet Cafe & Tito's Lane Stroll", "location": "Baga"}
                ]
            },
            {
                "day": 2,
                "title": "Scuba Diving, Grand Island & Spice Plantation",
                "weather": "29°C Clear skies",
                "activities": [
                    {"time": "07:30 AM", "activity": "Boat ride to Grand Island for Scuba Diving & Snorkeling", "location": "Sinquerim Jetty"},
                    {"time": "01:30 PM", "activity": "Authentic Goan Veg Buffet at Sahakari Spice Farm", "location": "Ponda"},
                    {"time": "04:30 PM", "activity": "Walk through Old Goa Churches (Basilica of Bom Jesus)", "location": "Old Goa"},
                    {"time": "08:30 PM", "activity": "Dinner at Navtara Pure Veg Restaurant", "location": "Panaji"}
                ]
            },
            {
                "day": 3,
                "title": "South Goa Tranquility & Palolem Sunset",
                "weather": "31°C Pleasant",
                "activities": [
                    {"time": "09:00 AM", "activity": "Drive to South Goa & Check out Cabo de Rama Fort", "location": "Cabo de Rama"},
                    {"time": "01:00 PM", "activity": "Lunch at Zest Vegan Cafe", "location": "Agonda"},
                    {"time": "04:00 PM", "activity": "Kayaking among mangroves at Palolem Beach", "location": "Palolem Beach"},
                    {"time": "07:30 PM", "activity": "Beachside candlelit dinner with live music", "location": "Palolem"}
                ]
            },
            {
                "day": 4,
                "title": "Panaji Latin Quarter & Souvenir Shopping",
                "weather": "28°C Partial Clouds",
                "activities": [
                    {"time": "10:00 AM", "activity": "Heritage street walk through Fontainhas (Latin Quarter)", "location": "Panaji"},
                    {"time": "01:00 PM", "activity": "Traditional Goan Thali Lunch at Kokni Kanteen", "location": "Panaji"},
                    {"time": "03:30 PM", "activity": "Cashew & Feni shopping at local market", "location": "Panaji Market"},
                    {"time": "06:00 PM", "activity": "Mandovi River Sunset Cruise & Airport Departure", "location": "Panaji Jetty"}
                ]
            }
        ],
        "hotels": [
            {
                "name": "Sea Breeze Resort & Spa",
                "rating": 4.5,
                "price_per_night": 3500,
                "amenities": ["Pool", "Free WiFi", "Near Beach", "Breakfast Included"],
                "address": "Calangute Beach Road, North Goa",
                "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=500&q=80"
            },
            {
                "name": "Palolem Eco Beach Huts",
                "rating": 4.7,
                "price_per_night": 2800,
                "amenities": ["Sea View", "Eco-friendly", "Yoga Deck"],
                "address": "Palolem Beach, South Goa",
                "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=500&q=80"
            }
        ],
        "restaurants": [
            {
                "name": "Bean Me Up Vegan Bistro",
                "cuisine": "Global Vegetarian / Organic",
                "rating": 4.8,
                "avg_cost_two": 800,
                "specialty": "Tofu Steaks & Smoothies"
            },
            {
                "name": "Navtara Pure Veg",
                "cuisine": "North & South Indian Veg",
                "rating": 4.6,
                "avg_cost_two": 600,
                "specialty": "Goan Veg Curry & Dosa"
            }
        ],
        "transport": {
            "recommended": "Self-drive Scooter / Rental Car",
            "estimated_cost": 2400,
            "flight_train_note": "Fly into GOI (Dabolim) or GOX (Mopa Airport). Pre-booked taxi to Calangute approx ₹1,200."
        },
        "budget_breakdown": {
            "stay": 9000,
            "food": 4500,
            "activities": 3000,
            "transport": 2000,
            "contingency": 1500,
            "total": 20000
        },
        "packing_list": [
            "Breathable cotton clothes & swimwear",
            "Sunscreen (SPF 50+)",
            "Waterproof dry bag for water sports",
            "Reusable water bottle",
            "Flip flops & comfortable walking sandals",
            "Universal power bank"
        ],
        "emergency_contacts": [
            {"name": "Goa Tourist Helpline", "phone": "1364"},
            {"name": "Police Control Room", "phone": "100"},
            {"name": "Medical Emergency", "phone": "108"}
        ],
        "created_at": datetime.utcnow().isoformat()
    }
]

async def seed_data():
    if db_manager.use_fallback:
        db_manager.in_memory_store["users"] = SEED_USERS
        db_manager.in_memory_store["trips"] = SEED_TRIPS
        db_manager.in_memory_store["savedTrips"] = SEED_TRIPS
        logger.info("Seeded in-memory fallback database with demo user & trip.")
    else:
        try:
            db = db_manager.db
            users_count = await db["users"].count_documents({})
            if users_count == 0:
                await db["users"].insert_many(SEED_USERS)
                await db["trips"].insert_many(SEED_TRIPS)
                await db["savedTrips"].insert_many(SEED_TRIPS)
                logger.info("Successfully seeded MongoDB database.")
        except Exception as e:
            logger.warning(f"Error seeding DB: {e}")

if __name__ == "__main__":
    asyncio.run(seed_data())
