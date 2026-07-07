import uvicorn
import sys

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        reload_delay=0.5,  # Espera medio segundo antes de recargar
        log_level="info",
        use_colors=True
    )