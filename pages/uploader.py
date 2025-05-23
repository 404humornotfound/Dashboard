import streamlit as st
import pandas as pd
from datetime import datetime, date
from class_init import *
import csv


# helpful init
info = Information()
info_df = info.dataframe

races = []
for i in range(len(info_df.index)):
    start_date = datetime.strptime(info_df['Registration start date'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(pd.read_csv(f'csvs/{start_date.year}_race.csv'), start_date, end_date, info_df['Name of race'].iloc[i]))

year_selector = st.radio(
    "Select race you want to modify",
    [i.race_name for i in races]
)
st.write(f"currently uploading for: {year_selector}")

current_year_number = date.today().year

uploaded = False
uploaded_file = st.file_uploader("Upload csv here",type=".csv", accept_multiple_files=False)


if uploaded_file is not None:
    data = pd.read_csv(uploaded_file, dtype=str, usecols=['Date Registered', 'Sex', 'City', 'State', 'ZIP/Postal Code', 'Sub-event', 'Age'])
    dataframe = pd.DataFrame(data).fillna("")
    st.write(dataframe)
    uploaded = True

submit = st.button("submit")

if submit and uploaded:
    stringg = dataframe['Date Registered'].iloc[0]
    stringg = stringg[:len(stringg)-4]
    year_of_csv = datetime.strptime(stringg, "%Y-%m-%d %H:%M:%S").year
    print(year_of_csv)
    if current_year_number == year_of_csv:
        match is_new_data(dataframe):
            case 0:
                st.write("Data already up to date")
            case 1:
                write_data(dataframe, current_year_number)
                st.write("New data uploaded")
            case 2:
                st.write("Too many values have been removed from the spreadsheet, try to upload a more recent sheet")
    else:
        st.write("Uploaded data is invalid, please check the year of data you are uploading for is the current year")





st.write("Create a new race below:")
new_uploaded_file = st.file_uploader("Upload csv here",type=".csv", accept_multiple_files=False, key="adsklfj")
race_name = st.text_input("Input race name here ex. 2024 race -- Must be just the year")
start_date = st.date_input("Input start date of registrations")
end_date = st.date_input("Input last day of registrations")
create_new_race = st.button("Create new race")

if create_new_race and new_uploaded_file is not None and race_name is not None and start_date is not None and end_date is not None:
    data1 = pd.read_csv(new_uploaded_file, dtype=str, usecols=['Participant ID', 'Date Registered', 'Bib Numbers', 'Last Name', 'First Name', 'Sex', 'Date of Birth', 'Email', 'City', 'State', 'Address', 'ZIP/Postal Code', 'Country', 'Sub-event', 'Age', 'Confirmation No.'])
    dataframe1 = pd.DataFrame(data).fillna("")
    # write_new_race(dataframe1, race_name, start_date, end_date)
    with open(f"csvs/{race_name}_race.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(dataframe1)

