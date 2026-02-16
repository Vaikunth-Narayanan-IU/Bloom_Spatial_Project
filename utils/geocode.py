from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable
import time

def get_lat_long(address):
    """
    Geocodes an address string using OpenStreetMap Nominatim.
    Returns (lat, lng, formatted_address) or (None, None, error_message)
    """
    if not address or not address.strip():
        return None, None, "No address provided"

    # Nominatim requires a user_agent
    geolocator = Nominatim(user_agent="bloom_spatial_demo_prototype_v1")

    try:
        # Simple retry logic
        location = None
        for attempt in range(2):
            try:
                location = geolocator.geocode(address, timeout=10)
                if location:
                    break
            except (GeocoderTimedOut, GeocoderUnavailable):
                time.sleep(1) # Wait a bit before retrying
                continue
        
        if location:
            return location.latitude, location.longitude, location.address
        else:
            return None, None, "Address not found"

    except GeocoderServiceError as e:
        return None, None, f"Geocoding service error: {str(e)}"
    except Exception as e:
        return None, None, f"Error: {str(e)}"
