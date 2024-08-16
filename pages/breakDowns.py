import streamlit as st
import streamlit as st
from datetime import *
from class_init import *


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
    


    


# dataframe1 = pd.DataFrame(data1)
# fig = px.line(dataframe1, x='Days Until Race', y=['Registrations for 5K', 'Registrations for 10K', 'Registrations all'],
#               color_discrete_sequence=['gray', 'red', 'blue'])
# fig.update_xaxes(type='category')
# st.plotly_chart(fig)