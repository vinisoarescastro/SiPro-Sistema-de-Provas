import json


def _ler(data_file):
    return json.loads(data_file.read_text(encoding="utf-8"))


# ── POST /questoes ────────────────────────────────────────────

def test_cadastrar_me_retorna_201_e_persiste(client, data_file, payload_me):
    resp = client.post("/questoes", json=payload_me)

    assert resp.status_code == 201
    corpo = resp.get_json()
    assert corpo["id"]
    assert corpo["enunciado"] == "Quanto é 2 + 2?"
    assert corpo["nivel"] == "facil"
    assert _ler(data_file) == [corpo]


def test_cadastrar_aplica_trim_e_nivel_padrao(client, payload_vf):
    payload_vf["enunciado"] = "  A Terra é redonda.  "
    payload_vf["disciplina"] = "  Geografia "

    corpo = client.post("/questoes", json=payload_vf).get_json()

    assert corpo["enunciado"] == "A Terra é redonda."
    assert corpo["disciplina"] == "Geografia"
    assert corpo["nivel"] == "medio"
    assert corpo["alternativas"] == []


def test_cadastrar_gera_ids_unicos(client, payload_me):
    id1 = client.post("/questoes", json=payload_me).get_json()["id"]
    id2 = client.post("/questoes", json=payload_me).get_json()["id"]
    assert id1 != id2


def test_cadastrar_payload_invalido_retorna_422_sem_persistir(client, data_file, payload_me):
    payload_me["enunciado"] = ""

    resp = client.post("/questoes", json=payload_me)

    assert resp.status_code == 422
    assert "O enunciado é obrigatório." in resp.get_json()["erros"]
    assert not data_file.exists()


def test_cadastrar_sem_corpo_json_retorna_400(client):
    resp = client.post("/questoes", data="isto não é json", content_type="application/json")
    assert resp.status_code == 400
    assert resp.get_json() == {"erro": "Payload JSON inválido."}


def test_cadastrar_objeto_vazio_retorna_400(client):
    assert client.post("/questoes", json={}).status_code == 400


# ── GET /questoes ─────────────────────────────────────────────

def test_listar_vazio(client):
    resp = client.get("/questoes")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_listar_retorna_todas(client, payload_me, payload_vf):
    client.post("/questoes", json=payload_me)
    client.post("/questoes", json=payload_vf)
    assert len(client.get("/questoes").get_json()) == 2


def test_listar_filtra_por_disciplina_sem_diferenciar_caixa(client, payload_me, payload_vf):
    client.post("/questoes", json=payload_me)
    client.post("/questoes", json=payload_vf)

    resp = client.get("/questoes?disciplina=matemática")

    assert [q["disciplina"] for q in resp.get_json()] == ["Matemática"]


def test_listar_filtra_por_tipo(client, payload_me, payload_vf):
    client.post("/questoes", json=payload_me)
    client.post("/questoes", json=payload_vf)

    resp = client.get("/questoes?tipo=verdadeiro_falso")

    assert [q["tipo"] for q in resp.get_json()] == ["verdadeiro_falso"]


def test_listar_combina_filtros(client, payload_me, payload_vf):
    client.post("/questoes", json=payload_me)
    client.post("/questoes", json=payload_vf)
    assert client.get("/questoes?disciplina=Matemática&tipo=verdadeiro_falso").get_json() == []


# ── GET /questoes/<id> ────────────────────────────────────────

def test_buscar_existente(client, payload_me):
    criada = client.post("/questoes", json=payload_me).get_json()
    resp = client.get(f"/questoes/{criada['id']}")
    assert resp.status_code == 200
    assert resp.get_json() == criada


def test_buscar_inexistente_retorna_404(client):
    resp = client.get("/questoes/nao-existe")
    assert resp.status_code == 404
    assert resp.get_json() == {"erro": "Questão não encontrada."}


# ── PUT /questoes/<id> ────────────────────────────────────────

def test_editar_atualiza_e_preserva_id(client, data_file, payload_me):
    criada = client.post("/questoes", json=payload_me).get_json()
    payload_me["enunciado"] = "Quanto é 3 + 3?"
    payload_me["gabarito"] = 2

    resp = client.put(f"/questoes/{criada['id']}", json=payload_me)

    assert resp.status_code == 200
    corpo = resp.get_json()
    assert corpo["id"] == criada["id"]
    assert corpo["enunciado"] == "Quanto é 3 + 3?"
    assert corpo["gabarito"] == 2
    assert _ler(data_file) == [corpo]


def test_editar_inexistente_retorna_404(client, payload_me):
    assert client.put("/questoes/nao-existe", json=payload_me).status_code == 404


def test_editar_payload_invalido_retorna_422_e_nao_altera(client, data_file, payload_me):
    criada = client.post("/questoes", json=payload_me).get_json()
    payload_me["disciplina"] = ""

    resp = client.put(f"/questoes/{criada['id']}", json=payload_me)

    assert resp.status_code == 422
    assert _ler(data_file) == [criada]


def test_editar_sem_corpo_retorna_400(client, payload_me):
    criada = client.post("/questoes", json=payload_me).get_json()
    resp = client.put(f"/questoes/{criada['id']}", data="x", content_type="application/json")
    assert resp.status_code == 400


# ── DELETE /questoes/<id> ─────────────────────────────────────

def test_excluir_remove_somente_a_questao_alvo(client, data_file, payload_me, payload_vf):
    alvo = client.post("/questoes", json=payload_me).get_json()
    outra = client.post("/questoes", json=payload_vf).get_json()

    resp = client.delete(f"/questoes/{alvo['id']}")

    assert resp.status_code == 200
    assert _ler(data_file) == [outra]
    assert client.get(f"/questoes/{alvo['id']}").status_code == 404


def test_excluir_inexistente_retorna_404(client, data_file, seed):
    seed([{"id": "a", "disciplina": "X", "tipo": "verdadeiro_falso"}])
    assert client.delete("/questoes/b").status_code == 404
    assert len(_ler(data_file)) == 1


def test_ciclo_completo_crud(client, payload_me):
    criada = client.post("/questoes", json=payload_me).get_json()
    qid = criada["id"]
    assert client.get(f"/questoes/{qid}").status_code == 200
    payload_me["enunciado"] = "Atualizada"
    assert client.put(f"/questoes/{qid}", json=payload_me).status_code == 200
    assert client.get(f"/questoes/{qid}").get_json()["enunciado"] == "Atualizada"
    assert client.delete(f"/questoes/{qid}").status_code == 200
    assert client.get("/questoes").get_json() == []
