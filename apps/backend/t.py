import os
import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    "https://api.cohere.com/v2/rerank",
    headers={
        "Authorization": f"Bearer {os.environ['COHERE_API_KEY']}",
        "Content-Type": "application/json",
        "X-Client-Name": "ai-study-platform",
    },
    json={
        "model": "rerank-v4.0-pro",
        "query": "ما هو دور الذكاء الاصطناعي في التعليم؟",
        "documents": [
            "يساعد الذكاء الاصطناعي الطلاب على تخصيص تجربة التعلم.",
            "تستخدم السيارات محركات كهربائية أو محركات احتراق.",
            "يمكن للمنصات التعليمية إنشاء اختبارات وتلخيص المستندات.",
        ],
        "top_n": 2,
    },
    timeout=20,
)

response.raise_for_status()
print(response.json())