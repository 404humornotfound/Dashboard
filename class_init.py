import pandas as pd
from datetime import *
from operator import *


class Race:
    def __init__(self, dataframe: pd.DataFrame, start_date: date, end_date: date, race_name: str):
        self.dataframe = dataframe
        self.start_date = start_date
        self.end_date = end_date
        self.race_name = race_name

        # just_date column for easier graphing
        for i in range(len(self.dataframe.index)):
            string = self.dataframe['Date Registered'].iloc[i]
            string = string[:len(string) - 4]
            self.dataframe.at[i, 'Date Registered'] = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        self.dataframe['Date Registered'] = pd.to_datetime(self.dataframe['Date Registered'], format='%Y-%m-%d %H:%M:%S')
        self.dataframe['just_date'] = self.dataframe['Date Registered'].dt.date
        self.dataframe = self.dataframe.sort_values(by=['just_date'])  # to guarentee info is always in chronological sign up order



    def get_final_total_unique(self):
        unique_events = self.dataframe['Sub-event'].unique()
        arr = []
        nums = []
        for i in unique_events:
            num = countOf(self.dataframe['Sub-event'], i)
            nums.append(num)
            arr.append([i, num])
        return unique_events, nums




    def to_frequency(self):
        frequency = []
        days = []
        start_date_input = self.dataframe['just_date'].iloc[0]
        end_date_intput = self.dataframe['just_date'].iloc[len(self.dataframe)-1]
        for i in range((end_date_intput - start_date_input).days + 1):
            days.append(start_date_input + timedelta(days=i))
            frequency.append(0)
        for i in range(len(days)):
            frequency[i] = countOf(self.dataframe['just_date'], days[i])
        return frequency
