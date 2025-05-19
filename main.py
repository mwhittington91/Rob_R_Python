import polars as pl
import pandas as pd

def clean_broadband_data_csv(csv_path: str) -> pl.LazyFrame:
    return (
        pl.read_csv(csv_path).lazy()
        .with_columns([
            pl.col("unit_count").cast(pl.Int64),
            pl.col("population").cast(pl.Int64),
            pl.col("max_advertised_download_speed").cast(pl.Float64),
            pl.col("max_advertised_upload_speed").cast(pl.Float64),
        ])
        .filter(
            (pl.col("business_type") != "B") &
            (pl.col("max_advertised_download_speed") >= 100) &
            (pl.col("max_advertised_upload_speed") >= 20) &
            (pl.col("unit_count") > 0) &
            (pl.col("population") > 0)
        )
        .unique(subset=["location_id", "provider_id"])
    )

def clean_broadband_data_stata(stata_path: str) -> pl.LazyFrame:
    df = pd.read_stata(stata_path)
    pl_df = pl.from_pandas(df)
    return (
        pl_df.lazy()
        .with_columns([
            pl.col("unit_count").cast(pl.Int64),
            pl.col("population").cast(pl.Int64),
            pl.col("max_advertised_download_speed").cast(pl.Float64),
            pl.col("max_advertised_upload_speed").cast(pl.Float64),
        ])
        .filter(
            (pl.col("business_type") != "B") &
            (pl.col("max_advertised_download_speed") >= 100) &
            (pl.col("max_advertised_upload_speed") >= 20) &
            (pl.col("unit_count") > 0) &
            (pl.col("population") > 0)
        )
        .unique(subset=["location_id", "provider_id"])
    )

def load_data(path:str) -> pl.DataFrame:
    if path.endswith('.csv'):
        return pl.read_csv(path)     
    elif path.endswith('.dta'):
        return pl.from_pandas(pd.read_stata(path))
    
def merge_dataframes(df1: pl.DataFrame, df2: pl.DataFrame) -> pl.DataFrame:
    return df1.join(df2, on=["location_id"], how="inner")


if __name__ == "__main__":
    stata_path = "data/BDC Update 07.12.23 AL Dec 2022.dta"
    sv_path = "ddata/FCC_Active_NoBSL_12312024_rel_6_test.csv"
    
    stata_df = load_data(stata_path)
    
    