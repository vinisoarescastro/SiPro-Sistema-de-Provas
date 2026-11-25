import os

import pytest


@pytest.fixture
def prova():
    return {
        "titulo": "Prova de Matemática",
        "data": "2026-12-01",
        "turno": "matutino",
        "descricao": "Leia com atenção.",
        "questoes": [
            {
                "enunciado": "Quanto é 2 + 2?",
                "tipo": "multipla-escolha",
                "alternativas": ["3", "4", "", "5"],
            },
            {"enunciado": "A Terra é redonda.", "tipo": "verdadeiro-falso"},
            {"enunciado": "Explique a fotossíntese.", "tipo": "dissertativa"},
        ],
    }


@pytest.fixture
def temporarios(questoes_module, monkeypatch):
    """Registra os PDFs temporários criados para removê-los ao final do teste."""
    criados = []
    original = questoes_module._gerar_pdf

    def _espiao(dados):
        caminho = original(dados)
        criados.append(caminho)
        return caminho

    monkeypatch.setattr(questoes_module, "_gerar_pdf", _espiao)
    yield criados
    for caminho in criados:
        if os.path.exists(caminho):
            os.remove(caminho)


def test_gerar_prova_retorna_pdf_valido(client, prova, temporarios):
    resp = client.post("/gerar-prova", json=prova)

    assert resp.status_code == 200
    assert resp.mimetype == "application/pdf"
    assert resp.data.startswith(b"%PDF")
    assert "prova_de_matem" in resp.headers["Content-Disposition"]


def test_gerar_prova_sem_titulo_usa_nome_padrao(client, temporarios):
    resp = client.post("/gerar-prova", json={"questoes": []})

    assert resp.status_code == 200
    assert "prova.pdf" in resp.headers["Content-Disposition"]


def test_gerar_prova_sem_questoes(client, temporarios):
    resp = client.post("/gerar-prova", json={"titulo": "Vazia", "questoes": []})
    assert resp.status_code == 200
    assert resp.data.startswith(b"%PDF")


def test_gerar_prova_com_muitas_questoes_gera_varias_paginas(client, temporarios):
    questoes = [
        {"enunciado": f"Questão {i}", "tipo": "dissertativa"} for i in range(40)
    ]
    resp = client.post("/gerar-prova", json={"titulo": "Longa", "questoes": questoes})

    assert resp.status_code == 200
    assert resp.data.count(b"/Type /Page\n") > 1


def test_gerar_prova_sem_corpo_retorna_400(client):
    resp = client.post("/gerar-prova", data="x", content_type="application/json")
    assert resp.status_code == 400
    assert resp.get_json() == {"erro": "Payload JSON inválido."}


def test_gerar_prova_erro_interno_retorna_500(client, questoes_module, monkeypatch):
    def _falha(dados):
        raise RuntimeError("boom")

    monkeypatch.setattr(questoes_module, "_gerar_pdf", _falha)

    resp = client.post("/gerar-prova", json={"titulo": "x"})

    assert resp.status_code == 500
    assert resp.get_json() == {"erro": "boom"}
