import streamlit as st
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
    start_date = datetime.strptime(info_df['Registration start date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(info.get_dataframe_by_gid(info_df['sheet gid'].iloc[i]), start_date, end_date, info_df['Name of race (unique)'].iloc[i]))


checkboxes = []


for i in range(len(info_df.index)):
    checkboxes.append(st.checkbox(races[i].race_name))

    start_date = datetime.strptime(info_df['Registration start date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(info.get_dataframe_by_gid(info_df['sheet gid'].iloc[i]), start_date, end_date, info_df['Name of race (unique)'].iloc[i]))
    

for i in range(len(info_df.index)):
    if checkboxes[i]:
        races[i].graph_it()
        


