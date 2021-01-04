""" Streamlit app with multiple views capable of CRUD and analysis of lifting data """
import pandas as pd
import streamlit as st
from helpers import (  # pylint: disable-msg=E0611
    calculate_1RM,
    load_weight_csv,
    load_lifts_csv,
    load_lifts_sql,
    get_maxes,
    calculate_total,
    calculate_wilks,
    get_category,
    add_exercise,
    plot_lift_vs_time,
)
from database import add_data, start_db, Lift, User


def main():
    """A Simple CRUD Blog App"""
    html_temp = """
		<div style="background-color:{};padding:10px;border-radius:10px">
		<h1 style="color:{};text-align:center;">Lifting Tracker</h1>
		</div>
		"""
    st.markdown(html_temp.format("royalblue", "white"), unsafe_allow_html=True)

    # menu sidebar
    menu = ["Home", "Add Workout", "View Lifts", "View Progress"]
    choice = st.sidebar.selectbox("Menu", menu)

    # initialize SQL database
    engine, session = start_db(r"C:\Development\lifting-tracker\lift_tracker.db")

    if choice == "Home":
        st.subheader("Home")
        result = session.query(Lift).all()
        st.write(len(result))

    elif choice == "Add Workout":
        st.subheader("Add Workout")
        exercise = st.text_input("Exercise")
        category = st.selectbox(
            "Category",
            [
                "Shoulders",
                "Back",
                "Chest",
                "Biceps",
                "Legs",
                "Triceps",
                "Cardio",
                "Abs",
                "Grip",
            ],
        )
        weight = st.number_input(
            "Weight (lbs)", min_value=0, max_value=1000, value=0, step=5
        )
        reps = st.number_input("Reps", min_value=0, max_value=99, value=1, step=1)
        orm = calculate_1RM(weight, reps)
        date = st.date_input("Date")
        if st.button("Add Exercise"):
            add_data(session, exercise, category, weight, reps, orm, date)
            st.write("Added")

    elif choice == "View Lifts":
        st.subheader("View Lifts")
        cutoff = st.slider("Weight", min_value=0, max_value=1000, value=500, step=5)
        df = pd.read_sql(
            session.query(Lift).filter(Lift.orm > cutoff).statement, session.bind
        )
        df["date"] = pd.to_datetime(df["date"])

        displayed_lifts = st.multiselect(
            "Lifts to display",
            df["exercise"].unique().tolist(),
            default=df["exercise"].unique().tolist(),
        )

        st.dataframe(df[df["exercise"].isin(displayed_lifts)])

    elif choice == "View Progress":
        st.subheader("View Progress")

        df = pd.read_sql(session.query(Lift).statement, session.bind)
        df["date"] = pd.to_datetime(df["date"])
        dfw = load_weight_csv(
            r"C:\Users\andre\Downloads\FitNotes_BodyTracker_Export_2019_12_28_14_11_27.csv"
        )

        # calculate 1RM maxes for each exercise for each month
        s = get_maxes(df, "Barbell Squat", "M")
        b = get_maxes(df, "Flat Barbell Bench Press", "M")
        d = get_maxes(df, "Deadlift", "M")
        w = get_maxes(dfw, "Bodyweight", "M")

        # plot squat/bench/deadlift/weight in Bokeh plot
        sbd_plot = plot_lift_vs_time(s, b, d, w)
        st.bokeh_chart(sbd_plot)

        # calculate totals for each month and wilks based upon totals
        total = calculate_total(s, b, d)
        wilks = pd.DataFrame()
        wilks["Wilks"] = calculate_wilks(total["Total"], 220, "M", "lb")
        wilks.name = "Wilks"

        # plot total/weight/wilks in Bokeh plot
        t_plot = plot_lift_vs_time(total, w, wilks)
        st.bokeh_chart(t_plot)


if __name__ == "__main__":
    main()
