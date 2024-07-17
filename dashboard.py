import pandas as pd
from datetime import datetime, date
from gsheetInterface import get_all_gids, get_dataframe_by_year
from infoGrabber import get_just_date, group_x_registrations_vs_date, get_frequency_of_registrations_arr, get_arr_of_all_dates, get_len_of_registrations_window, get_days_from_race
import plotly.express as px
import streamlit as st

gidsList = get_all_gids()



# df = get_dataframe_by_year(int(gidsList[len(gidsList)-2][0]))
# dataframe = get_dataframe_by_year(int(gidsList[len(gidsList)-1][0]))

df = get_dataframe_by_year(6)
dataframe = get_dataframe_by_year(7)

df['just_date'] = get_just_date(df)
dataframe['just_date'] = get_just_date(dataframe)



# dates = get_arr_of_all_dates(df['just_date'].iloc[0], df['just_date'].iloc[len(df.index)-1])
fiveK = group_x_registrations_vs_date(df, 'Sub-event', '5K', df['just_date'].iloc[0], df['just_date'].iloc[len(df.index)-1])
tenK = group_x_registrations_vs_date(df, 'Sub-event', '10K', df['just_date'].iloc[0], df['just_date'].iloc[len(df.index)-1])
allRegistrations = get_frequency_of_registrations_arr(df)


yr7 = get_frequency_of_registrations_arr(dataframe)
totalDays = (df['just_date'].iloc[len(df.index)-1] - df['just_date'].iloc[0]).days
days = []
for i in range(totalDays+1):
    days.append(totalDays-i)


data1 = {
    # "Days Until Race": days,
    "Days Until Race": get_arr_of_all_dates(df),
    "Registrations for 5K": fiveK,
    "Registrations for 10K": tenK,
    "Registrations all": allRegistrations
}



dataframe1 = pd.DataFrame(data1)
fig = px.line(dataframe1, x='Days Until Race', y=['Registrations for 5K', 'Registrations for 10K', 'Registrations all'],
              color_discrete_sequence=['gray', 'red', 'blue'])
fig.update_xaxes(type='category')
st.plotly_chart(fig)


minimum = 200
max = 0
list_of_years = []
for i in gidsList:
    num = int(i[0])
    list_of_years.append("year " + i[0])
    length = int(get_len_of_registrations_window(num))
    if minimum >= length:
        minimum = length
    if max <= length:
        max = length

d = st.text_input(f"Today is {get_days_from_race(2024)} days from race day. Print number of days until race you would like to see, must be < {minimum+2}")

if d.isdigit():
    num_days = int(d)

switch = st.toggle("On = days until race day, Off = start until given day")
st.write(switch)
if switch and d.isdigit() and num_days < minimum+2:
    total_days = []
    for i in range(num_days):
        total_days.append(num_days-i)
    data = {}

    data.update({"Days Until Race": total_days})
    for i in gidsList:
        lst = get_dataframe_by_year(int(i[0]))
        lst['just_date'] = get_just_date(lst)
        frequency = get_frequency_of_registrations_arr(lst)
        while len(frequency) < get_len_of_registrations_window(int(i[0])):
            frequency.append(0)
        data.update({"year " + i[0]: frequency[len(frequency)-num_days:]})
    real_df = pd.DataFrame(data)

    fig = px.line(real_df, x='Days Until Race', y=list_of_years)
    fig.update_xaxes(type='category')
    st.plotly_chart(fig)
else:
    st.write(f"year is not less than minimum number of days: {minimum+2}")

