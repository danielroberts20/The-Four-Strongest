import pandas as pd
import pulp
import itertools

# Load data from CSV
breadths = pd.read_csv("breadths.csv")

# Convert to dictionary: (animal, orientation) -> value
b = {
    (row['animal'].lower(), row['orientation'].lower()): row['value']
    for _, row in breadths.iterrows()
}

# Sets
animals = sorted(set([a.lower() for a in breadths['animal']]))
orientations = ['up', 'down']

# Parameters
L_max = 34.88  # max container length (cm)
M = 100        # big-M constant for ordering constraints

# Initialize model
model = pulp.LpProblem("Four_Strongest_Packing", pulp.LpMinimize)

# Decision variables
s = {i: pulp.LpVariable(f"s_{i}", lowBound=0, cat="Continuous") for i in animals}
o = {(i, j): pulp.LpVariable(f"o_{i}_{j}", cat="Binary") for i in animals for j in orientations}
z = {(i, i_): pulp.LpVariable(f"z_{i}_{i_}", cat="Binary") for i in animals for i_ in animals if i != i_}
L = pulp.LpVariable("L", lowBound=0, cat="Continuous")

# Objective
model += L

# Constraint 1: Each animal has exactly one orientation
for i in animals:
    model += o[(i, 'up')] + o[(i, 'down')] == 1

# Constraint 2: No overlap (using Big-M formulation)
for i, i_ in itertools.combinations(animals, 2):
    bi = b[(i, 'up')]*o[(i, 'up')] + b[(i, 'down')]*o[(i, 'down')]
    bi_ = b[(i_, 'up')]*o[(i_, 'up')] + b[(i_, 'down')]*o[(i_, 'down')]

    model += s[i] + bi <= s[i_] + M*(1 - z[(i, i_)])
    model += s[i_] + bi_ <= s[i] + M*z[(i, i_)]
    model += z[(i, i_)] + z[(i_, i)] == 1

# Constraint 3: Each animal must fit within the container
for i in animals:
    bi = b[(i, 'up')]*o[(i, 'up')] + b[(i, 'down')]*o[(i, 'down')]
    model += s[i] + bi <= L_max

# Constraint 4: Define objective value as the max right edge
for i in animals:
    bi = b[(i, 'up')]*o[(i, 'up')] + b[(i, 'down')]*o[(i, 'down')]
    model += s[i] + bi <= L

# Solve model
model.solve()

# Output
print("Model status:", pulp.LpStatus[model.status])
print("Minimum used length (cm):", round(pulp.value(L), 3))
print("\nAnimal placements:")

# Collect results into a list of tuples
results = []
for i in animals:
    start = pulp.value(s[i])
    ori = 'up' if pulp.value(o[(i, 'up')]) > 0.5 else 'down'
    results.append((start, i, ori))

# Sort by start position
results.sort()

# Print in order
print("\nAnimal placements (sorted by position):")
for start, i, ori in results:
    print(f"  {i.title():<7} | Start: {start:.2f} cm | Orientation: {ori}")
