import json
import requests
from requests.auth import HTTPBasicAuth
import datetime
import time
import base64

# --- Global Configuration ---
# Credentials and vendor code from the provided details
USERNAME = "gpsiem"
PASSWORD = "eA5yEDt2"  # Corrected to uppercase 'J'
VENDOR_CODE = "108"
BASE_API_URL = "https://gateway.kubsave.com"


def register_new_device ( vehicle_data ) :
    """
    Sends a request to the DeviceRegister API to register a new vehicle.

    Args:
        vehicle_data (dict): A dictionary containing all the necessary data for registration.

    Returns:
        dict: The JSON response from the server, or None if the request fails.
    """
    api_url = f"{BASE_API_URL}/vendor/DeviceRegister"
    print ( f"▶️  Attempting to register device with box_id: {vehicle_data.get ( 'box_id' )}..." )
    print ( f"   URL: {api_url}" )

    try :
        response = requests.post (
            api_url ,
            auth = HTTPBasicAuth ( USERNAME , PASSWORD ) ,
            headers = {"Content-Type" : "application/json"} ,
            data = json.dumps ( vehicle_data )
        )
        response.raise_for_status ( )  # Raise an exception for bad status codes (4xx or 5xx)
        print ( "✅  Registration request sent successfully!" )
        return response.json ( )

    except requests.exceptions.HTTPError as err :
        print ( f"❌ HTTP Error during registration: {err}" )
        # The server might return a JSON error message, so we try to print it
        try :
            print ( "   Server Response:" , err.response.json ( ) )
        except json.JSONDecodeError :
            print ( "   Server Response (not JSON):" , err.response.text )
        return None
    except requests.exceptions.RequestException as e :
        print ( f"❌ A connection error occurred during registration: {e}" )
        return None


def send_gps_data ( box_id ) :
    """
    Sends a GPS location data update for a specific device.

    Args:
        box_id (str): The box_id of the device to send data for.

    Returns:
        dict: The JSON response from the server, or None if the request fails.
    """
    api_url = f"{BASE_API_URL}/vendor/SendLocation"
    print ( f"\n▶️  Sending GPS data for box_id: {box_id}..." )
    print ( f"   URL: {api_url}" )

    # --- Sample GPS Location Data (Modify as needed) ---
    location_payload = {
        "vendor_code" : VENDOR_CODE ,
        "locations_count" : 1 ,
        "locations" : [
            {
                "seq" : 1 ,
                "box_id" : box_id ,
                "utc_ts" : datetime.datetime.utcnow ( ).strftime ( "%Y-%m-%d %H:%M:%S" ) ,
                "recv_utc_ts" : datetime.datetime.utcnow ( ).strftime ( "%Y-%m-%d %H:%M:%S" ) ,
                "lat" : 13.7563 ,  # Example: Bangkok latitude
                "lon" : 100.5018 ,  # Example: Bangkok longitude
                "alt" : 20 ,
                "speed" : 75 ,
                "engine_status" : 1 ,
                "fix" : 0 ,
                "course" : 180 ,
                "hdop" : 0.8 ,
                "num_sats" : 15 ,
                "gsm_rssi" : 28 ,
                "mileage" : 915 ,  # Mileage updated since registration
                "ext_power" : 12.6 ,
                "driver_id" : ""
            }
        ]
    }

    try :
        response = requests.post (
            api_url ,
            auth = HTTPBasicAuth ( USERNAME , PASSWORD ) ,
            headers = {"Content-Type" : "application/json"} ,
            data = json.dumps ( location_payload )
        )
        response.raise_for_status ( )
        print ( "✅  GPS data sent successfully!" )
        return response.json ( )

    except requests.exceptions.HTTPError as err :
        print ( f"❌ HTTP Error while sending GPS data: {err}" )
        try :
            print ( "   Server Response:" , err.response.json ( ) )
        except json.JSONDecodeError :
            print ( "   Server Response (not JSON):" , err.response.text )
        return None
    except requests.exceptions.RequestException as e :
        print ( f"❌ A connection error occurred while sending GPS data: {e}" )
        return None


# --- Main execution block to run the test ---
if __name__ == "__main__" :
    # --- Print the encoded credentials ---
    credentials = f"{USERNAME}:{PASSWORD}"
    encoded_credentials = base64.b64encode ( credentials.encode ( 'ascii' ) ).decode ( 'ascii' )
    print ( f"🔑 Encoded Basic Auth Credentials: {encoded_credentials}\n" )

    # --- Vehicle Data for Registration (Modify as needed) ---
    # Using the data you provided in the previous step.
    vehicle_to_register = {
        "gps_vendor_code" : VENDOR_CODE ,
        "vehicle_plate" : "71-8697|สบ" ,
        "chassis_no" : "MNKFM2PK1XHX10616" ,
        "box_id" : "v1752287035" ,
        "gps_imei" : "867936074539716" ,
        "gps_phone" : "0975081030" ,
        "gps_have_mic" : "N" ,
        "carrier_name" : "IEM" ,
        "mileage" : 909 ,
        "speed_limit" : 90 ,
        "fuel_tank_size" : 70
    }

    # Step 1: Register the device
    registration_response = register_new_device ( vehicle_to_register )

    print ( "\n--- Registration Response ---" )
    if registration_response :
        print ( json.dumps ( registration_response , indent = 2 ) )
        # Check if registration was successful based on the API documentation's success code
        if str ( registration_response.get ( "code" ) ) == "1" :
            print ( "\nRegistration appears successful. Proceeding to send GPS data..." )
            time.sleep ( 2 )  # Pausing for 2 seconds before sending the next request

            # Step 2: Send GPS data for the newly registered device
            box_id_from_payload = vehicle_to_register.get ( "box_id" )
            location_response = send_gps_data ( box_id_from_payload )

            print ( "\n--- GPS Data Sending Response ---" )
            if location_response :
                print ( json.dumps ( location_response , indent = 2 ) )
            else :
                print ( "Failed to get a response for the location update." )
        else :
            print ( "\nRegistration was not successful. Skipping GPS data sending." )
    else :
        print ( "Registration failed. Cannot proceed to send GPS data." )