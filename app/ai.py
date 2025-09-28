import openai
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class CustomAI:

    def openai_check_content(self, prompt, content):
        chat_completion= openai.ChatCompletion.create(
            messages=[
                {
                    "role": "user",
                    "content": content,
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ], 
            model="gpt-3.5-turbo"
        )

        return chat_completion.choices[0].message.content

    def gemini_check_content(self, prompt, text, model_name="gemini-1.5-flash", max_output_tokens=1024, temperature=0.3):  # Adjust max_output_tokens and temp as needed
        """
        Args:
            text: The text to be analyzed.
            model_name: The name of the Gemini model to use (e.g., "gemini-1.5-flash").
            max_output_tokens: The maximum number of tokens in the generated output.
            temperature: Controls randomness of the model output.
        """
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                f"{prompt}. Return just the JSON, do not wrap it in markdown or any other formatting.:{text}",
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=temperature
                )
            )
            if response.text:
                return (response.text).strip()
            else:
                return None
        except Exception as e:
            print(f"Error during analysis: {e}",flush=True)
            logger.error(f"Error during analysis: {e}",exc_info=True)
            return None
