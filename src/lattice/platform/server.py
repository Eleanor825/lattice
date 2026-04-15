from __future__ import annotations

from fastapi import FastAPI

from lattice.platform.registry import PlatformRegistry


def create_app(db_path: str) -> FastAPI:
    registry = PlatformRegistry(db_path)
    app = FastAPI(title="Lattice Platform API", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"ok": True}

    @app.get("/runs")
    def runs() -> list[dict[str, object]]:
        return registry.list_runs()

    @app.get("/datasets")
    def datasets() -> list[dict[str, object]]:
        return registry.list_datasets()

    @app.get("/backends")
    def backends() -> list[dict[str, object]]:
        return registry.list_backends()

    return app
