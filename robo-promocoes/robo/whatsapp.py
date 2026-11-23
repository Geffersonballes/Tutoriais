"""Envio para os grupos pela Evolution API (v2)."""
import requests

from . import config


def _headers() -> dict:
    return {"apikey": config.EVOLUTION_API_KEY, "Content-Type": "application/json"}


def enviar_imagem(grupo: str, url_imagem: str, legenda: str) -> dict:
    resp = requests.post(
        f"{config.EVOLUTION_URL}/message/sendMedia/{config.EVOLUTION_INSTANCIA}",
        json={
            "number": grupo,
            "mediatype": "image",
            "mimetype": "image/jpeg",
            "media": url_imagem,
            "fileName": "oferta.jpg",
            "caption": legenda,
        },
        headers=_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def listar_grupos() -> list[dict]:
    resp = requests.get(
        f"{config.EVOLUTION_URL}/group/fetchAllGroups/{config.EVOLUTION_INSTANCIA}",
        params={"getParticipants": "false"},
        headers=_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()
