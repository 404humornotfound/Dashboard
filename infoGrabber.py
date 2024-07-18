import pandas as pd
from datetime import datetime, timedelta,date
from operator import *
import streamlit as st
import json

def to_frequency(startDate, endDate, df):
    frequency = []
    days = []
    for i in range((endDate - startDate).days + 1):
        days.append(startDate + timedelta(days=i))
        frequency.append(0)
    for i in range(len(days)):
        # frequency[i] = countOf(df['just_date'], days[i].date())
        frequency[i] = countOf(df['just_date'], days[i])
    data = pd.DataFrame(frequency, days)
    return data


def get_frequency_of_registrations_arr(dataframe):
    frequency = []
    days = []
    dataframe = dataframe.sort_values(by=['just_date'])
    endDate = dataframe['just_date'].iloc[len(dataframe.index)-1]
    startDate = dataframe['just_date'].iloc[0]

    for i in range((endDate - startDate).days + 1):
        days.append(startDate + timedelta(days=i))
        frequency.append(0)

    counter = 0
    for index, row in dataframe.iterrows():
        if days[counter] == row['just_date']:
            frequency[counter] += 1
        else:
            while days[counter] != row['just_date']:
                counter += 1
            frequency[counter] += 1
    return frequency


def get_x_and_frequency(df, nameOfCategory):
    frequency = []
    x = []
    for i in range(len(df.index)):
        if df[nameOfCategory].iloc[i] not in x:
            x.append(df[nameOfCategory].iloc[i])
            frequency.append(0)
    for i in range(len(x)):
        frequency[i] = countOf(df[nameOfCategory], x[i])
    data = pd.DataFrame({'frequency': frequency, 'category': x})
    return data


def draw_graphs_and_summary(df, start_date, end_date, year_number):

    data = to_frequency(start_date, end_date, df)
    col1, col2 = st.columns([4, 1])

    with col1:
        st.header("Registrations vs Date")
        st.line_chart(data)

    with col2:
        st.header(f"Stats for year {year_number}")
        st.write(f"Total Registrants: {len(df.index)}")
        max_series = pd.Series(data.max())
        st.write(f"Peak Registrations: {max_series[0]}")
        st.write(f"Total Days Until Race: {(end_date-start_date).days}")


def group_x_registrations_vs_date(dataframe, group, subgroup, startDate, endDate):  # returns only frequency of values
    frequency = []
    days = []
    dataframe = dataframe.sort_values(by=['just_date'])
    for i in range((endDate - startDate).days + 1):
        days.append(startDate + timedelta(days=i))
        frequency.append(0)

    day_number = 0
    for index, row in dataframe.iterrows():
        if row[group] == subgroup:
            if row['just_date'] == days[day_number]:
                frequency[day_number] += 1
            else:
                while row['just_date'] != days[day_number]:
                    day_number += 1
                frequency[day_number] += 1

    return frequency


def get_arr_of_all_dates(df):
    dataframe = df.sort_values(by=['just_date'])
    endDate = dataframe['just_date'].iloc[len(dataframe.index)-1]
    startDate = dataframe['just_date'].iloc[0]
    days = []
    for i in range((endDate - startDate).days + 1):
        days.append(startDate + timedelta(days=i))
    return days




def get_just_date(df):
    for i in range(len(df.index)):
        string = df['Date Registered'].iloc[i]
        string = string[:len(string) - 4]
        df.at[i, 'Date Registered'] = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
    df['Date Registered'] = pd.to_datetime(df['Date Registered'], format='%Y-%m-%d %H:%M:%S')
    df['just_date'] = df['Date Registered'].dt.date
    return df['just_date']


def get_len_of_registrations_window(year): # manually insert dates b/c race may not be complete but
    match year:
        case 5:
            return (datetime(2022, 10, 8) - datetime(2022, 4, 24)).days
        case 6:
            return (datetime(2023, 10, 14) - datetime(2023, 4, 28)).days
        case 7:
            return (datetime(2024, 10, 12) - datetime(2024, 4, 5)).days
        case _:
            raise Exception("year has no data")


def get_start_end_date_by_year(year: int):
    match year:
        case 2022:
            return [datetime(2022, 4, 24), datetime(2022, 10, 8)]
        case 2023:
            return [datetime(2023, 4, 28), datetime(2023, 10, 14)]
        case 2024:
            return [datetime(2024, 4, 5), datetime(2024, 10, 12)]
        case _:
            raise Exception("year has no data")


def get_arr_all_dates():
    return [
        [datetime(2022, 4, 24), datetime(2022, 10, 8)],

    [datetime(2023, 4, 28), datetime(2023, 10, 14)],

     [datetime(2024, 4, 5), datetime(2024, 10, 12)]
    ]


def get_days_from_race(current_year: int): # returns numerical value of days from race
    today = date.today()
    end_day = get_start_end_date_by_year(current_year)[1].date()

    days = (end_day - today).days
    return days


def smol_days_to_actual_years(smol_day):
    f = open('info.json')
    data = json.load(f)
    for index, i in data['name']:
        if int(i) == int(smol_day):
            to_return = data['name'][index]
            f.close()
            return to_return
