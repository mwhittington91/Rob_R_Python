import numpy as np
import pandas as pd

locations=pd.read_stata('python test assign pop 2022 state 1 round two no business.dta')

# Ensure blockgroup and location are integers
locations['blockgroup'] = locations['blockgroup'].astype(int)
locations['location_id'] = locations['location_id'].astype(int)
locations['unit_count'] = locations['unit_count'].astype(int)
locations['unit_count_group'] = locations['unit_count_group'].astype(int)
locations['units_no_pop_sum_group'] = locations['units_no_pop_sum_group'].astype(int)
locations['pop_zero_unit_pos'] = locations['pop_zero_unit_pos'].astype(int)
locations['pop_unit_pos'] = locations['pop_unit_pos'].astype(int)

# Compute probability of being assigned to each location within a Census group
locations['prob1_location'] = np.where(
    locations['units_no_pop_sum_group'] == 0, 
    0,  # Set prob1_location to zero when units_no_pop_sum_group is zero
    locations['unit_count'] * ((locations['units_no_pop_sum_group'] + locations['unit_count_group']) /
                               (2 * locations['units_no_pop_sum_group'] * locations['unit_count_group']))
)

locations['prob2_location'] = np.where(
    locations['units_no_pop_sum_group'] == 0, 
    locations['unit_count'] / locations['unit_count_group'],  # Alternative formula
    locations['unit_count'] / (2 * locations['unit_count_group'])  # Original formula
)

# Compute final probability
locations['prob'] = (locations['pop_zero_unit_pos'] * locations['prob1_location']) + \
                    (locations['pop_unit_pos'] * locations['prob2_location'])


people_per_group=pd.read_stata('state 1 pop 2022 no units by group no business.dta')

people_per_group['blockgroup'] = people_per_group['blockgroup'].astype(int)
people_per_group['pop_no_units_sum_group'] = people_per_group['pop_no_units_sum_group'].astype(int)

people = pd.DataFrame({
    'blockgroup': np.repeat(people_per_group['blockgroup'].values, people_per_group['pop_no_units_sum_group'].values)
})
	
np.random.seed(12345)

def assign_location(group):
    blockgroup = group.name
    group_locations = locations[locations['blockgroup'] == blockgroup]
	
	  
    # Sample locations for people in this block based on probability
    assigned = np.random.choice(
        group_locations['location_id'], 
        size=len(group), 
        replace=True, 
        p=group_locations['prob']
    )
    
    return pd.Series(assigned, index=group.index)
		
	
# Apply the function per Census blockgroup
people['assigned_location'] = people.groupby('blockgroup', group_keys=False).apply(assign_location)

people.to_csv("assigned_people_state1_2022_round2_no_business.csv", index=False) 
