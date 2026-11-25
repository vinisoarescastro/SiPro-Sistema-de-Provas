import json

import pytest


def test_load_sem_arquivo_retorna_lista_vazia(questoes_module, data_file):
    assert not data_file.exists()
    assert questoes_module._load() == []


def test_save_e_load_preservam_acentos(questoes_module, data_file):
    dados = [{"id": "1", "enunciado": "Educação física: não é só correr"}]
    questoes_module._save(dados)
    assert questoes_module._load() == dados
    # ensure_ascii=False: acentos legíveis no arquivo
    assert "Educação" in data_file.read_text(encoding="utf-8")


def test_load_arquivo_corrompido_levanta_erro(questoes_module, data_file):
    # Documenta o comportamento atual: JSON inválido propaga JSONDecodeError
    # (a API responderia 500). Se for tratado no futuro, ajustar este teste.
    data_file.write_text("{ não é json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        questoes_module._load()
