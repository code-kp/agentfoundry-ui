from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.staticfiles import StaticFiles


def packaged_ui_dist() -> Path | None:
    with as_file(files("agent_foundry_ui")) as package_root:
        dist = Path(package_root) / "dist"
        if dist.is_dir():
            return dist
    return None


class SinglePageAppFiles(StaticFiles):
    def __init__(self, directory: str | Path) -> None:
        super().__init__(directory=str(directory), html=True)

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code != 404:
            return response

        request = Request(scope)
        if request.url.path.startswith("/api/"):
            raise HTTPException(status_code=404)
        return await super().get_response("index.html", scope)


def mount_ui(app: FastAPI, *, path: str = "/", name: str = "web") -> None:
    dist = packaged_ui_dist()
    if dist is None:
        raise RuntimeError(
            "agentfoundry-ui does not include a packaged frontend build. "
            "Run `npm install && npm run build` in the agentfoundry-ui repo before publishing."
        )
    app.mount(path, SinglePageAppFiles(dist), name=name)
