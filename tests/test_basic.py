import pytest
import pandas as pd
from pandas._testing import assert_frame_equal
from .context import lifting_tracker


@pytest.fixture(scope="session")
def csv_lift_file(tmpdir_factory):
    lifts = [
        ["12/26/2015", "Barbell Squat", "Legs", "225", "2", "", "", "", ""],
    ]
    cols = [
        "Date",
        "Exercise",
        "Category",
        "Weight (lbs)",
        "Reps",
        "Distance",
        "Distance Unit",
        "Time",
        "Comment",
    ]
    dataframe = pd.DataFrame(lifts, columns=cols)
    filename = str(tmpdir_factory.mktemp("data").join("data.csv"))
    dataframe.to_csv(filename, index=False)
    return filename


@pytest.fixture(scope="session")
def csv_weight_file(tmpdir_factory):
    lifts = [
        ["9/1/2015", "7:56:05 PM", "Bodyweight", "155", "lbs", ""],
    ]
    cols = [
        "Date",
        "Time",
        "Measurement",
        "Value",
        "Unit",
        "Comment",
    ]
    dataframe = pd.DataFrame(lifts, columns=cols)
    filename = str(tmpdir_factory.mktemp("data").join("data.csv"))
    dataframe.to_csv(filename, index=False)
    return filename


@pytest.fixture(scope="module")
def df_lifts():
    df = pd.DataFrame(
        data=[["2015-12-26", "Barbell Squat", "Legs", 225, 2, 231.75],],
        columns=["Date", "Exercise", "Category", "Weight (lbs)", "Reps", "1RM",],
    )

    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture(scope="module")
def df_bodyweights():
    df = pd.DataFrame(
        data=[["9/1/2015", "Bodyweight", 155, "lbs"],],
        columns=["Date", "Measurement", "Value", "Unit",],
    )

    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture(scope="module")
def df_added_exercise():
    df = pd.DataFrame(
        data=[
            ["2015-12-26", "Barbell Squat", "Legs", 225, 2, 231.75],
            ["2019-09-01", "Flat Barbell Bench Press", "Chest", 330, 1, 330.0],
        ],
        columns=["Date", "Exercise", "Category", "Weight (lbs)", "Reps", "1RM",],
    )

    df["Date"] = pd.to_datetime(df["Date"])
    return df


@pytest.fixture(scope="module")
def df_maxlifts():
    max_df = pd.DataFrame(data=[["2015-12-31", "231.75"]], columns=["Date", "1RM"])
    max_df = max_df.set_index("Date")
    max_df["1RM"] = max_df["1RM"].astype("float64")
    return max_df


@pytest.fixture(scope="module")
def df_totals():
    tot_df = pd.DataFrame(data=[["2015-12-31", "695.25"]], columns=["Date", "Total"])
    tot_df = tot_df.set_index("Date")
    tot_df["Total"] = tot_df["Total"].astype("float64")
    return tot_df


@pytest.mark.parametrize("weight,reps,expected", [(100, 2, 103), (100, 8, 122.9)])
def test_1RM_calculator(weight, reps, expected):
    assert lifting_tracker.helpers.calculate_1RM(weight, reps) == pytest.approx(
        expected, 0.1
    )


@pytest.mark.parametrize(
    "total,weight,sex,units,expected",
    [(1000, 200, "M", "lb", 288.4), (454, 70, "F", "kg", 451.6)],
)
def test_calculate_wilks(total, weight, sex, units, expected):
    assert lifting_tracker.helpers.calculate_wilks(
        total, weight, sex, units
    ) == pytest.approx(expected, 0.1)


@pytest.mark.parametrize(
    "test_input,expected", [("Beans", "Category not found"), ("Deadlift", "Back")]
)
def test_get_category(test_input, expected):
    assert lifting_tracker.helpers.get_category(test_input) == expected


def test_load_lifts_csv(csv_lift_file, df_lifts):

    assert_frame_equal(
        lifting_tracker.helpers.load_lifts_csv(csv_lift_file),
        df_lifts,
        check_like=True,
    )


def test_get_maxes(df_lifts, df_maxlifts):
    assert_frame_equal(
        lifting_tracker.helpers.get_maxes(df_lifts, "Barbell Squat", "M"),
        df_maxlifts,
        check_like=True,
    )


def test_calculate_total(df_maxlifts, df_totals):
    assert_frame_equal(
        lifting_tracker.helpers.calculate_total(df_maxlifts, df_maxlifts, df_maxlifts),
        df_totals,
        check_like=True,
    )


def test_load_weight_csv(csv_weight_file, df_bodyweights):

    assert_frame_equal(
        lifting_tracker.helpers.load_weight_csv(csv_weight_file),
        df_bodyweights,
        check_like=True,
    )


def test_add_exercise(df_lifts, df_added_exercise):
    assert_frame_equal(
        lifting_tracker.helpers.add_exercise(
            df_lifts,
            {
                "Date": "2019-09-01",
                "Exercise": "Flat Barbell Bench Press",
                "Weight (lbs)": 330,
                "Reps": 1,
            },
        ),
        df_added_exercise,
        check_like=True,
    )


def test_remove_exercise():
    # TODO
    assert 1 == 1
