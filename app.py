import os
import json
import random
from datetime import datetime, timedelta
import numpy as np
from from_root import from_root
import sys

from logger import logging
from exception import FlightException

print("Script Started")

N = 5000
M = (50,100)
K = (100,200)
L= (0.005,0.001)

cities = [i for i in range(random.randint(K[0], K[1]))]
output_dir = "tmp/flights"

os.makedirs(output_dir, exist_ok=True)

def generation():
    logging.info("Generation started")
    for i in range(N):
        flights_data = []
        timestamp = datetime.now().strftime("%d-%m-%y-%H-%M-%S")
        origin_city = random.choice(cities)
        num_flights = random.randint(M[0], M[1])
        na_prob = random.uniform(L[0], L[1])
        for _ in range(num_flights):
            flight = {
                "date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
                "origin_city": random.choice(cities),
                "destination_city": random.choice(cities),
                "flight_duration_secs": random.randint(3600 , 72000),  
                "passengers_on_board": random.randint(1, 100)
            }
            if random.random() < na_prob:
                flight[random.choice(list(flight.keys()))] = None
            flights_data.append(flight)

        
        file_path = os.path.join(from_root(), "tmp", "flights", f"{timestamp}-city_{origin_city}-flights.json")
        with open(file_path, 'w') as f:
            json.dump(flights_data, f)
    logging.info(f"Created {N} Json files randomly with random Data")

def analyze_files():
    logging.info("Analysis Phase Started")
    start_time = datetime.now()
    total_records = 0
    dirty_records = 0
    flight_durations = []
    destination_counts = {}
    passengers_arrived = {}
    passengers_left = {}

    for filename in os.listdir(output_dir):
        file_path = os.path.join(from_root(), output_dir.split("/")[0], output_dir.split("/")[1], filename)
        with open(file_path, 'r') as f:
            flights = json.load(f)

        for flight in flights:
            total_records += 1
            if [v for v in flight.values() if v is None]:
                dirty_records += 1
            else:
                flight_durations.append(flight['flight_duration_secs'])
                dest_city = flight['destination_city']
                destination_counts[dest_city] = destination_counts.get(dest_city, 0) + 1
                passengers_arrived[dest_city] = passengers_arrived.get(dest_city, 0) + flight['passengers_on_board']
                origin_city = flight['origin_city']
                passengers_left[origin_city] = passengers_left.get(origin_city, 0) + flight['passengers_on_board']

    # Calculate statistics
    Avg_time = np.mean(flight_durations)
    P95_percentile = np.percentile(flight_durations, 95)
    Top_dest = sorted(destination_counts, key=destination_counts.get, reverse=True)[:25]
    max_arrived = max(passengers_arrived, key=passengers_arrived.get)
    max_left = max(passengers_left, key=passengers_left.get)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    output = {
        "Total records processed": total_records,
        "Total dirty records": dirty_records,
        "Total run duration": duration,
        "AVG duration": Avg_time,
        "P95 ": P95_percentile,
        "Top 25 destination cities": Top_dest,
        "Max Arrived City": max_arrived,
        "Max left city": max_left
    }

    logging.info(f"Output: {output}")

    with open("output.json", "w") as outputfile:
        json.dump(output, outputfile, indent=4)
    logging.info("Output values are stored in output.json file.")


if __name__ == "__main__":
    try:
        generation()
        logging.info("Generate Phase completed")
        analyze_files()
        logging.info("Analysis Phase completed")
        print("Script Completed Successfully.")
    except Exception as e:
        raise FlightException(e,sys)
