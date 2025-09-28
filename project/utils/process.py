import os
import logging
import time
import json
import ast
import datetime as dt
import re

from dotenv import load_dotenv

# from utils.google import GoogleSearch, HTTPError, MaxRetryError
from utils.google import GoogleSearch, HTTPError, MaxRetryError
from utils.browser import Browser, RequestsError
from utils.counter import Stats

from utils.gemini import gemini_check_content_langchain
from utils.openai import get_openai_response_langchain

from app.models import ScrapedLink

logger = logging.getLogger(__name__)

load_dotenv(override=True)

serp_proxy_url = os.getenv("SERP_PROXY_URL").strip()

GEMINI_AI_MAX_RETRIES= 2  


def start_processing(keyword, sector, pages, prompt):
    logger.info(f"Started processing with keyword='{keyword}', sector='{sector}', pages={pages}, prompt='{prompt}'")
    links = []
    google =  GoogleSearch(proxy=serp_proxy_url)
    browser = Browser()
    pages = int(pages)
    for page in range(1, pages + 1):
        try:
            _links = google.search(keyword=keyword, page=page)
            links.extend(_links)
        except (HTTPError, MaxRetryError):
            print(
                "there are some issues with serp proxy, if persists, please contact developer"
            )
            break
        
    links = list(set(links)) if links else [] #for removing duplicates
    logger.info('google search completed ')
    
    contents = []
    Stats.total = len(links)
    
    for link in links:
        if ScrapedLink.objects.filter(url=link).exists():
            print(f"{link} already exists",flush=True)
            logger.info(f"{link} already exists")
            Stats.already_exists+=1
            continue

        else:
            ScrapedLink.objects.create(url=link)

        max_retry = 2
        retry = 0
        base_delay = 2
        max_text_length = 10000
        while retry <= max_retry:
            try:
                content = browser.browse(link, max_text_length)
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
        ai_response = get_openai_response_langchain(prompt,content)
        
        if not ai_response:
            ai_response = gemini_check_content_langchain(prompt,content)
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
                res_dict = json.loads(result) if not isinstance(result,dict) else result
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