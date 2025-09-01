import json
import requests
import datetime

# --- Global Configuration for AXONS API ---
# Details from the "API GPS Guide V3.pdf"
AXONS_TEST_URL = "https://traceabilityoversea-api-nonprd.fit-cpgroup.com/sit/gps/location"
# IMPORTANT: Replace "XXXXXX" with the actual API key provided via email.
AXONS_API_KEY = "PRDDTy9Kw7jB04yK3kbgFVrA9WYAHZcvGsH9kjUy8hf"
# As specified in the documentation
COUNTRY_ID = "1"
VENDOR_ID = "1" # Example Vendor ID, adjust if a different one is provided


def send_gps_data_to_axons(location_data_list):
    """
    Sends GPS location data to the AXONS test server.

    Args:
        location_data_list (list): A list of dictionaries, where each dictionary
                                   represents a single location data point for a vehicle.

    Returns:
        dict: The JSON response from the server, or None if the request fails.
    """
    print(f"▶️  Preparing to send {len(location_data_list)} location(s) to AXONS test server...")
    print(f"   URL: {AXONS_TEST_URL}")

    # --- Construct the HTTP Headers ---
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "x-api-key": AXONS_API_KEY,
        "country_id": str(COUNTRY_ID) # Ensure country_id is a string
    }

    # --- Construct the Full Payload Body ---
    payload = {
        "vender_id": VENDOR_ID, # Note: PDF shows 'vender_id', not 'vendor_id'
        "location_count": len(location_data_list),
        "locations": location_data_list
    }

    # --- Convert payload to JSON string ---
    json_payload = json.dumps(payload, indent=2)
    print("\n--- Sending JSON Payload ---")
    print(json_payload)
    print("--------------------------\n")


    # --- Make the POST request ---
    try:
        # Check if the placeholder API key is still being used
        if AXONS_API_KEY == "PRDDTy9Kw7jB04yK3kbgFVrA9WYAHZcvGsH9kjUy8hf":
            print("⚠️  Warning: Using a placeholder API key. Please update 'AXONS_API_KEY' with your actual key.")

        response = requests.post(
            AXONS_TEST_URL,
            headers=headers,
            data=json_payload
        )
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        print("✅  GPS data sent successfully!")
        return response.json()

    except requests.exceptions.HTTPError as err:
        print(f"❌ HTTP Error while sending GPS data: {err}")
        # The server might return a JSON error message, so we try to print it
        try:
            print("   Server Response:", err.response.json())
        except json.JSONDecodeError:
            print("   Server Response (not JSON):", err.response.text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ A connection error occurred while sending GPS data: {e}")
        return None


# --- Main execution block to run the test ---
if __name__ == "__main__":
    # --- Sample GPS Location Data (Modify as needed) ---
    # This structure matches the "GPS Locations" object in the API guide.
    # Using a mix of data from your old script and the new API guide for a complete example.
    current_utc_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    vehicle_location_1 = {
        "driver_id": "0X00101XXX0X00", # Example from PDF
        "unit_id": "v1752287035", # Mapped from old "box_id"
        "seq": 120,
        "utc_ts": current_utc_time,
        "recv_utc_ts": current_utc_time,
        "lat": 13.7563,  # Example: Bangkok latitude
        "lon": 100.5018, # Example: Bangkok longitude
        "alt": 20,
        "speed": 95,
        "engine_status": 1, # 1 for On, 0 for Off
        "fix": 1,
        "license": "71-8697", # Mapped from old "vehicle_plate"
        "course": 102,
        "hdop": 2.0,
        "num_sats": 15,
        "gsm_cell": 54643,
        "gsm_loc": 123,
        "gsm_real": 2, # Assuming this is gsm_rssi from the old script
        "mileage": 915,
        "ext_power_status": 1,
        "ext_power": 12.6,
        "high_acc_count": 2,
        "high_de_acc_count": 0,
        "over_speed_count": 1,
        "max_speed": 95
    }

    # You can add more location objects to the list to send a batch
    locations_to_send = [vehicle_location_1]

    # Send the GPS data
    api_response = send_gps_data_to_axons(locations_to_send)

    print("\n--- API Server Response ---")
    if api_response:
        print(json.dumps(api_response, indent=2))
    else:
        print("Failed to get a valid response from the server.")