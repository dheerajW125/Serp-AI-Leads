import logging
from typing import Optional
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

def get_openai_response_langchain(
    prompt: str,
    content: dict,
    model_name: str = "gpt-3.5-turbo",
    temperature: float = 0.3,
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Uses LangChain + OpenAI to analyze prompt and content and return the response.
    """
    return None
    try:
        llm = ChatOpenAI(
            model=model_name,
            #openai_api_key=api_key,  # or set env var OPENAI_API_KEY
            temperature=temperature
        )

        messages = [
            HumanMessage(content=content.get("content", "")),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)

        result = response.content.strip() if response.content else None

        print(f"OpenAI link: {content.get('link')} response: {result}", flush=True)
        logger.info(f"OpenAI link: {content.get('link')} response: {result}")

        return result

    except Exception as e:
        print(f"Error occurred with OpenAI GPT for link: {content.get('link')} | error: {e}", flush=True)
        logger.error(f"Error occurred with OpenAI GPT for link: {content.get('link')} | error: {e}", exc_info=True)
        return None


if __name__=='__main__':
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

    ai_response = get_openai_response_langchain(prompt=prompt,content=content)
    
    print(ai_response)