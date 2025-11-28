from fastapi import FastAPI
import uvicorn

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth


"""
Main entry point for the FastAPI application.

This module initializes the FastAPI application, includes the necessary routers,
and runs the Uvicorn server for development purposes.
"""

# Создаем экземпляр приложения FastAPI
app = FastAPI()
"""FastAPI application instance.

This is the main entry point for the API, which handles routing and request processing.
"""


app.include_router(router_auth)
app.include_router(router_hotels)
"""Include the hotels router.

Adds all routes defined in the hotels API router to the main application.
These routes are accessible under the prefix defined in the router (e.g., /hotels).
"""


# Запуск сервера Uvicorn для запуска API
if __name__ == "__main__":
    """
    Run the application using Uvicorn server.

    This block executes only when the script is run directly (not imported).
    It starts the Uvicorn server with the following configuration:
    - Host: 127.0.0.1 (localhost)
    - Port: 8080
    - Reload: True (auto-reload on code changes, useful for development)

    The app is referenced as "main:app" where:
    - "main" is the module name (main.py)
    - "app" is the FastAPI instance name
    """
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)


"""
Если плохо работает документация OpenAPI.

from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

"""