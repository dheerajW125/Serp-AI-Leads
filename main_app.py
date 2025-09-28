from app.ai import CustomAI
from app.browse import Browser, RequestsError
from app.google import GoogleSearch, HTTPError, MaxRetryError
import os
import sys
from db import insert_link, link_exists
import logging
import csv
import re
import ast
import json
import random
import time
import datetime as dt
from dotenv import load_dotenv
import os
import openai
import google.generativeai as genai
import traceback
from app.gsheets_integrator import authorize_and_get_spreadsheet, create_input_googlesheet, create_output_gsheets,update_google_sheet_from_df
from pathlib import Path


# Ensure the console output uses UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')


print("This is an info message logged via print!")

DIR_PATH = Path(__file__).parent

FINISHED_FILE_PATH = DIR_PATH / 'finished_keyword.txt'

# Disable all logging
#logging.disable(logging.CRITICAL)


logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(__file__)
if hasattr(sys, "_MEIPASS"):
    BASE_DIR = os.path.dirname(sys.argv[0])
    
 
##Constraints 
GEMINI_AI_MAX_RETRIES= 2    
class Stats:
    yes=0
    no=0
    total=0
    already_exists = 0
    
    @classmethod
    def display_stats(cls):
        return f"yes: {cls.yes} | no: {cls.no} | total: {cls.total} | already exists: {cls.already_exists} | not scrapable : {cls.total- (cls.yes + cls.no + cls.already_exists)}"

    @classmethod
    def reset_stats(cls):
        cls.yes = 0
        cls.no = 0
        cls.total = 0
        cls.already_exists = 0


def generate_csv(data, filename):
    if not data:
        raise ValueError("Data is empty. There is nothing to write to the CSV file.")

    headers = data[0].keys()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        writer.writeheader()

        writer.writerows(data)

    print(f"Data successfully written to {filename}",flush=True)
    logger.info(f"Data successfully written to {filename}")


def get_openai_resposne(prompt,content):
    ai = CustomAI()
    ai_response = {}
    try:
        ai_response = ai.openai_check_content(
                    prompt=prompt, content=content["content"]
                )
        print(f"openai link : {content.get('link')} resposne : {ai_response}",flush=True)
        logger.info(f"openai link : {content.get('link')} resposne : {ai_response}")
    except Exception as e:
        print(f"error occurred with open ai gpt for link : {content.get('link')}  | error ; {e}",flush=True)   
        logger.error(f"error occurred with open ai gpt for link : {content.get('link')}  | error ; {e}",exc_info=True)

    return ai_response

def get_geminiai_resposne(prompt,content):
    ai = CustomAI()
    ai_response = {}
    current_retry = 0
    while current_retry <= GEMINI_AI_MAX_RETRIES:
        try:
            ai_response = ai.gemini_check_content(
                prompt=prompt, text=content["content"]
            )
            #print(ai_response,flush=True)
            print(f"openai link : {content.get('link')} resposne : {ai_response}",flush=True)
            logger.info(f"openai link : {content.get('link')} resposne : {ai_response}",flush=True)
            break
        except Exception as e:
            current_retry += 1

    return ai_response

class App:
    def __init__(self, serp_proxy_url) -> None:
        self.ai = CustomAI()
        self.browser = Browser()
        self.google = GoogleSearch(proxy=serp_proxy_url)

    def run(self, keyword, sector, pages, prompt):
        links = []
        for page in range(1, pages + 1):
            try:
                _links = self.google.search(keyword=keyword, page=page)
                links.extend(_links)
            except (HTTPError, MaxRetryError):
                print(
                    "there are some issues with serp proxy, if persists, please contact developer"
                )
                break
        links = list(set(links)) if links else [] #for removing duplicates
        print("searches complete",flush=True)
        # logger.info('\n'*5,)
        # logger.info("searches complete")
        # print(links)
        # with open(f'{keyword}_links.json','w') as f:
        #     json.dump(links,f,indent=4)
        # with open(f'{keyword}_links.json','r') as f:
        #     links = json.load(f)
        contents = []
        Stats.total = len(links)
        for link in links:
            if link_exists(link):
                print(f"{link} already exists",flush=True)
                logger.info(f"{link} already exists")
                Stats.already_exists+=1
                continue

            else:
                insert_link(link)

            max_retry = 2
            retry = 0
            base_delay = 2
            max_text_length = 10000
            while retry <= max_retry:
                try:
                    content = self.browser.browse(link, max_text_length)
                    contents.append({"link": link, "content": content})
                    #({"link": link, "content": content},flush=True)
                    break
                except RequestsError as e:
                    retry+=1
                    # delay = base_delay * (2 ** retry) + random.uniform(0, 1)
                    delay = base_delay
                    time.sleep(delay)
                    print(f"Retrying browse link {link} in {delay:.2f} seconds (retry {retry}/{max_retry})",flush=True)
                    logger.error(f"Retrying browse link {link} in {delay:.2f} seconds (retry {retry}/{max_retry})")
                    if retry>max_retry:
                        print(f"could'nt browse {link} | {e}",flush=True)
                        logger.info(f"could'nt browse {link} | {e}")
                

        print("browsing complete")
        logger.info("browsing complete")

        output = []
        date = dt.datetime.today().strftime("%Y-%m-%d")
        for content in contents:
            ai_response = get_openai_resposne(prompt,content)
            
            if not ai_response:
               ai_response = get_geminiai_resposne(prompt,content)
            try:
                res_dict = json.loads(ai_response.strip())
                if res_dict["response"] == "yes":
                    output.append({"date":date, "category":keyword, "sector":sector, "link":content["link"], "ai_response":res_dict["response"], "company_name":res_dict["company_name"], "location":res_dict["location"]})
                    Stats.yes+=1
                    print(f'link : {content["link"]} | ai_response:{res_dict["response"]}',flush=True)
                    logger.info(f'link : {content["link"]} | ai_response:{res_dict["response"]}')
                else:
                    Stats.no+=1
                    print(f'link : {content["link"]} | ai_response:no',flush=True)
                    logger.info(f'link : {content["link"]} | ai_response:no')
            except Exception as e1:
                print(f"Exception : {e1}")
                logger.error(f"Exception : {e1}",)
                try:
                    result = ast.literal_eval(re.search('({.+})', ai_response).group(0))
                    res_dict = json.loads(result)
                    if res_dict["response"] == "yes":
                        output.append({"date":date, "category":keyword, "sector":sector, "link":content["link"], "ai_response":res_dict["response"], "company_name":res_dict["company_name"], "location":res_dict["location"]})
                        Stats.yes+=1
                        print(f'link : {content["link"]} | ai_response:{res_dict["response"]}',flush=True)
                        logger.info(f'link : {content["link"]} | ai_response:{res_dict["response"]}')
                    else:
                        Stats.no+=1
                        print(f'link : {content["link"]} | ai_response:no',flush=True)
                        logger.info(f'link : {content["link"]} | ai_response:no')
                except Exception as e2:
                    print(f"error 2 : {e2} | response : {ai_response}")
                    logger.error(f"error 2 : {e2} | response : {ai_response}",exc_info=True)

            # output.append({"link": content["link"], "ai_response": ai_response})
            print(f'link : {content["link"]} | stats : {Stats.display_stats()}',flush=True)
            logger.info(f'link : {content["link"]} | stats : {Stats.display_stats()}')
        return output


if __name__ == "__main__":

    load_dotenv(override=True)

    serp_proxy_url = os.getenv("SERP_PROXY_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=google_api_key)
    openai.api_key = openai_api_key

    if not serp_proxy_url:
        raise Exception("please configure serp proxy in environment")

    if not openai_api_key:
        raise Exception("please configure openai api key in environment")

    if not google_api_key:
       raise Exception("Please configure google genai api key in environment")

    app = App(serp_proxy_url=serp_proxy_url)

    # keyword = input(">>> enter keyword: ")
    # while True:
    #     try:
    #         pages = int(input(">>> enter number of pages to search: "))
    #         break
    #     except ValueError:
    #         print("please enter a valid number")

    # prompt = input(">>> enter prompt: ")

    # authorize spreadsheet through google sheets api
    spreadsheet = authorize_and_get_spreadsheet()

    # create input sheet
    input_ws = create_input_googlesheet(spreadsheet)
    # read input sheet to get keyword, pages, prompt
    input_df = input_ws.get_as_df()
    print(input_df.columns)
    input_df.to_csv('temp.csv')
    filtered_df = input_df[input_df['Run'] == 'TRUE']
    #print(f"input : {input_df}")
    print(f"filterdf ; {filtered_df}")
    all_output = []

    try:
        # REQUIRED_DATE = "2024-11-14"
        # required_input_df = input_df[input_df["Date"] == REQUIRED_DATE]
        # keyword = required_input_df["Keyword"].values[0]

        for index,row in filtered_df.iterrows():
            required_input_df = row.to_dict()
            date = required_input_df["Date"]
            keyword = required_input_df["Keyword"]
            sector = required_input_df["Sector"]
            pages = required_input_df["Number of google search result pages"]
            prompt = required_input_df["Test prompt"]
            print(date, keyword, sector, pages, prompt,flush=True)
            logger.info("started processing for ",date, keyword, sector, pages, prompt)

            # try:
            #     with open(FINISHED_FILE_PATH) as f:
            #         keyword_list = [key.strip() for key in f.readlines()]
            #         print(keyword_list)

            #     if keyword in keyword_list:
            #         print(f"{keyword} is already processed. Going to next keyword from input google sheet...")
            #         continue
            # except Exception as e:
            #     print(f"finished_keyword.txt doesn't exists {e}")
            filtered_df.loc[filtered_df.index, 'Run'] = 'FALSE' #df updation logic

            # prompt: does this company provide staffing solution in hospitality sector and is based in USA
            output = app.run(keyword, sector, pages, prompt)
            timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            stats = Stats.display_stats()
            filtered_df.loc[filtered_df.index, 'Stats'] = stats
            Stats.reset_stats()
            # with open(FINISHED_FILE_PATH, "a") as f:
            #     f.write("\n"+keyword)
            all_output.extend(output)

        print(all_output)

        if all_output:
            filename = os.path.join(BASE_DIR, f"results/result-{timestamp}.csv")
            filename = os.path.normpath(filename)
            generate_csv(all_output, filename)
            create_output_gsheets(spreadsheet, all_output)
        update_google_sheet_from_df(input_ws, input_df, filtered_df)
    except Exception as e:
        print(f"The input sheet doesn't exist or input date doesn't exists in the input excel or some other error: {e}. {traceback.format_exc()}")
        logger.error("The input sheet doesn't exist or input date doesn't exists in the input excel or some other error: {e}")
    print(f"completd the execution",flush=True)
    logger.info("completd the execution")
    #input('press enter to close...')
    #https://docs.google.com/spreadsheets/d/1Mf4BbcX2v13x-cY4rEvj-Ez2oel30OKPeU9qnEk_jQA/edit?pli=1&gid=13686703#gid=13686703

# read the content carefully. summarize the content to check if the content is for a company that provides staffing solutions in hospitality sector in usa. if yes, then give the summary, otherwise summarize as "not for hospitality sector".
# read the content carefully. does this company provide staffing solution in hospitality sector and is based in USA? Yes or No
# Read the content carefully. Analyse the content to check if this company provides staffing solutions for hospitality sector and is based in usa? Provide the result in the format {"response":"yes","company_name":"indeed.com","location":"usa"}
