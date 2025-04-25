import requests
import json

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un assistant marketing spécialisé dans la rédaction de contenu pour campagnes SMS."
            },
            {
                "role": "user",
                "content": "Proposez un contenu pour une campagne marketing."
            }
        ],
        "max_tokens": 500
    }
)

print(response.status_code)
print(response.json())