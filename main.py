from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def health():
    return {"Status" : "200 OK"}


if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8089,reload=True)

