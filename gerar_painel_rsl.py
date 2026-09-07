#!/usr/bin/env python3
"""
Gerador do painel HTML de obtencao de textos completos para RSL/meta-analise.

Implementa a parte automatizavel do prompt Prompt_PAINEL_Obtencao_Textos_RSL_
Metaanalise.md: le uma lista de referencias (CSV com pelo menos titulo e DOI),
deduplica por DOI normalizado e por titulo normalizado, e monta um painel HTML
autocontido com cartoes, filtros e persistencia de marcacao em localStorage.

A deteccao de acesso aberto (Unpaywall/OpenAlex) e a verificacao de anexos em
gerenciador de referencias, descritas no prompt original, nao estao
implementadas aqui (exigem chamadas de rede/credenciais); ficam como pontos de
extensao em buscar_acesso_aberto().

Uso:
    python gerar_painel_rsl.py referencias.csv
"""
from __future__ import annotations

import csv
import html
import json
import re
import sys
import unicodedata


def norm_doi(doi: str) -> str:
    return (doi or "").strip().lower().replace("https://doi.org/", "").rstrip(".")


def norm_titulo(titulo: str) -> str:
    t = unicodedata.normalize("NFKD", titulo or "").encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9 ]", "", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def carregar_referencias(caminho_csv: str) -> list[dict]:
    with open(caminho_csv, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def deduplicar(refs: list[dict]) -> list[dict]:
    vistos_doi, vistos_titulo, unicos = set(), set(), []
    for r in refs:
        doi = norm_doi(r.get("doi", ""))
        titulo = norm_titulo(r.get("titulo") or r.get("title", ""))
        if doi and doi in vistos_doi:
            continue
        if not doi and titulo in vistos_titulo:
            continue
        if doi:
            vistos_doi.add(doi)
        vistos_titulo.add(titulo)
        unicos.append(r)
    return unicos


def buscar_acesso_aberto(doi: str) -> str:
    """Ponto de extensao: consultar Unpaywall/OpenAlex pelo DOI.
    Sem chamada de rede aqui; retorna 'desconhecido' por padrao."""
    return "desconhecido"


def render_card(rec_id: str, r: dict) -> str:
    titulo = html.escape(r.get("titulo") or r.get("title", "Sem título"))
    autores = html.escape(r.get("autores") or r.get("authors", ""))
    ano = html.escape(str(r.get("ano") or r.get("year", "")))
    periodico = html.escape(r.get("periodico") or r.get("journal", ""))
    doi = html.escape(r.get("doi", ""))
    oa = buscar_acesso_aberto(doi)
    link_doi = f"https://doi.org/{doi}" if doi else "#"
    link_scholar = f"https://scholar.google.com/scholar?q={html.escape(titulo)}"
    return f"""
      <div class="card" data-id="{rec_id}" data-oa="{oa}" data-status="pendente">
        <div class="card-id">{rec_id}</div>
        <div class="card-title">{titulo}</div>
        <div class="card-meta">{autores} ({ano}) — <i>{periodico}</i></div>
        <div class="card-doi">{doi}</div>
        <div class="card-actions">
          <a class="btn-primary" href="{link_doi}" target="_blank" rel="noopener">Abrir pelo DOI</a>
          <a class="btn-secondary" href="{link_scholar}" target="_blank" rel="noopener">Buscar no Scholar</a>
          <label><input type="checkbox" class="marcar-obtido"> obtido</label>
        </div>
      </div>"""


def montar_html(cards_html: str, total: int) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel de Obtenção de Textos Completos</title>
<style>
  :root{{--bg:#faf8f5; --panel:#fff; --border:#ddd6cc; --text:#2a2620; --muted:#7a7266; --accent:#3d6b52;}}
  *{{box-sizing:border-box;}}
  body{{margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
    background:var(--bg); color:var(--text); line-height:1.5;}}
  header{{padding:20px 24px; background:var(--panel); border-bottom:1px solid var(--border); position:sticky; top:0;}}
  h1{{margin:0 0 6px; font-size:1.4rem;}}
  #progresso{{color:var(--muted); font-size:0.9rem;}}
  main{{max-width:1000px; margin:0 auto; padding:20px;}}
  input#busca{{width:100%; padding:8px 12px; margin-bottom:16px; border:1px solid var(--border); border-radius:8px;}}
  .card{{background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:14px 16px; margin-bottom:10px;}}
  .card-id{{font-family:monospace; font-size:0.75rem; color:var(--muted);}}
  .card-title{{font-weight:650; margin:4px 0;}}
  .card-meta{{font-size:0.85rem; color:var(--muted);}}
  .card-doi{{font-family:monospace; font-size:0.78rem; margin:6px 0;}}
  .card-actions{{display:flex; gap:10px; align-items:center; margin-top:8px;}}
  .btn-primary,.btn-secondary{{font-size:0.82rem; padding:5px 10px; border-radius:6px; text-decoration:none;}}
  .btn-primary{{background:var(--accent); color:#fff;}}
  .btn-secondary{{border:1px solid var(--border); color:var(--text);}}
  .card.obtido{{opacity:0.55;}}
</style>
</head>
<body>
<header>
  <h1>Painel de Obtenção de Textos Completos</h1>
  <div id="progresso">0 de {total} obtidos</div>
</header>
<main>
  <input id="busca" placeholder="Buscar por título, autor, DOI...">
  <div id="lista">{cards_html}
  </div>
</main>
<script>
(function(){{
  var STORE_KEY = 'painel_rsl_obtidos';
  function carregar(){{ try {{ return JSON.parse(localStorage.getItem(STORE_KEY) || '{{}}'); }} catch(e) {{ return {{}}; }} }}
  function salvar(obj){{ try {{ localStorage.setItem(STORE_KEY, JSON.stringify(obj)); }} catch(e) {{}} }}
  var estado = carregar();
  var cards = document.querySelectorAll('.card');
  function atualizarProgresso(){{
    var obtidos = document.querySelectorAll('.card.obtido').length;
    document.getElementById('progresso').textContent = obtidos + ' de ' + cards.length + ' obtidos';
  }}
  cards.forEach(function(c){{
    var id = c.dataset.id;
    var chk = c.querySelector('.marcar-obtido');
    if (estado[id]) {{ c.classList.add('obtido'); chk.checked = true; }}
    chk.addEventListener('change', function(){{
      estado[id] = chk.checked;
      c.classList.toggle('obtido', chk.checked);
      salvar(estado);
      atualizarProgresso();
    }});
  }});
  atualizarProgresso();
  document.getElementById('busca').addEventListener('input', function(e){{
    var q = e.target.value.toLowerCase();
    cards.forEach(function(c){{ c.style.display = c.textContent.toLowerCase().includes(q) ? '' : 'none'; }});
  }});
}})();
</script>
</body>
</html>"""


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python gerar_painel_rsl.py referencias.csv")
        sys.exit(1)
    refs = deduplicar(carregar_referencias(sys.argv[1]))
    cards = "\n".join(render_card(f"REC{idx+1:04d}", r) for idx, r in enumerate(refs))
    pagina = montar_html(cards, len(refs))
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(pagina)
    print(f"index.html gerado com {len(refs)} referências únicas.")


if __name__ == "__main__":
    main()
