import ntplib
from time import ctime, time, sleep
import datetime
import sys

# Function to get current time from NTP server
def get_ntp_time(server):
    client = ntplib.NTPClient()
    try:
        response = client.request(server, version=3)
        ntp_time = datetime.datetime.utcfromtimestamp(response.tx_time)
        return ntp_time
    except Exception as e:
        print(f"Failed to get NTP time: {e}")
        sys.exit(1)

# Function to get local time
def get_local_time():
    local_time = datetime.datetime.utcnow()
    return local_time

# Main function to calculate the time difference
def calculate_time_difference(server):
    ntp_time = get_ntp_time(server)
    local_time = get_local_time()
    print(f"The local time is {local_time}")
    print(f"The ntp time is {ntp_time}")
    # Calculating the difference
    difference = ntp_time - local_time
    return difference

if __name__ == "__main__":
    ntp_server = "pool.ntp.org"  # You can change this to your central NTP server
    difference = calculate_time_difference(ntp_server)
    print(f"Time difference between local and NTP server ({ntp_server}): {difference}")

