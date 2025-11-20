import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    
    return distance

def is_within_geofence(
    student_lat: float,
    student_lon: float,
    class_lat: float,
    class_lon: float,
    radius: float
) -> tuple[bool, float]:
    distance = haversine_distance(student_lat, student_lon, class_lat, class_lon)
    is_within = distance <= radius
    
    return is_within, distance