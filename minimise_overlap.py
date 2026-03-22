import pandas as pd
import pulp
from itertools import permutations

# === Load data ===
df = pd.read_csv("breadths.csv")

# === Map animal names to short codes ===
name_map = {
    'dragon': 'D',
    'tiger': 'T',
    'lion': 'L',
    'garuda': 'G',
}

arrow = {
    "up": "\u2191",
    "down": "\u2193"
}

# === Build b[i, j] dictionary with full orientation info ===
b = {}
for _, row in df.iterrows():
    animal = name_map[row['animal'].strip().lower()]
    orientation = row['orientation'].strip().lower()  # 'up' or 'down'
    b[(animal, orientation)] = float(row['value'])

# === Static data ===
TOYS = ['D', 'T', 'L', 'G']
ORIENTATIONS = ['up', 'down']
POSITIONS = list(range(len(TOYS)))
M = 100

# === Model ===
model = pulp.LpProblem("FourStrongest", pulp.LpMinimize) # Min

# x[i,k]: is toy i in position k?
x = pulp.LpVariable.dicts("x", [(i, k) for i in TOYS for k in POSITIONS], cat='Binary')

# j_i[i,j]: is toy i in orientation j?
j_i = pulp.LpVariable.dicts("j", [(i, j) for i in TOYS for j in ORIENTATIONS], cat='Binary')

# s[i]: starting position of toy i
s = pulp.LpVariable.dicts("s", TOYS, lowBound=0)

# delta[i,i2]: overlap penalty
delta = pulp.LpVariable.dicts("delta", [(i, i2) for (i, i2) in permutations(TOYS, 2)], lowBound=0)

# === Constraints ===

# 1. Each toy must appear in one position
for i in TOYS:
    model += pulp.lpSum(x[i, k] for k in POSITIONS) == 1

# 2. Each position must be occupied by exactly one toy
for k in POSITIONS:
    model += pulp.lpSum(x[i, k] for i in TOYS) == 1

# 3. Each toy has exactly one orientation
for i in TOYS:
    model += pulp.lpSum(j_i[i, j] for j in ORIENTATIONS) == 1

# 4. Overlap constraints based on orientation-dependent lengths
for i, i2 in permutations(TOYS, 2):
    for k in POSITIONS[:-1]:  # positions 0, 1, 2
        model += (
            s[i] + pulp.lpSum(b[(i, j)] * j_i[i, j] for j in ORIENTATIONS)
            <= s[i2] + delta[i, i2] + M * (2 - x[i, k] - x[i2, k + 1])
        )

# === Objective Function ===
model += pulp.lpSum(delta[i, i2] for (i, i2) in permutations(TOYS, 2))

# === Solve ===
solver = pulp.PULP_CBC_CMD(msg=False)
model.solve(solver)

# === Output ===
print(f"Total overlap penalty: {pulp.value(model.objective)}cm")

# === Collect toy data by position ===
arrangement = {}

for i in TOYS:
    pos = [k for k in POSITIONS if pulp.value(x[i, k]) > 0.5][0]
    ori = [j for j in ORIENTATIONS if pulp.value(j_i[i, j]) > 0.5][0]
    arrangement[pos] = f"{i}{arrow[ori]}"

# === Print toys in order of position ===
ordered_output = " ".join(arrangement[k] for k in sorted(arrangement))
print(ordered_output)

# === Calculate total length ===
starts = {}
ends = {}

for i in TOYS:
    si = pulp.value(s[i])
    ori = [j for j in ORIENTATIONS if pulp.value(j_i[i, j]) > 0.5][0]
    length = b[(i, ori)]
    starts[i] = si
    ends[i] = si + length

total_length = max(ends.values()) - min(starts.values())
print(f"Total arrangement length: {total_length:.2f} cm")
