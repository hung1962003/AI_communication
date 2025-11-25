from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()  
client1 = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def aiFeedback(message, bilingual=False):
    if bilingual:
        system_message = """You are an expert dialect/accent coach for american spoken english. You will provide valuable feedback to improve my american accent. 
        
IMPORTANT: Provide your feedback in BOTH Vietnamese and English (song ngữ). Structure your response in TWO separate sections:

SECTION 1 - ENGLISH (all English content first):
1. Overall Impression: [English content]
2. Specific Feedback: [English content]
3. Google Pronunciation Respelling Suggestions: [English content]
4. Additional Tips: [English content]

SECTION 2 - VIETNAMESE (all Vietnamese content after):
1. Ấn tượng tổng quan: [Vietnamese content]
2. Phản hồi cụ thể: [Vietnamese content]
3. Gợi ý cách phát âm theo Google: [Vietnamese content]
4. Mẹo bổ sung: [Vietnamese content]

Write ALL English sections first, then write ALL Vietnamese sections. Do NOT mix English and Vietnamese within the same section.

For ease of understanding, use google pronunciation respelling for pronunciation suggestions."""
        user_content = f"""Please provide bilingual feedback (Vietnamese and English) on my spoken english: {message}"""
    else:
        system_message = """You are an expert dialect/accent coach for american spoken english. you will provide valuable feedback to improve my american accent. For ease of understanding, I would prefer you give suggestions for mipronunciation using google pronunciation respelling.
    provide following Overall Impression, Specific Feedback, Google Pronunciation Respelling Suggestions, additional tips"""
        user_content = f"""Please provide feedback on my spoken english: {message}"""
    
    chat_completion = client1.chat.completions.create(
        messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_content,
                }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    feedback = chat_completion.choices[0].message.content
    return feedback