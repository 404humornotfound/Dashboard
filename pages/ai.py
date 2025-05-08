import google.generativeai as genai
import os
from class_init import *
from dotenv import load_dotenv, dotenv_values
load_dotenv() 

info = Information()
info_df = info.dataframe

# initialize races
races = []
for i in range(len(info_df.index)):
    start_date = datetime.strptime(info_df['Registration start date'].iloc[i], "%Y-%m-%d").date()
    end_date = datetime.strptime(info_df['Registration end date'].iloc[i], "%Y-%m-%d").date()
    races.append(Race(info.get_dataframe_by_gid(info_df['sheet gid'].iloc[i]), start_date, end_date, info_df['Name of race'].iloc[i]))



api_key = os.getenv("gemeni_api_key")

response = model.generate_content("Tell me a joke about AI.")


def generate_llm_response(key:str, question:str, races:list):
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-pro")
    parts_of_question = []
    parts_of_question.append("Database:")
    for i in races:
        sql = f"create table {i.race_name}("
        columns = i.columns
        for i in columns:
            sql +=f"{i} {i.dtype},"
        sql = sql[:-1]
        sql+=")"
        parts_of_question.append(sql)
    parts_of_question.append(f"With the previous data, answer the following question: {question}")
    return model.generate_content()
    
        





# Print the output
print(response.text)