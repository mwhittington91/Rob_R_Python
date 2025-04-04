import random
from collections import defaultdict

def allocate_population_to_bsl(block_population, bsl_units_per_bsl):
    """
    Allocate block population to Broadband Serviceable Locations (BSLs).

    Args:
        block_population (int): Total number of people in the census block.
        bsl_units_per_bsl (dict): Dictionary of BSL ID to number of units in that BSL.
                                  Example: {"BSL1": 2, "BSL2": 1, "BSL3": 3} => total 6 units

    Returns:
        dict: Estimated population per BSL.
    """
    # Flatten unit list with BSL IDs for random assignment
    unit_to_bsl = []
    for bsl_id, unit_count in bsl_units_per_bsl.items():
        unit_to_bsl.extend([bsl_id] * unit_count)

    total_units = len(unit_to_bsl)
    if total_units == 0 or block_population == 0:
        return {bsl_id: 0 for bsl_id in bsl_units_per_bsl}

    # Initialize BSL population counter
    bsl_population = defaultdict(int)

    # Assign each person randomly to one unit, and thus to a BSL
    for _ in range(block_population):
        chosen_bsl = random.choice(unit_to_bsl)
        bsl_population[chosen_bsl] += 1

    return dict(bsl_population)