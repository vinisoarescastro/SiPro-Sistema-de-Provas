import pytest


def test_payload_me_valido_nao_gera_erros(questoes_module, payload_me):
    assert questoes_module._validate(payload_me) == []


def test_payload_vf_valido_nao_gera_erros(questoes_module, payload_vf):
    assert questoes_module._validate(payload_vf) == []


@pytest.mark.parametrize("enunciado", ["", "   "])
def test_enunciado_vazio_ou_so_espacos(questoes_module, payload_me, enunciado):
    payload_me["enunciado"] = enunciado
    assert "O enunciado é obrigatório." in questoes_module._validate(payload_me)


def test_enunciado_ausente(questoes_module, payload_me):
    del payload_me["enunciado"]
    assert "O enunciado é obrigatório." in questoes_module._validate(payload_me)


@pytest.mark.parametrize("tipo", [None, "", "dissertativa", "multipla-escolha"])
def test_tipo_invalido(questoes_module, payload_me, tipo):
    payload_me["tipo"] = tipo
    erros = questoes_module._validate(payload_me)
    assert "Tipo deve ser 'multipla_escolha' ou 'verdadeiro_falso'." in erros


@pytest.mark.parametrize("qtd", [0, 1, 6])
def test_me_quantidade_de_alternativas_fora_do_intervalo(questoes_module, payload_me, qtd):
    payload_me["alternativas"] = [{"texto": str(i)} for i in range(qtd)]
    payload_me["gabarito"] = 0
    erros = questoes_module._validate(payload_me)
    assert "Múltipla escolha requer entre 2 e 5 alternativas." in erros


@pytest.mark.parametrize("qtd", [2, 5])
def test_me_limites_de_alternativas_sao_validos(questoes_module, payload_me, qtd):
    payload_me["alternativas"] = [{"texto": str(i)} for i in range(qtd)]
    payload_me["gabarito"] = 0
    assert questoes_module._validate(payload_me) == []


def test_me_alternativa_vazia_indica_posicao(questoes_module, payload_me):
    payload_me["alternativas"][2] = {"texto": "  "}
    assert "Alternativa 3 não pode ser vazia." in questoes_module._validate(payload_me)


@pytest.mark.parametrize("gabarito", [None, -1, 3, "1"])
def test_me_gabarito_fora_das_alternativas(questoes_module, payload_me, gabarito):
    payload_me["gabarito"] = gabarito
    erros = questoes_module._validate(payload_me)
    assert "Gabarito deve ser o índice de uma alternativa válida." in erros


@pytest.mark.parametrize("gabarito", [None, "true", "sim"])
def test_vf_gabarito_deve_ser_booleano(questoes_module, payload_vf, gabarito):
    payload_vf["gabarito"] = gabarito
    erros = questoes_module._validate(payload_vf)
    assert "Gabarito para verdadeiro/falso deve ser true ou false." in erros


@pytest.mark.parametrize("gabarito", [True, False])
def test_vf_gabarito_booleano_e_valido(questoes_module, payload_vf, gabarito):
    payload_vf["gabarito"] = gabarito
    assert questoes_module._validate(payload_vf) == []


@pytest.mark.parametrize("disciplina", ["", "  "])
def test_disciplina_obrigatoria(questoes_module, payload_me, disciplina):
    payload_me["disciplina"] = disciplina
    assert "A disciplina é obrigatória." in questoes_module._validate(payload_me)


def test_acumula_multiplos_erros(questoes_module):
    erros = questoes_module._validate({})
    assert "O enunciado é obrigatório." in erros
    assert "A disciplina é obrigatória." in erros
    assert any(e.startswith("Tipo deve ser") for e in erros)
