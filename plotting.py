# imports
import streamlit as st
import pandas as pd
import os
import datetime as dt
from dotenv import load_dotenv
import os
import openai
from main_app import App, generate_csv, BASE_DIR
from app.gsheets_integrator import authorize_and_get_spreadsheet, create_input_googlesheet, create_output_gsheets


# page title
st.set_page_config(page_title="App created for Serp AI Leads with google sheets integration and Rapid API deployment")
st.title("Dataframe output to show open ai analysis of google serp api search results for jo search keyword and sub sector.")

# file uploads
container = st.container()

load_dotenv(override=True)

serp_proxy_url = os.getenv("SERP_PROXY_URL")
openai_api_key = os.getenv("OPENAI_API_KEY")

openai.api_key = openai_api_key

if not serp_proxy_url:
    raise Exception("please configure serp proxy in environment")

if not openai_api_key:
    raise Exception("please configure openai apikey in environment")

app = App(serp_proxy_url=serp_proxy_url)

# authorize spreadsheet through google sheets api
spreadsheet = authorize_and_get_spreadsheet()

# create input sheet
input_ws = create_input_googlesheet(spreadsheet)

# read input sheet to get keyword, pages, prompt
input_df = input_ws.get_as_df()

try:
    REQUIRED_DATE = "2024-11-14"
    required_input_df = input_df[input_df["Date"] == REQUIRED_DATE]
    keyword = required_input_df["Keyword"].values[0]
    sector = required_input_df["Sector"].values[0]
    pages = required_input_df["Number of google search result pages"].values[0]
    prompt = required_input_df["Test prompt"].values[0]
    print(keyword, pages, prompt)

    # prompt: does this company provide staffing solution in hospitality sector and is based in USA
    output = app.run(keyword, sector, pages, prompt)
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if output:
        filename = os.path.join(BASE_DIR, f"results/result-{timestamp}.csv")
        filename = os.path.normpath(filename)
        generate_csv(output, filename)
        create_output_gsheets(spreadsheet, output)
except Exception as e:
    print(f"The input sheet doesn't exist or input date doesn't exists in the input excel or some other error: {e}.")

#input('press enter to close...')

st.write(f"Input Dataframe: {input_df}")
st.write(f"DataFrame source: {filename}")

df = pd.read_csv(filename)
# df = pd.read_csv('Spotify_Youtube.csv') # only for vs code terminal
st.dataframe(df)
