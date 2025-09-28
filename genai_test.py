import google.generativeai as genai

genai.configure(api_key="AIzaSyBdH6MgBBQzUJ4d6vit4_srGwYpw-Z8Cco")

model = genai.GenerativeModel(model_name="gemini-pro")
response = model.generate_content("Explain AI like I'm 5")
print(response.text)
