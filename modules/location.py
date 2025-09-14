import geocoder
from typing import Optional, Tuple, Dict, Any
import logging

class Location:
    """
    A helper class for getting the current geographical location.
    Uses the geocoder library to determine the current latitude and longitude.
    """
    
    @staticmethod
    def get_current_location() -> Optional[Dict[str, float]]:
        """
        Get the current latitude and longitude.
        
        Returns:
            Optional[Dict[str, float]]: A dictionary with 'lat' and 'lng' keys if successful,
                                      None if the location could not be determined.
        """
        try:
            # Get current location using IP address
            g = geocoder.ip('me')
            
            if g.ok:
                return {
                    'lat': g.lat,
                    'lng': g.lng,
                    'address': g.address
                }
            else:
                logging.error(f"Failed to get location: {g.error}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting location: {str(e)}")
            return None
    
    @classmethod
    def get_lat_lng(cls) -> Optional[Tuple[float, float]]:
        """
        Get the current latitude and longitude as a tuple.
        
        Returns:
            Optional[Tuple[float, float]]: A tuple of (latitude, longitude) if successful,
                                         None if the location could not be determined.
        """
        location = cls.get_current_location()
        if location:
            return (location['lat'], location['lng'])
        return None

    @classmethod
    def get_formatted_location(cls) -> str:
        """
        Get a formatted string of the current location.
        
        Returns:
            str: A formatted string with the location information,
                 or an error message if the location could not be determined.
        """
        location = cls.get_current_location()
        if location:
            return f"Latitude: {location['lat']}, Longitude: {location['lng']}, Address: {location.get('address', 'N/A')}"
        return "Unable to determine current location."


if __name__ == "__main__":
    print(Location.get_formatted_location())