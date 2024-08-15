from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st


def setup():  # literally copied and pasted just allows for writing to spreadsheets
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file(
        'secret_new_key.json',
        scopes=scopes
    )

    gc = gspread.authorize(credentials)
    name = 'WaterDogRunData'
    sh = gc.open(name)

    return sh


def get_gids():  # uses api to get gids
    sh = setup()

    for x in sh.worksheets():
        i = str(x)
        print()
    return sh.worksheets()


def strip_name_and_id_from_string(i: str):
    second_quote_location = i[13:].find('\'')+13
    second_string = i[second_quote_location:]
    return [i[12:second_quote_location], second_string[second_string.find(':')+1:second_string.find('>')]]
    

