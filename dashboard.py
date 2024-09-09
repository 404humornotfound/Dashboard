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
    start_date = datetime.strptime(info_df['Registration start date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(info.get_dataframe_by_gid(info_df['sheet gid'].iloc[i]), start_date, end_date, info_df['Name of race (unique)'].iloc[i]))
    

# print(races[0].to_frequency())


checkboxes = []
verified_races = []


unique = sorted(races[0].dataframe['Sub-event'].unique())

for i in unique:
    checkboxes.append(st.checkbox(i))
checkboxes.append(st.checkbox("all registrations"))


for i in range(len(checkboxes)):
    if checkboxes[i]:
        if i < len(checkboxes)-1:
            graph_it(unique[i], races)
        else:
            graph_it("all registrations", races)


