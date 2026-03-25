from fastapi import FastAPI
from models import Eval,Response

import uvicorn

app = FastAPI()

@app.get("/")
def health():
    return {"Status" : "200 OK"}

@app.post("/evaluate",response_model=Response)
def evaluate(e:Eval):
    pass

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8089,reload=True)

