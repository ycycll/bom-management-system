from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from crud.we import we
from crud.copilot import copilot
from crud.hub import hub
from crud.defog import defog
from crud.agreement import agreement
from crud.draw import draw

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(we)
app.include_router(copilot)
app.include_router(hub)
app.include_router(defog)
app.include_router(agreement)
app.include_router(draw)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8070, reload=True)
