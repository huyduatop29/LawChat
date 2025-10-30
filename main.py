from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import query

app = FastAPI(title="Chatbot API")

origins = [
    "http://localhost:8501"
]

# Cho phép frontend Streamlit gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mô hình dữ liệu nhận từ frontend
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str


# API chat chính
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    ai_reply = query.reply(request.message)[0][0]
    return ChatResponse(
        response=ai_reply.split("Trả lời:")[-1].strip(),
        timestamp=datetime.now().strftime("%H:%M:%S")
    )

'''
# Chạy server (nếu chạy trực tiếp)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''