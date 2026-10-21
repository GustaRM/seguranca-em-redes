# Atividade 09 - Hash

## Como executar
Só precisa de Python 3 (biblioteca padrão).
```bash
python3 sha256_passo_a_passo.py            # SHA-256 de "abc" passo a passo
python3 sha256_passo_a_passo.py "texto"    # ou de outro texto
python3 hash_simples.py                    # hash simples + testes de fraqueza
```
No Windows use `python` no lugar de `python3`.

## Item 3: como o hash simples funciona
1. `hash_xor`: divide a mensagem em blocos de 4 bytes (completando com zeros) e faz XOR de todos.
2. `hash_xor_rot`: começa com um valor inicial, e para cada bloco faz `h = rotl(h XOR bloco, 5)`;
   no fim faz XOR com o tamanho da mensagem e gira mais uma vez.

### Por que não são seguros (resultados do programa)
| Teste | hash_xor | hash_xor_rot | SHA-256 |
|---|---|---|---|
| Bits da saída que mudam ao trocar 1 bit da entrada | 3,1% | 3,1% | 50,0% |
| Colisão | trocar a ordem dos blocos (`AAAABBBB` e `BBBBAAAA`) | construída por álgebra (tudo é linear) | - |
| Colisão por força bruta | - | 63308 tentativas (esperado ~2^16) | inviável |

O XOR e a rotação são operações lineares: não existe a não linearidade (como o Ch/Maj do SHA-256) que
faz uma pequena mudança virar uma mudança enorme. Além disso, 32 bits de saída já permitem achar colisões
em ~65 mil tentativas pelo paradoxo do aniversário (o mesmo princípio do Sweet32).
