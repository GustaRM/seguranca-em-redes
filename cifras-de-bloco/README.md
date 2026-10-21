# Atividade 06 - Modos de operação de cifra de blocos (OpenSSL + Tux) e Sweet32

## Arquivos
| Arquivo | Para que serve |
|---|---|
| `executar_pratica.sh` | Roda toda a prática (chave, IV, Tux em ECB/CBC/CFB/OFB/CTR) e mostra cada comando |
| `imagem.py` | Conversões PNG↔PPM, contagem de blocos repetidos e montagem comparativa (usa Pillow) |
| `explicacao_resultados.md` | Texto da explicação dos resultados (item 1 do PDF) |
| `sweet32.md` | Texto de 3 parágrafos sobre o Sweet32 (item 2) |

## Requisitos
- `openssl`, `curl`, Python 3 com Pillow (`pip install pillow`)
- No Windows: **Git Bash** (já vem com o Git) ou WSL. No Linux, já funciona direto.
  (Ubuntu/Debian: `sudo apt install openssl curl python3-pil`)

## Como executar
```bash
cd 06-modos-de-operacao
bash executar_pratica.sh
```
O script cria `key.priv`, `iv.txt`, os arquivos `.enc` e a pasta `saida/` com as imagens
em PNG (inclusive `saida/comparacao.png`, que junta o original e os cinco modos).

Se o download do Tux falhar, baixe `https://upload.wikimedia.org/wikipedia/commons/a/af/Tux.png`,
salve como `Tux.png` nesta pasta e rode o script de novo.

## Montando o PDF da entrega
1. Rode o script e tire **prints do terminal** de cada seção (os títulos `=== N. ... ===` ajudam).
2. Cole no documento: os prints, `saida/comparacao.png` e o texto de `explicacao_resultados.md`
   (troque os campos `[seu número]` pelos valores do seu terminal).
3. Exporte para PDF (no Google Docs: Arquivo > Fazer download > PDF).
4. O texto do Sweet32 (`sweet32.md`) vai como segundo item da entrega.

Observação: `key.priv` e `iv.txt` são chaves de teste da prática; não reutilize em nada real.
