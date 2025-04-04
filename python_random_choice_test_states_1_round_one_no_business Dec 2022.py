import numpy as np
import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_data(
    locations_file: str, population_file: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load location and population data from Stata files.

    Args:
        locations_file: Path to the locations Stata file
        population_file: Path to the population Stata file

    Returns:
        tuple: (locations DataFrame, people_per_block DataFrame)
    """
    try:
        if not Path(locations_file).exists():
            raise FileNotFoundError(f"Locations file not found: {locations_file}")
        if not Path(population_file).exists():
            raise FileNotFoundError(f"Population file not found: {population_file}")

        locations = pd.read_stata(locations_file)
        people_per_block = pd.read_stata(population_file)

        # Validate required columns
        required_cols = {"block", "units", "location"}
        if not all(col in locations.columns for col in required_cols):
            raise ValueError(
                f"Locations file missing required columns: {required_cols}"
            )

        if (
            "block" not in people_per_block.columns
            or "pop2022" not in people_per_block.columns
        ):
            raise ValueError(
                "Population file missing required columns: 'block' and/or 'pop2022'"
            )

        return locations, people_per_block

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def prepare_locations(locations: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare location data by computing probabilities.

    Args:
        locations: DataFrame containing location information

    Returns:
        DataFrame with added probability calculations
    """
    try:
        # Compute total units per Census block
        locations["total_units"] = locations.groupby("block")["units"].transform("sum")

        # Validate no zero totals
        if (locations["total_units"] == 0).any():
            raise ValueError("Found Census blocks with zero total units")

        # Compute probability of being assigned to each location within a Census block
        locations["prob_location"] = locations["units"] / locations["total_units"]

        # Validate probabilities sum to 1 for each block
        prob_sums = locations.groupby("block")["prob_location"].sum()
        if not np.allclose(prob_sums, 1.0):
            logger.warning("Some block probabilities don't sum exactly to 1.0")

        return locations

    except Exception as e:
        logger.error(f"Error preparing locations: {str(e)}")
        raise


def create_people_df(people_per_block: pd.DataFrame) -> pd.DataFrame:
    """
    Create DataFrame with individual people entries.

    Args:
        people_per_block: DataFrame containing population counts per block

    Returns:
        DataFrame with individual entries for each person
    """
    try:
        # Validate population counts
        if (people_per_block["pop2022"] < 0).any():
            raise ValueError("Negative population counts found")

        people = pd.DataFrame(
            {
                "block": np.repeat(
                    people_per_block["block"].values,
                    people_per_block["pop2022"].values.astype(int),
                )
            }
        )

        return people

    except Exception as e:
        logger.error(f"Error creating people DataFrame: {str(e)}")
        raise


def assign_location(group: pd.DataFrame, locations: pd.DataFrame) -> pd.Series:
    """
    Assign locations to people within a Census block.

    Args:
        group: DataFrame group containing people in a block
        locations: DataFrame containing location information

    Returns:
        Series with assigned locations
    """
    try:
        block = group.name
        block_locations = locations[locations["block"] == block]

        if len(block_locations) == 0:
            raise ValueError(f"No locations found for block {block}")

        # Sample locations for people in this block based on probability
        assigned = np.random.choice(
            block_locations["location"],
            size=len(group),
            replace=True,
            p=block_locations["prob_location"],
        )

        return pd.Series(assigned, index=group.index)

    except Exception as e:
        logger.error(f"Error assigning locations for block {block}: {str(e)}")
        raise


def main():
    """Main execution function."""
    try:
        # File paths
        locations_file = "test dataset states 1 block_id location_id unit_count round one no business Dec 2022.dta"
        population_file = "test dataset states 1 round one no business Dec 2022.dta"
        output_file = "assigned_people_test_state_01_round1_no_business_Dec2022.csv"

        # Set random seed for reproducibility
        np.random.seed(12345)

        # Load and prepare data
        logger.info("Loading data...")
        locations, people_per_block = load_data(locations_file, population_file)

        logger.info("Preparing location probabilities...")
        locations = prepare_locations(locations)

        logger.info("Creating people DataFrame...")
        people = create_people_df(people_per_block)

        logger.info("Assigning locations...")
        people["assigned_location"] = people.groupby("block", group_keys=False).apply(
            lambda x: assign_location(x, locations)
        )

        # Add assignment timestamp
        people["assignment_timestamp"] = pd.Timestamp.now()

        logger.info(f"Saving results to {output_file}...")
        people.to_csv(output_file, index=False)
        logger.info("Assignment complete!")

        # Print summary statistics
        print("\nAssignment Summary:")
        print(f"Total people assigned: {len(people):,}")
        print(f"Number of blocks: {people['block'].nunique():,}")
        print(
            f"Number of unique locations used: {people['assigned_location'].nunique():,}"
        )

    except Exception as e:
        logger.error(f"Program failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
