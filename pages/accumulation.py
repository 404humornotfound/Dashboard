import streamlit as st
from datetime import *
from class_init import *


info = Information()
info_df = info.dataframe

races = []
for i in range(len(info_df.index)):
    start_date = datetime.strptime(info_df['Registration start date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date (YYYY-MM-DD) (inclusive)'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(info.get_dataframe_by_gid(info_df['sheet gid'].iloc[i]), start_date, end_date, info_df['Name of race (unique)'].iloc[i]))


today = datetime.today().date()

for i in reversed(range(len(races))):
    days_from_race = (races[i].end_date-today).days
    if days_from_race >= 0:
        st.write(f"today is {days_from_race} days from race")
        break


num_days = st.text_input("input days until race here")



if num_days.isnumeric():
    col1, col2 = st.columns(2)
    for i in reversed(range(len(races))):
        if i % 2 == 0:
            with col1:
                st.write(races[i].race_name)
                st.dataframe(races[i].get_accumulated_unique_by_day(int(num_days)).set_index('events'))
        else:
            with col2:
                st.write(races[i].race_name)
                st.dataframe(races[i].get_accumulated_unique_by_day(int(num_days)).set_index('events'))




# if num_days.isnumeric():
#     df = races[0].get_accumulated_unique_by_day(int(num_days)).set_index('events')

#     for i in range(len(races)-1):  
#             # df.merge(races[i+1].get_accumulated_unique_by_day(int(num_days)), rsuffix=f'_{races[i+1].race_name}')
#         df = df.join(races[i+1].get_accumulated_unique_by_day(int(num_days)), rsuffix=f'_{races[i+1].race_name}')


# st.dataframe(df)


