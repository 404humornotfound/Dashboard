import streamlit as st
import pandas as pd
from infoGrabber import to_frequency, draw_graphs_and_summary, get_x_and_frequency
from gsheetInterface import get_dataframe_by_year
from datetime import datetime, timedelta
import plotly.express as px

dates = [
    [datetime.strptime("2023-04-28", '%Y-%m-%d'),
    datetime.strptime("2023-10-14", '%Y-%m-%d')]
                       ]


home_page = st.button("Home page")

if home_page:
    st.switch_page("dashboard.py")


df = get_dataframe_by_year(6)

for i in range(len(df.index)):
    string = df['Date Registered'].iloc[i]
    string = string[:len(string) - 4]
    df.at[i, 'Date Registered'] = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
df['Date Registered'] = pd.to_datetime(df['Date Registered'], format='%Y-%m-%d %H:%M:%S')
df['just_date'] = df['Date Registered'].dt.date

draw_graphs_and_summary(df, dates[0][0], dates[0][1], 6)

#gender pie chart
gender_info = get_x_and_frequency(df, 'Sex')

fig = px.pie(values=gender_info['frequency'], names=gender_info['category'])
st.write("Pie Chart of Gender")
st.plotly_chart(fig)

#race divide pie chart
gender_info = get_x_and_frequency(df,'Sub-event')

fig = px.pie(values=gender_info['frequency'], names=gender_info['category'])
st.write("Pie Chart of events ")
st.plotly_chart(fig)




