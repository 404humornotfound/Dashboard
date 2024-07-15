import pandas as pd
import json
from datetime import datetime


def get_gids_local_from_year(year_number):  # gets gids from local json instead of google api (keeping requests low)
    f = open('info.json')
    data = json.load(f)
    gid = ""
    index = 0
    for i in data['name']:
        test = int(i)
        if test == year_number:
            gid = data['gid'][index]
            f.close()
            break
        index += 1

    return gid

def get_all_gids():
    f = open('info.json')
    data = json.load(f)
    gids = []
    for count, i in enumerate(data['name']):
        gids.append([data['name'][count], data['gid'][count]])
    f.close()
    return gids


def get_sheet_name_and_id():  # returns name then id in a array
    f = open('info.json')
    data = json.load(f)
    lst = [data['sheet_id'], data['sheet_name']]
    f.close()
    return lst


def get_dataframe_by_year(year):  # returns dataframe from sheet
    lst = get_sheet_name_and_id()

    gid = get_gids_local_from_year(year)

    url = f"https://docs.google.com/spreadsheets/d/{lst[0]}/gviz/tq?tqx=out:csv&sheet={lst[1]}&gid={gid}"

    data = pd.read_csv(url, dtype=str).fillna("")
    df = pd.DataFrame(data)
    return df


def is_new_data(df, year_number):
    dataframe = get_dataframe_by_year(year_number)
    if dataframe.equals(df):
        return 0  # means same data
    else:
        if len(df.index) < len(dataframe.index) - 5:
            return 2  # means too much data will be removed
        return 1  # means upload new data


def get_first_date(year):  # checks if correct year by first registration date
    data = get_dataframe_by_year(year)
    return data['Date Registered'].iloc[0]

