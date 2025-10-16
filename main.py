import threading
import time
import webbrowser
from fastapi import FastAPI
import uvicorn
from app.routes import users, posts, templates

app = FastAPI(title="Блог про селедку", description="API для ведения блога")


app.include_router(users.router)
app.include_router(posts.router)
app.include_router(templates.router)


def open_browser():
    """Открывает браузер после запуска сервера"""
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8001")


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Блог работает!"}


if __name__ == "__main__":

    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )