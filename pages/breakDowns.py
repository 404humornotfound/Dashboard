import streamlit as st
from datetime import *
from class_init import *
import plotly.express as px

# initialize info class

info = Information()
info_df = info.dataframe

# initialize races
races = []
for i in range(len(info_df.index)):
    start_date = datetime.strptime(info_df['Registration start date'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(info.get_dataframe_by_gid(info_df['sheet gid'].iloc[i]), start_date, end_date, info_df['Name of race'].iloc[i]))


checkboxes = []


for i in range(len(info_df.index)):
    checkboxes.append(st.checkbox(races[i].race_name))

toggle_days_vs_days_to_race = st.checkbox("X axis labelling: On = days, Off = days until race")

for i in range(len(info_df.index)):
    if checkboxes[i]:
        if toggle_days_vs_days_to_race:
            races[i].graph_it()
        else: 
            races[i].graph_it_vs_days_to_race()


# todo add graphs breaking down age and gender

# fig = 
# st.plotly_chart(fig)