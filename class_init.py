import pandas as pd
from datetime import *
from operator import *
from jsonHandling import *


class Information:
    def __init__(self) -> None:
        self.stuff = get_secure_info()
        self.info_gid = self.stuff[0]
        self.sheet_id = self.stuff[1]
        self.sheet_name = self.stuff[2]
        # print(f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={self.sheet_name}&gid={self.info_gid}")
        self.url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={self.sheet_name}&gid={self.info_gid}"

        self.dataframe = pd.DataFrame(pd.read_csv(self.url, dtype=str).fillna(""))
        # print(self.dataframe)

    def get_dataframe_by_gid(self,given_gid: str) -> pd.DataFrame:
        url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&sheet={self.sheet_name}&gid={given_gid}"
        return pd.DataFrame(pd.read_csv(url, dtype=str).fillna(""))



class Race:
    def __init__(self, dataframe: pd.DataFrame, start_date: datetime, end_date: datetime, race_name: str) -> None:
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
        self.dataframe['just_date'] = pd.to_datetime(self.dataframe['just_date'])
        self.dataframe = self.dataframe.set_index('just_date')




    def get_final_total_unique(self) -> pd.DataFrame:
        unique_events = self.dataframe['Sub-event'].unique()
        arr = []
        nums = []
        for i in unique_events:
            num = countOf(self.dataframe['Sub-event'], i)
            nums.append(num)
            arr.append([i, num])
        return pd.DataFrame(unique_events, nums)
    

    def get_accumulated_unique_by_day(self, days_until_race:int):
        datee = self.end_date-timedelta(days=days_until_race)
        dates_of_interest_df = self.dataframe.loc[self.start_date:datee]
        unique_events = sorted(self.dataframe['Sub-event'].unique())
        arr = []
        nums = []
        overall_nums = []
        for i in unique_events:
            num = countOf(dates_of_interest_df['Sub-event'], i)
            num1 = countOf(self.dataframe['Sub-event'], i)
            overall_nums.append(num1)
            nums.append(num)
            arr.append([i, num, num1])
        unique_events.append("z_sum")
        nums.append(len(dates_of_interest_df.index))
        overall_nums.append(len(self.dataframe.index))
        df = pd.DataFrame({"events":unique_events,f"{days_until_race} days left":nums, "total":overall_nums})
        return df





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
    def get_dataframe(self) -> pd.DataFrame:
        return self.dataframe
