from app.ai import CustomOpenAI
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
import datetime as dt
from dotenv import load_dotenv
import os
import openai
from app.gsheets_integrator import authorize_and_get_spreadsheet, create_input_googlesheet, create_output_gsheets


# Disable all logging
logging.disable(logging.CRITICAL)


BASE_DIR = os.path.dirname(__file__)
if hasattr(sys, "_MEIPASS"):
    BASE_DIR = os.path.dirname(sys.argv[0])


def generate_csv(data, filename):
    if not data:
        raise ValueError("Data is empty. There is nothing to write to the CSV file.")

    headers = data[0].keys()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        writer.writeheader()

        writer.writerows(data)

    print(f"Data successfully written to {filename}")



class App:
    def __init__(self, serp_proxy_url) -> None:
        self.ai = CustomOpenAI()
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

        print("searches complete")
        # print(links)

        contents = []
        for link in links:
            if link_exists(link):
                print(f"{link} already exists")
                continue

            else:
                insert_link(link)

            try:
                content = self.browser.browse(link)
                contents.append({"link": link, "content": content})
            except RequestsError:
                print(f"could'nt browse {link}")

        print("browsing complete")

        output = []
        date = dt.datetime.today().strftime("%Y-%m-%d")
        for content in contents:
            ai_response = self.ai.check_content(
                prompt=prompt, content=content["content"]
            )
            try:
                res_dict = json.loads(ai_response.strip())
                if res_dict["response"] == "yes":
                    output.append({"date":date, "category":keyword, "sector":sector, "link":content["link"], "ai_response":res_dict["response"], "company_name":res_dict["company_name"], "location":res_dict["location"]})
            except:
                try:
                    result = ast.literal_eval(re.search('({.+})', ai_response).group(0))
                    res_dict = json.loads(result)
                    if res_dict["response"] == "yes":
                        output.append({"date":date, "category":keyword, "sector":sector, "link":content["link"], "ai_response":res_dict["response"], "company_name":res_dict["company_name"], "location":res_dict["location"]})
                except:
                    pass

            # output.append({"link": content["link"], "ai_response": ai_response})
        return output


if __name__ == "__main__":

    load_dotenv(override=True)

    serp_proxy_url = os.getenv("SERP_PROXY_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    openai.api_key = openai_api_key

    if not serp_proxy_url:
        raise Exception("please configure serp proxy in environment")

    if not openai_api_key:
        raise Exception("please configure openai apikey in environment")

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
        logging.info(f"The input sheet doesn't exist or input date doesn't exists in the input excel or some other error: {e}.")

    input('press enter to close...')

# read the content carefully. summarize the content to check if the content is for a company that provides staffing solutions in hospitality sector in usa. if yes, then give the summary, otherwise summarize as "not for hospitality sector".
# read the content carefully. does this company provide staffing solution in hospitality sector and is based in USA? Yes or No
# Read the content carefully. Analyse the content to check if this company provides staffing solutions for hospitality sector and is based in usa? Provide the result in the format {"response":"yes","company_name":"indeed.com","location":"usa"}
