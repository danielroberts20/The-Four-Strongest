import csv
from collections import defaultdict

# Initialize the measurements dictionary
measurements = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

ANIMALS = ["dragon", "tiger", "lion", "garuda"]
ORIENTATIONS = ["up", "down"]

# Function to populate the dictionary from the CSV file
def populate_measurements_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        # Iterate through the rows in the CSV
        for i, row in enumerate(csvreader):
            if i == 0:
                continue
            toy1, orientation1, toy2, orientation2, measurement = row

            # Convert the measurement to a float (assuming it's a numerical value)
            measurement = float(measurement)

            # Populate the dictionary with the measurement value
            measurements[toy1][orientation1][toy2][orientation2] = measurement

def get_measurement(toy1, dir1, toy2, dir2, csv_file='distances.csv'):
    animal_letters = [t[0] for t in ANIMALS]
    dir_letters = [d[0] for d in ORIENTATIONS]


    if toy1.lower() not in ANIMALS and toy1.lower() not in animal_letters:
        return
        #raise ValueError(
        #    f"Invalid toy '{toy1}'. Must be one of {{{", ".join(animal_letters)}}} or {{{", ".join(ANIMALS)}}}.")
    if toy2.lower() not in ANIMALS and toy2.lower() not in animal_letters:
        return
        #raise ValueError(
        #    f"Invalid toy '{toy2}'. Must be one of {{{", ".join(animal_letters)}}} or {{{", ".join(ANIMALS)}}}.")
    if dir1.lower() not in ORIENTATIONS and dir1.lower() not in dir_letters:
        return
        #raise ValueError(
        #    f"Invalid orientation '{dir1}'. Must be one of {{{", ".join(dir_letters)}}} or {{{", ".join(ORIENTATIONS)}}}.")
    if dir2.lower() not in ORIENTATIONS and dir2.lower() not in dir_letters:
        return
        #raise ValueError(
        #    f"Invalid orientation '{dir2}'. Must be one of {{{", ".join(dir_letters)}}} or {{{", ".join(ORIENTATIONS)}}}.")

    if len(measurements) == 0:
        populate_measurements_from_csv(csv_file)

    if toy1 not in ANIMALS:
        toy1 = ANIMALS[animal_letters.index(toy1.lower())]
    if toy2 not in ANIMALS:
        toy2 = ANIMALS[animal_letters.index(toy2.lower())]
    if dir1 not in ORIENTATIONS:
        dir1 = ORIENTATIONS[dir_letters.index(dir1.lower())]
    if dir2 not in ORIENTATIONS:
        dir2 = ORIENTATIONS[dir_letters.index(dir2.lower())]

    return measurements[toy1][dir1][toy2][dir2]

print(get_measurement("g", "d", "l", "d"))


