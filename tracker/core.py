"""Plot lifts over time"""

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
    )

import pandas as pd
import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Category10  # pylint: disable-msg=E0611


def plot_lift_vs_time(*args: pd.DataFrame):
    """
    Plot an arbitrary number of lifts on an HTML line chart
    """
    # output to static HTML file
    output_file("max_lifts.html")

    # create a new plot with a title and axis labels
    # https://bokeh.pydata.org/en/latest/docs/reference/models/layouts.html#bokeh.models.layouts.LayoutDOM.sizing_mode
    p = figure(
        title="One Rep Maxes vs. Time",
        x_axis_label="Time",
        y_axis_label="Max 1RM (lb)",
        x_axis_type="datetime",
        sizing_mode="stretch_width",
        plot_height=400,
    )

    # split data into x(date) and y(weight), then plot
    for i, lift in enumerate(args):
        x = lift.index
        y = lift[lift.columns[0]]

        p.line(
            x=x, y=y, line_width=2, line_color=Category10[6][i], legend_label=lift.name
        )

    # show the results
    # show(p)

    return p


# With debug=True, Flask server will auto-reload
# when there are code changes
if __name__ == "__main__":
    plots = []

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
    script, div = components(sbd_plot)
    plots.append({"script": script, "div": div})

    # calculate totals for each month and wilks based upon totals
    total = calculate_total(s, b, d)
    wilks = pd.DataFrame()
    wilks["Wilks"] = calculate_wilks(total["Total"], 220, "M", "lb")
    wilks.name = "Wilks"

    # plot total/weight/wilks in Bokeh plot
    t_plot = plot_lift_vs_time(total, w, wilks)

    # Embed plot into HTML via Flask Render
    # script, div = components(t_plot)
    # plots.append({"script": script, "div": div})

    output_file("lifts.html", title="Lifting Tracker")
    print("here")
    show(t_plot)
