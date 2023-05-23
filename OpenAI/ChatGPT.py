from fastapi import APIRouter
import openai
import os
from MongoDB.MongoDB import mycol

router = APIRouter(tags=["OpenAI API"])
@router.get("/reviseDB/{ID},{Content}")
async def reviseDB(ID,Content):
    if(Content != ""):
        mycol.update_one({"_id":ID},{"$set":{"rdCondition":Content}})
    for doc in mycol.find():
        print(doc)
#ChatGPT
def chatgpt(str):
    openai.api_key = app_id = os.getenv('OpenAI_Key')
    user = str + "。幫我分類出時間及事件"
    if user:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "我需要用繁體中文輸出"},
                {"role": "user", "content": user},
            ]
        )
        return (response['choices'][0]['message']['content'])