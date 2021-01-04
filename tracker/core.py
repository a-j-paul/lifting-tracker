"""Plot lifts over time"""
import pandas as pd
import numpy as np
from bokeh.plotting import show

# https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time
if __package__:
    # file being run as a module
    print("module")

    # from . import helpers
    from tracker.helpers import (  # pylint: disable-msg=E0611
        calculate_1RM,
        load_weight_csv,
        load_lifts_csv,
        get_maxes,
        calculate_total,
        calculate_wilks,
        get_category,
        add_exercise,
    )
else:
    # file is being run as a script
    print("script")

    from helpers import (  # pylint: disable-msg=E0611
        calculate_1RM,
        load_weight_csv,
        load_lifts_csv,
        get_maxes,
        calculate_total,
        calculate_wilks,
        get_category,
        add_exercise,
        plot_lift_vs_time,
    )


if __name__ == "__main__":

    # load data into DataFrames
    df = load_lifts_csv(
        r"C:\Users\andre\Downloads\FitNotes_Export_2019_12_28_14_11_12.csv"
    )

    dfw = load_weight_csv(
        r"C:\Users\andre\Downloads\FitNotes_BodyTracker_Export_2019_12_28_14_11_27.csv"
    )

    # exercise aliases
    squat = "Barbell Squat"
    bench = "Flat Barbell Bench Press"
    deadlift = "Deadlift"
    bw = "Bodyweight"

    # calculate 1RM maxes for each exercise for each month
    s = get_maxes(df, squat, "M")
    b = get_maxes(df, bench, "M")
    d = get_maxes(df, deadlift, "M")
    w = get_maxes(dfw, bw, "M")

    # plot squat/bench/deadlift/weight in Bokeh plot
    sbd_plot = plot_lift_vs_time(s, b, d, w)

    # calculate totals for each month and wilks based upon totals
    total = calculate_total(s, b, d)
    wilks = pd.DataFrame()
    wilks["Wilks"] = calculate_wilks(total["Total"], 220, "M", "lb")
    wilks.name = "Wilks"

    # plot total/weight/wilks in Bokeh plot
    t_plot = plot_lift_vs_time(total, w, wilks)
    show(t_plot)
