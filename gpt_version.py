import numpy as np
import pandas as pd


def load_data(file_path):
    """Load CSV or Stata file into a Pandas DataFrame."""
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".dta"):
        df = pd.read_stata(file_path)
    else:
        raise ValueError(
            "Unsupported file format. Please provide a CSV or Stata (.dta) file."
        )
    print(df)
    # required_cols = {"block_id", "bsl_id", "unit_count", "block_population"}
    required_cols = {"block_id", "unit_count"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"File is missing required columns: {required_cols - set(df.columns)}"
        )
    return df


def allocate_population_blockwise(df):
    """
    Allocate population to BSLs block-by-block using vectorized operations.

    Args:
        df (pd.DataFrame): Input DataFrame with columns:
            - block_id
            - bsl_id
            - unit_count
            - block_population

    Returns:
        pd.DataFrame: DataFrame with allocated population per BSL.
    """
    allocation_results = []

    for block_id, group in df.groupby("block_id"):
        block_population = group["block_population"].iloc[0]
        if block_population == 0 or group["unit_count"].sum() == 0:
            # Skip empty blocks or return 0s
            for _, row in group.iterrows():
                allocation_results.append({**row, "allocated_population": 0})
            continue

        # Create weighted BSL list based on unit_count
        bsl_unit_expansion = np.repeat(
            group["bsl_id"].values, group["unit_count"].values
        )

        # Randomly assign each person to a BSL via unit
        assigned_bsl_ids = np.random.choice(bsl_unit_expansion, size=block_population)

        # Count how many people got assigned to each BSL
        bsl_pop_counts = pd.Series(assigned_bsl_ids).value_counts()

        for _, row in group.iterrows():
            bsl_id = row["bsl_id"]
            allocated_pop = bsl_pop_counts.get(bsl_id, 0)
            allocation_results.append({**row, "allocated_population": allocated_pop})

    return pd.DataFrame(allocation_results)


def main(csv_path, output_path):
    df = load_data(csv_path)
    result_df = allocate_population_blockwise(df)
    result_df.to_csv(output_path, index=False)
    print(f"✅ Population allocation complete. Output saved to {output_path}")


if __name__ == "__main__":
    csv_path = (
        "data/test dataset state 56 block_id location_id unit_count round one.dta"
    )
    output_path = "output/allocated_output_56.csv"
    main(csv_path, output_path)
