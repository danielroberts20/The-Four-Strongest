import pulp
import pandas as pd

# Load the data
breadths = pd.read_csv('breadths.csv', index_col=[0,1])
distances = pd.read_csv('distances.csv', index_col=[0,1,2,3])

# Define sets
animals = ['dragon', 'tiger', 'lion', 'garuda']
orientations = ['up', 'down']
positions = ['k1', 'k2', 'k3', 'k4']

# Create model
model = pulp.LpProblem("Four_Strongest", pulp.LpMinimize)

# Define variables
x = pulp.LpVariable.dicts('x', (animals, orientations, positions), cat='Binary')
y = pulp.LpVariable.dicts('y', (animals, orientations, positions, animals, orientations, positions), lowBound=0, cat='Continuous')

# Objective function
model += (
    pulp.lpSum(
        distances.loc[(i,j,ii,jj),'value'] * y[i][j][k][ii][jj][positions[positions.index(k)+1]]
        for i in animals for j in orientations
        for ii in animals for jj in orientations
        for k in positions[:-1] if i != ii
    )
    -
    pulp.lpSum(
        breadths.loc[(i,j),'value'] * x[i][j][k]
        for i in animals for j in orientations
        for k in positions[1:-1]  # Positions 2 and 3
    )
)

# Constraints
# 1. Exactly one piece at each position
for k in positions:
    model += pulp.lpSum(x[i][j][k] for i in animals for j in orientations) == 1

# 2. Each animal placed exactly once
for i in animals:
    model += pulp.lpSum(x[i][j][k] for j in orientations for k in positions) == 1

# 3. Linearization (McCormick constraints)
for i in animals:
    for j in orientations:
        for ii in animals:
            for jj in orientations:
                for k in positions[:-1]:
                    if i != ii:
                        next_k = positions[positions.index(k)+1]
                        model += y[i][j][k][ii][jj][next_k] <= x[i][j][k]
                        model += y[i][j][k][ii][jj][next_k] <= x[ii][jj][next_k]
                        model += y[i][j][k][ii][jj][next_k] >= x[i][j][k] + x[ii][jj][next_k] - 1

# Solve
model.solve()

# Output solution
for i in animals:
    for j in orientations:
        for k in positions:
            if pulp.value(x[i][j][k]) > 0.5:
                print(f"{i} {j} at {k}")

print("Objective value:", pulp.value(model.objective))
