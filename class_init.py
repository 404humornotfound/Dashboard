import pandas as pd
from datetime import *
from operator import *
from jsonHandling import *
import plotly.express as px
import streamlit as st
import os
from dotenv import load_dotenv, dotenv_values


load_dotenv() 

class Information:
    def __init__(self) -> None:
        self.info_gid = os.getenv("info_gid")
        self.sheet_id = os.getenv("sheet_id")
        self.sheet_name = os.getenv("sheet_name")
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
        self.dataframe = self.dataframe.set_index('Participant ID')
        self.dataframe['rly_just_date'] = pd.to_datetime(self.dataframe['just_date'])
        print(f"dtype: {self.dataframe['rly_just_date'].dtype}")




    """
    Returns 2d array of 0 column of unique event names, 1 column is the number of people in said event 
    """
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
        df = self.dataframe
        datee = self.end_date-timedelta(days=days_until_race)
        # dates_of_interest_df = self.dataframe['rly_just_date'].loc[self.start_date:datee]
        # the problem is figuring out how to get the date range
        dates_of_interest_df = self.dataframe[(self.start_date >= df['just_date']) & (self.end_date <= df['just_date'])]
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

        for i in range((self.end_date - self.start_date).days + 1):
            day = self.start_date + timedelta(days=i)
            frequency.append(len(self.dataframe[self.dataframe.just_date == day]))
        return frequency
    
    def to_frequency_unique(self, unique:str):
        frequency = []
        days = []

        for i in range((self.end_date - self.start_date).days+1):
            day = self.start_date + timedelta(days=i)
            try:
                temp = self.dataframe.loc[day] 
            except:
                frequency.append(0)
                days.append(0)
            else:
                days.append(day)
                nums = countOf(temp, unique)
                frequency.append(nums)
        return frequency

    

    def get_dataframe(self) -> pd.DataFrame:
        return self.dataframe
    
#graphing dedicated fxns below:



    def get_arr_days(self):
        days = []

        for i in range((self.end_date - self.start_date).days + 1):
            days.append(self.start_date + timedelta(days=i))

        return days
    








    def graph_it(self):
        days = self.get_arr_days()

        data = {
        "Days Until Race": days,
        }




        unique_events = sorted(self.dataframe['Sub-event'].unique())
        list_of_frequencies = [[]]

        overall_frequency = []

        for i in range(len(unique_events)-1):
            list_of_frequencies.append([])


        # .set_index('just_date')

        for i in days:

            try:
                temp = self.dataframe.loc[i]
            except:
                for j in range(len(unique_events)):
                    list_of_frequencies[j].append(0)
                overall_frequency.append(0)
            
            else:

                overall_frequency.append(0)

                for j in range(len(unique_events)):
            
                    that_days_frequency = countOf(temp['Sub-event'], unique_events[j])
                    list_of_frequencies[j].append(that_days_frequency)
                    overall_frequency[days.index(i)] += that_days_frequency


            

        data.update({'Registrations all':overall_frequency})
        for i in range(len(unique_events)):
            data.update({unique_events[i]:list_of_frequencies[i]})

        # print(data)



        dataframe1 = pd.DataFrame(data)



        unique_events.append('Registrations all')

        
        fig = px.line(dataframe1, x='Days Until Race', y=unique_events, title=f"{self.race_name}")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig)


    def graph_it_vs_days_to_race(self): # graphed vs days until race
        days = self.get_arr_days()
        dayss = []
        for i in range(len(days)):
            dayss.append(len(days)-i)
        data = {
        "Days Until Race": dayss,
        }




        unique_events = sorted(self.dataframe['Sub-event'].unique())
        list_of_frequencies = [[]]

        overall_frequency = []

        for i in range(len(unique_events)-1):
            list_of_frequencies.append([])




        for i in days:

            try:
                temp = self.dataframe.loc[i]
            except:
                for j in range(len(unique_events)):
                    list_of_frequencies[j].append(0)
                overall_frequency.append(0)

            else:

                # overall_frequency.append(len(temp.index))
                overall_frequency.append(0)
                for j in range(len(unique_events)):
            
                    that_days_frequency = countOf(temp['Sub-event'], unique_events[j])
                    list_of_frequencies[j].append(that_days_frequency)
                    overall_frequency[days.index(i)] += that_days_frequency


        data.update({'Registrations all':overall_frequency})
        for i in range(len(unique_events)):
            data.update({unique_events[i]:list_of_frequencies[i]})

        # print(data)



        dataframe1 = pd.DataFrame(data)

        unique_events.append('Registrations all')

        
        fig = px.line(dataframe1, x='Days Until Race', y=unique_events, title=f"{self.race_name}")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig)

        return None
    

    

