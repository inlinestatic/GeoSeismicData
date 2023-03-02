import threading
import obspy
import json
from obspy.clients.fdsn.header import URL_MAPPINGS
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
from time import sleep

# Set start and end times for the data
end_time = UTCDateTime.now()
start_time = end_time - 1

# Set the update interval
update_interval = 1  # seconds

# Define a function to retrieve seismic data for a provider
def get_seismic_data(provider):
    # Create a client object for the provider
    client = Client(provider)

    # Get the seismic data for the last 1 second using QuakeML
    events = client.get_events(starttime=start_time, endtime=end_time, minmagnitude=5)

    # Print the number of events retrieved from the provider
    print(f"{provider}: {len(events)} events retrieved")

    return events

# Define the GetSeismicData function
def GetSeismicData():
    # Initialize the events hashtable
    all_events = {}

    # Loop indefinitely to update seismic data at the specified interval
    while True:
        # Loop through each provider and create a thread for each one
        threads = []
        for provider in URL_MAPPINGS.keys():
            thread = threading.Thread(target=get_seismic_data, args=(provider,))
            threads.append(thread)

        # Start the threads
        for thread in threads:
            thread.start()

        # Wait for the threads to finish
        for thread in threads:
            thread.join()

        # Aggregate the events from all providers
        for thread in threads:
            events = thread.result()
            for event in events:
                # Extract the event properties and store them in a hashtable
                event_properties = {}
                event_properties['latitude'] = event.preferred_origin().latitude
                event_properties['longitude'] = event.preferred_origin().longitude
                event_properties['magnitude'] = event.preferred_magnitude().mag
                event_properties['amplitude'] = event.preferred_magnitude().amplitude
                event_properties['time'] = str(event.preferred_origin().time)
                event_properties['depth'] = event.preferred_origin().depth
                event_properties['color'] = get_color(event.preferred_magnitude().mag)

                # Store the event in the hashtable based on a hash of its properties
                key = hash(json.dumps(event_properties))
                all_events[key] = event_properties

        # Print the JSON array of event properties
        print(json.dumps(list(all_events.values())))

        # Wait for the next update interval
        sleep(update_interval)

    return all_events

# Define a function to generate an RGB color code based on an input value between 5 and 12
def get_color(value):
    # Define the minimum and maximum values for the color gradient
    min_value = 5
    max_value = 12

    # Calculate the normalized value between 0 and 1
    normalized_value = (value - min_value) / (max_value - min_value)

    # Calculate the RGB color code based on the normalized value
    red = int(255 * normalized_value)
    green = int(255 * (1 - normalized_value))
    blue = 0

    # Format the RGB color code as a string
    color_code = f"#{red:02x}{green:02x}{blue:02x}"

    return color_code

# Call the GetSeismicData function
if __name__ == "__main__":
    events = GetSeismicData()
