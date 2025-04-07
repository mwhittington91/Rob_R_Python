import numpy as np
import pandas as pd

locations=pd.read_stata('test dataset state 56 block_id location_id unit_count round one.dta')

# Compute total units per Census block
locations['total_units'] = locations.groupby('block')['units'].transform('sum')

# Compute probability of being assigned to each location within a Census block
locations['prob_location'] = locations['units'] / locations['total_units']

people_per_block=pd.read_stata('test dataset state 56 pop2022 round one.dta')

people = pd.DataFrame({
    'block': np.repeat(people_per_block['block'].values, people_per_block['pop2022'].values)
})

np.random.seed(12345)

def assign_location(group):
    block = group.name
    block_locations = locations[locations['block'] == block]


    # Sample locations for people in this block based on probability
    assigned = np.random.choice(
        block_locations['location'],
        size=len(group),
        replace=True,
        p=block_locations['prob_location']
    )

    return pd.Series(assigned, index=group.index)

# Apply the function per Census block
people['assigned_location'] = people.groupby('block', group_keys=False).apply(assign_location)

people.to_csv("assigned_people_test_state_01_round1_no_business_Dec2022.csv", index=False)
