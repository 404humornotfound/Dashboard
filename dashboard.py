import streamlit as st
import streamlit as st
from datetime import *
from class_init import *
import plotly.express as px
from dashboardHelper import *


# initialize info class
info = Information()
info_df = info.dataframe

# initialize races
races = []
for i in range(len(info_df.index)):
    start_date = datetime.strptime(info_df['Registration start date'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(info.get_dataframe_by_gid(info_df['sheet gid'].iloc[i]), start_date, end_date, info_df['Name of race'].iloc[i]))
    

# print(races[0].to_frequency())


checkboxes = []
verified_races = []


unique = sorted(races[0].dataframe['Sub-event'].unique())
# unique = races[0].dataframe['Sub-event'].unique()


# initializes selector
# for i in unique:
#     checkboxes.append(st.checkbox(i))
# checkboxes.append(st.checkbox("all registrations"))
unique.append("all registrations")


quiz = st.radio(
    "select a type",
    unique
)



if quiz == "all registrations":
    graph_it("all registrations", races)
else:
    graph_it(quiz, races)



