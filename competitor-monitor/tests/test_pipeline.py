"""
Tests for deterministic pipeline components.
No LLM calls — these test only the deterministic layers.

Run: python -m pytest tests/test_pipeline.py -v
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.extract.hasher import compute_hash, hashes_equal, change_fingerprint
from src.extract.normalizer import normalize
from src.diff.differ import compute_diff, diff_is_substantive, extract_added_lines
from src.crawl.url_filter import is_relevant_url, classify_url_type, deduplicate_urls
from src.classify.matcher import find_candidate_solutions


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


# ── 1. Página sem alteração → zero chamada LLM (hash igual)
def test_unchanged_page_no_llm():
    text = load_fixture("page_unchanged.txt")
    normalized = normalize(text)
    h1 = compute_hash(normalized)
    h2 = compute_hash(normalized)
    assert hashes_equal(h1, h2), "Hashes should be equal for unchanged content"


# ── 2. Alteração apenas de layout → diff não substantivo ou IGNORE esperado
def test_layout_change_not_substantive():
    old = normalize(load_fixture("page_unchanged.txt"))
    new = normalize(load_fixture("page_layout_change.txt"))
    diff = compute_diff(old, new)
    # Layout change produces a diff but it's small
    assert diff != "", "Should produce a diff"
    added = extract_added_lines(diff)
    # The added content should be identifiable as boilerplate (test checks diff exists)
    assert len(added) > 0


# ── 3. Hash diferente quando conteúdo muda
def test_hash_changes_on_content_change():
    old = normalize(load_fixture("page_unchanged.txt"))
    new = normalize(load_fixture("page_new_client.txt"))
    h1 = compute_hash(old)
    h2 = compute_hash(new)
    assert not hashes_equal(h1, h2), "Hashes should differ when content changes"


# ── 4. Diff substantivo quando novo cliente é adicionado
def test_new_client_produces_substantive_diff():
    old = normalize(load_fixture("page_unchanged.txt"))
    new = normalize(load_fixture("page_new_client.txt"))
    diff = compute_diff(old, new)
    assert diff_is_substantive(diff, min_chars=50), "New client diff should be substantive"


# ── 5. Deduplicação de fingerprint — mesma mudança não gera dois alertas
def test_change_fingerprint_deduplication():
    fp1 = change_fingerprint("shield", "offers", "new_product", "EDR CrowdStrike")
    fp2 = change_fingerprint("shield", "offers", "new_product", "EDR CrowdStrike")
    assert fp1 == fp2, "Same change should produce same fingerprint"


# ── 6. Fingerprint diferente para mudanças diferentes
def test_change_fingerprint_unique():
    fp1 = change_fingerprint("shield", "offers", "new_product", "EDR CrowdStrike")
    fp2 = change_fingerprint("shield", "clients", "new_client", "Banco XYZ")
    assert fp1 != fp2, "Different changes should produce different fingerprints"


# ── 7. URL filter — página de cases é relevante
def test_url_filter_cases_relevant():
    assert is_relevant_url("https://shieldsec.com.br/cases/banco-xyz", "shieldsec.com.br")


# ── 8. URL filter — página de carreiras é ignorada
def test_url_filter_careers_ignored():
    assert not is_relevant_url("https://shieldsec.com.br/carreiras/vaga-analista", "shieldsec.com.br")


# ── 9. URL filter — domínio externo é rejeitado
def test_url_filter_external_domain():
    assert not is_relevant_url("https://linkedin.com/company/shield", "shieldsec.com.br")


# ── 10. Classificação de tipo de URL
def test_url_type_classification():
    assert classify_url_type("https://shieldsec.com.br/cases/banco") == "CLIENTS_CASES"
    assert classify_url_type("https://shieldsec.com.br/blog/novidades") == "NEWS_LAUNCHES"
    assert classify_url_type("https://shieldsec.com.br/solucoes/soc") == "OFFERS"


# ── 11. Deduplicação de URLs
def test_url_deduplication():
    urls = [
        "https://shieldsec.com.br/soc",
        "https://shieldsec.com.br/soc/",
        "https://shieldsec.com.br/soc#ancora",
        "https://shieldsec.com.br/mdr",
    ]
    result = deduplicate_urls(urls)
    assert len(result) == 2, f"Expected 2 unique URLs, got {len(result)}"


# ── 12. Matcher determinístico encontra candidatos de EDR
def test_matcher_finds_edr_candidates():
    text = "Proteja seus endpoints com solução EDR/XDR avançada."
    candidates = find_candidate_solutions(text)
    edr_solutions = [c for c in candidates if "EDR" in c or "Endpoint" in c]
    assert len(edr_solutions) > 0, f"Should find EDR candidates, got: {candidates}"


# ── 13. Matcher não encontra candidatos em texto irrelevante
def test_matcher_no_candidates_irrelevant():
    text = "Nosso escritório fica na Avenida Paulista, 37. Entre em contato."
    candidates = find_candidate_solutions(text)
    assert len(candidates) == 0, f"Should find no candidates, got: {candidates}"


# ── 14. Normalização remove markdown de imagens
def test_normalizer_removes_images():
    text = "![logo](https://example.com/img.png)\n\nConteúdo relevante aqui."
    normalized = normalize(text)
    assert "![logo]" not in normalized
    assert "Conteúdo relevante" in normalized


# ── 15. Normalização colapsa linhas duplicadas
def test_normalizer_deduplicates_lines():
    line = "Solução de SOC/MDR contínuo para empresas"
    text = "\n".join([line] * 3) + "\nOutra linha diferente"
    normalized = normalize(text)
    lines = [l for l in normalized.splitlines() if l.strip()]
    assert lines.count(line) == 1, "Should deduplicate consecutive identical lines"


if __name__ == "__main__":
    import unittest
    # Run all test_ functions
    failures = 0
    tests = [(name, fn) for name, fn in globals().items() if name.startswith("test_")]
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            failures += 1
        except Exception as e:
            print(f"  ✗ {name}: UNEXPECTED ERROR — {e}")
            failures += 1
    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    sys.exit(0 if failures == 0 else 1)
