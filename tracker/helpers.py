"""Load data into DataFrames, group by month/week, calculate totals and wilks"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine


def calculate_1RM(weight: float, reps: int) -> float:
    """
    Calculate one repetition maximum
    """
    return weight * 1.03 ** (reps - 1)


def calculate_wilks(t: float, bw: float, sex: str, units: str) -> float:
    """
    Calculates wilks coefficient based on sex and bodyweight
    """

    # adjust for sex
    if sex == "F":
        a = 594.31747775582
        b = -27.23842536447
        c = 0.82112226871
        d = -0.00930733913
        e = 0.00004731582
        f = -0.00000009054
    else:
        a = -216.0475144
        b = 16.2606339
        c = -0.002388645
        d = -0.00113732
        e = 0.00000701863
        f = -0.00000001291

    # adjust for units
    if units == "lb":
        t = t / 2.20462
        bw = bw / 2.20462

    return (
        t * 500 / (a + b * bw + c * bw ** 2 + d * bw ** 3 + e * bw ** 4 + f * bw ** 5)
    )


def calculate_total(s: pd.DataFrame, b: pd.DataFrame, d: pd.DataFrame) -> pd.DataFrame:
    """
    Sums squat, bench, and deadlift one-rep maximums

    's' 'b' 'd' are the DataFrames created by get_maxes()
    """
    temp = s["1RM"] + b["1RM"] + d["1RM"]

    total = temp.to_frame()
    total.rename(columns={"1RM": "Total"}, inplace=True)
    total.name = "Total"
    return total


def load_lifts_csv(csv_file: str) -> pd.DataFrame:
    """
    Load lifts .csv file to a DataFrame
    """
    # fields: date, exercise, category, weight, reps
    df = pd.read_csv(csv_file)

    # drop useless columns, change column types, etc.
    df = df.drop("Distance", 1)
    df = df.drop("Distance Unit", 1)
    df = df.drop("Time", 1)
    df["Date"] = pd.to_datetime(df["Date"])
    # df["Comment"] = df["Comment"].astype("object")
    df = df.drop("Comment", 1)

    # create 1RM column
    df["1RM"] = df["Weight (lbs)"] * 1.03 ** (df["Reps"] - 1)

    df = df.rename(
        columns={
            "Weight (lbs)": "weight",
            "Date": "date",
            "Exercise": "exercise",
            "Category": "category",
            "Weight": "weight",
            "Reps": "reps",
            "1RM": "orm",
        }
    )

    return df


def load_lifts_sql(sql_db_file: str):
    """
    Loads lifts from SQL database to a DataFrame
    """
    engine = create_engine(f"sqlite:///{sql_db_file}", echo=True)

    df = pd.read_sql_table("lifts", engine)
    return df


def load_weight_csv(csv_file: str) -> pd.DataFrame:
    """
    Load lifts .csv file to a DateFrame
    """
    # fields: date, measurement, value, unit
    df = pd.read_csv(csv_file)

    # drop useless columns, drop non-bodyweight-related rows
    df = df.drop("Comment", 1)
    df = df.drop("Time", 1)
    df = df.drop(df[df["Measurement"] != "Bodyweight"].index)
    df["Date"] = pd.to_datetime(df["Date"])

    return df


def get_maxes(df: pd.DataFrame, exercise: str, frequency="W") -> pd.DataFrame:
    """
    Get maximum one repetition (1RM) weight for a particular exercise or maximum bodyweight within a specific time interval
    """
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    # W (weekly), M (monthly), SM (semi-monthly)
    if exercise == "Bodyweight":
        grouped_df = df[["Date", "Value"]].groupby(
            pd.Grouper(key="Date", freq=frequency)
        )
    else:
        # filter for exercise, get max 1RM for each day
        df2 = df[df["Exercise"] == exercise]
        grouped_df = df2[["Date", "1RM"]].groupby(
            pd.Grouper(key="Date", freq=frequency)
        )
    max_df = grouped_df.max().ffill()
    max_df.name = exercise
    return max_df


def get_category(exercise: str) -> str:
    """
    Returns category of exercise
    """
    exercise_categories = {
        "Hanging Leg Raise": "Abs",
        "Barbell Squat": "Legs",
        "Deadlift": "Back",
        "Flat Barbell Bench Press": "Chest",
    }
    return exercise_categories.get(exercise, "Category not found")


def add_exercise(df: pd.DataFrame, new_ex: dict) -> pd.DataFrame:
    """
    Add exercise to DataFrame

    df = add_exercise(
        df, {"Date": "2019-09-01", "Exercise": "Deadlift", "Weight (lbs)": 550, "Reps": 1}
    """
    # populate dictionary with default values if necessary
    new_ex.setdefault("Category", get_category(new_ex["Exercise"]))
    # new_ex.setdefault("Comment", np.nan)
    new_ex.setdefault("1RM", calculate_1RM(new_ex["Weight (lbs)"], new_ex["Reps"]))

    # wrap dictionary values in list to allow for single row DF creation
    new_df = pd.DataFrame({k: [v] for k, v in new_ex.items()})

    # change dtype to datetime
    new_df["Date"] = pd.to_datetime(new_df["Date"])

    return df.append(new_df, ignore_index=True, sort=False)


def remove_exercise(df: pd.DataFrame, removed_exercise):
    """
    Remove exercise from DataFrame
    """
    _a = 1
    return None
