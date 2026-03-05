from fastapi import APIRouter
from app.models.technician import ServiceCategory

router = APIRouter(prefix="/services", tags=["Services"])

SERVICE_INFO = {
    ServiceCategory.PLUMBER: {
        "name": "Plumber",
        "icon": "🔧",
        "description": "Pipe leaks, tap repair, bathroom fitting, water tank cleaning",
        "emergency_keywords": ["leak", "burst", "flood", "overflow"],
        "avg_response_time": "15-30 mins",
        "color": "#3B82F6"
    },
    ServiceCategory.ELECTRICIAN: {
        "name": "Electrician",
        "icon": "⚡",
        "description": "Wiring, short circuit, switchboard repair, fan fitting",
        "emergency_keywords": ["spark", "short circuit", "shock", "no power"],
        "avg_response_time": "20-40 mins",
        "color": "#F59E0B"
    },
    ServiceCategory.GAS_SERVICE: {
        "name": "Gas Service",
        "icon": "🔥",
        "description": "Gas cylinder, pipeline repair, stove servicing",
        "emergency_keywords": ["gas smell", "leak", "hissing"],
        "avg_response_time": "10-20 mins",
        "color": "#EF4444"
    },
    ServiceCategory.BIKE_MECHANIC: {
        "name": "Bike Mechanic",
        "icon": "🏍️",
        "description": "Puncture, engine repair, oil change, battery jump",
        "emergency_keywords": ["not starting", "breakdown", "puncture"],
        "avg_response_time": "20-45 mins",
        "color": "#8B5CF6"
    },
    ServiceCategory.MOBILE_TECHNICIAN: {
        "name": "Mobile Repair",
        "icon": "📱",
        "description": "Screen replacement, charging port, battery, software fix",
        "emergency_keywords": ["broken", "cracked", "not turning on"],
        "avg_response_time": "30-60 mins",
        "color": "#06B6D4"
    },
    ServiceCategory.CLEANING_SERVICE: {
        "name": "Cleaning",
        "icon": "🧹",
        "description": "House cleaning, sofa cleaning, deep clean, pest control",
        "emergency_keywords": [],
        "avg_response_time": "1-3 hours",
        "color": "#10B981"
    },
    ServiceCategory.AC_TECHNICIAN: {
        "name": "AC Technician",
        "icon": "❄️",
        "description": "AC servicing, gas refill, installation, not cooling fix",
        "emergency_keywords": ["not cooling", "leaking water"],
        "avg_response_time": "30-60 mins",
        "color": "#60A5FA"
    },
    ServiceCategory.CARPENTER: {
        "name": "Carpenter",
        "icon": "🪚",
        "description": "Furniture repair, door fitting, cupboard, wood work",
        "emergency_keywords": [],
        "avg_response_time": "1-2 hours",
        "color": "#D97706"
    },
    ServiceCategory.PAINTER: {
        "name": "Painter",
        "icon": "🎨",
        "description": "Wall painting, waterproofing, texture paint, touch up",
        "emergency_keywords": [],
        "avg_response_time": "1-2 hours",
        "color": "#EC4899"
    },
}

@router.get("/")
def get_services():
    return [
        {
            "id": category.value,
            "category": category.value,
            **info
        }
        for category, info in SERVICE_INFO.items()
    ]

@router.get("/{category}")
def get_service_detail(category: ServiceCategory):
    info = SERVICE_INFO.get(category)
    if not info:
        return {"error": "Service not found"}
    return {"id": category.value, "category": category.value, **info}
