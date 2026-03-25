from fastapi import FastAPI

import uvicorn

from eval import get_eval
from models import Eval, Response

app = FastAPI()


@app.get("/")
def health():
    return {"Status": "200 OK"}


@app.post("/evaluate", response_model=Response)
def evaluate(e: Eval) -> Response:
    out = get_eval().evaluation(
        e.api_url,
        e.model_name,
        use_structured_output=e.use_structured_output,
    )
    return Response(**out)

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8089)

