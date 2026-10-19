# Atividade 05 - AES: confusão, difusão e efeito avalanche

Prática baseada no código `aluno.py` fornecido pelo professor (núcleo do AES-128 em
Python puro, sem dependências).

## O que foi feito
- **Núcleo do AES:** não foi alterado.
- **Parte 1 (já resolvida):** avalanche com AES completo.
- **Parte 2 (TODO 2):** avalanche variando `rounds = 1..10`.
- **Parte 3 (TODO 3):** avalanche com `use_mixcolumns=False` para 2, 4, 6 e 10 rodadas.

## Como executar
Requer Python 3.9+ (nada para instalar).
```bash
python3 -c "import aluno; aluno.validar_fips()"   # confere o núcleo (FIPS-197)
python3 aluno.py                                    # roda os 3 experimentos (~10 s)
```
No Windows use `python` no lugar de `python3`.

## Arquivos
| Arquivo | Conteúdo |
|---|---|
| `aluno.py` | código completo (TODO 2 e 3 resolvidos e comentados) |
| `resultados.txt` | saída de uma execução |
| `relatorio.md` | relatório de 1 página (parágrafos técnico e crítico) |

## Resultados (média de 1500 a 2000 amostras)
- 1 bit no texto ou na chave: **≈ 50%** dos bits do cifrado mudam.
- Por rodada: **3,2% → 12,5% → 50,2%** (satura na 3ª rodada).
- Sem MixColumns: **≈ 3%** (≈ 4 bits), para qualquer número de rodadas.

Como as amostras são aleatórias, os valores variam um pouco entre execuções.
