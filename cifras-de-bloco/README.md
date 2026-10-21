# Atividade 06 - Modos de operação de cifra de blocos (OpenSSL + Tux) e Sweet32

## Arquivos
| Arquivo | Para que serve |
|---|---|
| `executar_pratica.sh` | Roda toda a prática (chave, IV, Tux em ECB/CBC/CFB/OFB/CTR) e mostra cada comando |
| `imagem.py` | Conversões PNG↔PPM, contagem de blocos repetidos e montagem comparativa (usa Pillow) |

## Requisitos
- `openssl`, `curl`, Python 3 com Pillow (`pip install pillow`)
- No Windows: **Git Bash** (já vem com o Git) ou WSL. No Linux, já funciona direto.
  (Ubuntu/Debian: `sudo apt install openssl curl python3-pil`)

## Como executar
```bash
cd cifras-de-bloco
bash executar_pratica.sh
```
O script cria `key.priv`, `iv.txt`, os arquivos `.enc` e a pasta `saida/` com as imagens
em PNG (inclusive `saida/comparacao.png`, que junta o original e os cinco modos).


Observação: `key.priv` e `iv.txt` são chaves de teste da prática; não reutilize em nada real.
