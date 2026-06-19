import math

def get_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in KM

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1) * math.cos(lat2) *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
def get_bot_reply(message):
    msg = message.lower()

    if "booking" in msg:
        return "📅 Check My Bookings section."
    elif "payment" in msg:
        return "💰 Payment after job completion."
    elif "worker" in msg:
        return "👷 Worker assigned based on location."
    elif "cancel" in msg:
        return "❌ Cancel before work starts."
    else:
        return "🤖 Hi! How can I help you today?"