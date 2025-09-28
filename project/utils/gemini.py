from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from typing import Optional
import logging


from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

def gemini_check_content_langchain(
    prompt: str,
    content: dict,
    model_name: str = "gemini-1.5-flash",
    max_output_tokens: int = 1024,
    temperature: float = 0.3,
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Uses LangChain + Gemini to analyze a prompt + text and return JSON response.
    """

    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
             # or set env var GOOGLE_API_KEY
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )
        text = content.get('content')
        full_prompt = f"{prompt}. Return just the JSON, do not wrap it in markdown or any other formatting.:{text}"
        response = llm.invoke([HumanMessage(content=full_prompt)])

        return response.content.strip() if response.content else None

    except Exception as e:
        print(f"Error during analysis: {e}", flush=True)
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return None


if __name__=='__main__':
    import requests
    from utils.browser import Browser
    
    load_dotenv()
    prompt = 'Does this company provide staffing solution in Healthcare Staffing and their staffing in agency and is based in USA? Provide the result in the format {"response":"yes","company_name":"indeed.com","location":"usa"}'
    content ={}
    #resposne = requests.get('https://www.innovapeople.com/',timeout=10)
    browser  = Browser()
    max_text_length = 10000
    txt = browser.browse('https://www.innovapeople.com/',max_text_length=max_text_length)
    
    content['content'] = txt
    print(txt)

    ai_response = gemini_check_content_langchain(prompt=prompt,content=content)
    
    print(ai_response)