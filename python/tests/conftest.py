import importlib.util
import json
import os

import pytest

QUESTOES_APP = os.path.join(os.path.dirname(__file__), "..", "questoes", "app.py")


@pytest.fixture(scope="session")
def questoes_module():
    """Carrega python/questoes/app.py por caminho (existem dois módulos `app`)."""
    spec = importlib.util.spec_from_file_location("sipro_questoes_app", QUESTOES_APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def data_file(questoes_module, tmp_path, monkeypatch):
    """Aponta DATA_FILE para um arquivo temporário: nunca toca em questoes.json real."""
    path = tmp_path / "questoes.json"
    monkeypatch.setattr(questoes_module, "DATA_FILE", str(path))
    return path


@pytest.fixture
def client(questoes_module, data_file):
    questoes_module.app.config["TESTING"] = True
    return questoes_module.app.test_client()


@pytest.fixture
def seed(data_file):
    def _seed(questoes):
        data_file.write_text(json.dumps(questoes), encoding="utf-8")

    return _seed


@pytest.fixture
def payload_me():
    return {
        "enunciado": "Quanto é 2 + 2?",
        "tipo": "multipla_escolha",
        "alternativas": [{"texto": "3"}, {"texto": "4"}, {"texto": "5"}],
        "gabarito": 1,
        "disciplina": "Matemática",
        "nivel": "facil",
    }


@pytest.fixture
def payload_vf():
    return {
        "enunciado": "A Terra é redonda.",
        "tipo": "verdadeiro_falso",
        "gabarito": True,
        "disciplina": "Geografia",
    }
