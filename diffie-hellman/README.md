# Atividade 08 - Diffie-Hellman (DH)

Implementação do Diffie-Hellman em Python (só biblioteca padrão), com:
- exemplo pequeno (p = 23) para conferir a lógica,
- ataque de força bruta da "Eve" ao p pequeno,
- exemplo com **primo de 256 bits**.

## Como executar
```bash
python3 dh.py            # roda os 3 exemplos
python3 dh.py --novo-p   # gera outro primo seguro de 256 bits e sua raiz primitiva
```

## Valores - Exemplo 1 (p = 23, o clássico da Wikipédia)
| Variável | Valor |
|---|---|
| p | 23 |
| g | 5 (raízes primitivas de 23: 5, 7, 10, 11, 14, 15, 17, 19, 20, 21) |
| a | 6 |
| b | 15 |
| A = g^a mod p | 8 |
| B = g^b mod p | 19 |
| s = B^a mod p = A^b mod p | 2 |

## Valores - Exemplo 3 (p grande, 256 bits / 77 dígitos)
| Variável | Valor |
|---|---|
| **p** | 91968614663333001359732462613504843415210995925369141928228899021272355533083 |
| **g** | 2 |
| **a** | 43375646396213544966052051347786005282075117287134079075646793577096902219365 |
| **b** | 72928476973422965632467730146431736394074046644765371786922567414218744169654 |
| **A** = g^a mod p | 13531072344222705938777338325444321949939486744242670040065727483090656191869 |
| **B** = g^b mod p | 4667595600160001363392047540916941463051393308993904313655869168641813273128 |
| **s** = B^a mod p = A^b mod p | 30971890797004383508508536366312361277827704220708676383934223006263195304900 |

## Como escolhi p e g
- **p**: primo "seguro", ou seja, p = 2q + 1 com q também primo. Gerei com Miller-Rabin
  e conferi que p e (p-1)/2 são primos. Assim, p - 1 = 2·q só tem dois fatores primos, o que facilita achar a raiz primitiva.
- **g**: raiz primitiva módulo p. g é raiz primitiva se g^((p-1)/f) ≠ 1 (mod p) para todo
  fator primo f de p-1. O código testa g = 2, 3, 4... até achar; para este p, o g = 2 já funcionou.
  Conferi também que g^((p-1)/2) = p - 1 e que s = g^(a·b) mod p.
- **a e b**: sorteados entre 2 e p-2 com `secrets.randbelow`. Estão fixos no código só para a
  entrega ser reproduzível; em uso real nunca se mostram.

## Observações
- Com p pequeno a Eve descobre o segredo por força bruta (exemplo 2). Com 256 bits isso é inviável (logaritmo discreto).
- Em uso real se usam primos de pelo menos 2048 bits. 256 bits serve só para a prática.
- O DH puro **não autentica** ninguém: sofre ataque man-in-the-middle (por isso se usam certificados, como na Aula 11).
