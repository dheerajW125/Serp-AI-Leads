from pathlib import Path
import logging
import traceback
import sys
import datetime as dt

from django.core.management.base import BaseCommand
from django.conf import settings



from utils.helers import get_input_values,generate_csv
from utils.sheets import GoogleSheetsClient
from utils.process import start_processing
from utils.counter import Stats

import pandas as pd


logger = logging.getLogger(__name__)

logging.basicConfig()

DATA_DIR:Path = settings.DATA_DIR
BASE_DIR:Path = settings.BASE_DIR

class Command(BaseCommand):
    help = 'Prints Hello, World'

    def handle(self, *args, **kwargs):
        hellow()
        main_process()

def hellow():
    print("hellow world")
    

def main_process():
    logger.info('started the SERP AI Project')
        
    # BASE_DIR = Path(__file__).resolve().parents[4]
    print(BASE_DIR)
    CREDS_PATH = BASE_DIR / 'singular-citron-435211-p7-03fab432846a.json'
    print(CREDS_PATH)

    sheet_id = '1Mf4BbcX2v13x-cY4rEvj-Ez2oel30OKPeU9qnEk_jQA'       # ✅ Sheet ID
    worksheet_name = 'input_sheet'                                       # ✅ Actual tab name

    sheet_client = GoogleSheetsClient(creds_path=CREDS_PATH,sheet_id=sheet_id)
    input_sheet:pd.DataFrame = sheet_client.get_df(worksheet_name)
    
    input_sheet.to_csv('test.csv',index=False)
    filtered_df = get_input_values(input_df=input_sheet)
    print(filtered_df)
    
    all_output = []

    if  not filtered_df.empty :
        
        try:
            # REQUIRED_DATE = "2024-11-14"

            # required_input_df = input_df[input_df["Date"] == REQUIRED_DATE]
            # keyword = required_input_df["Keyword"].values[0]
                
            filtered_positions = filtered_df.index.tolist()
            sheet_start_row = 2 
            
            
            # Compute start and end row in sheet coordinates (1-based)
            start_row = filtered_positions[0] + sheet_start_row
            end_row = filtered_positions[-1] + sheet_start_row

            SHEET_UPDATE_RANGE:str = f'E{start_row}:F{end_row}'
            for index,row in filtered_df.iterrows():
                required_input_df = row.to_dict()
                date = required_input_df["Date"]
                keyword = required_input_df["Keyword"]
                sector = required_input_df["Sector"]
                pages = required_input_df["Number of google search result pages"]
                prompt = required_input_df["Test prompt"]
                print(date, keyword, sector, pages, prompt,flush=True)
                logger.info("started processing for date=%s, keyword=%s, sector=%s, pages=%s, prompt=%s",date,keyword,sector,pages,prompt)

                output = start_processing(keyword, sector, pages, prompt)

                filtered_df.loc[filtered_df.index, 'Run'] = 'FALSE' #df updation logic
                filtered_df.style.set_properties(subset=['Run'], **{'text-align': 'center'})
                #filtered_df.loc[filtered_df.index, 'Stats'] = "sample stats" #df updation logic
                
                timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
                stats = Stats.display_stats()
                filtered_df.loc[filtered_df.index, 'Stats'] = stats
                Stats.reset_stats()
                all_output.extend(output)
            
            if all_output:
                filename = DATA_DIR / f"result-{timestamp}.csv"
                generate_csv(all_output, filename)
                sheet_client.append_data('output_sheet1',all_output)
              
            values = filtered_df[['Run', 'Stats']].values.tolist()
            sheet_client.update_values(worksheet_name=worksheet_name,range_str=SHEET_UPDATE_RANGE,values=values)
            
        except Exception as e:
            logger.error(f'Erropr occured while processing : {e} | tarce : {traceback.format_exc()}')
            
    logger.info('completed  the SERP AI Project')