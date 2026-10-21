"""
Atividade 07 - Gerador Blum Blum Shub (BBS)
Disciplina: DCC075 - Segurança em Sistemas de Computação

Como o BBS funciona (resumo do que vimos em aula):
  1. escolhe dois primos grandes p e q, os dois congruentes a 3 mod 4
  2. calcula n = p * q
  3. escolhe uma semente s com mdc(s, n) = 1 (s não pode ser múltiplo de p nem de q)
  4. estado inicial: x0 = s^2 mod n
  5. a cada passo:  x(i+1) = x(i)^2 mod n
     e o bit de saída é o bit menos significativo (LSB) de x(i+1)

Uso:
    python3 bbs.py              -> gera 1.000.000 de bits em bits.txt
    python3 bbs.py 100000       -> gera a quantidade de bits que você quiser
"""

import sys
from math import gcd

# ----------------------------------------------------------------------
# Parâmetros escolhidos (p e q retirados da lista dos 10000 primos)
# ----------------------------------------------------------------------
P = 104723
Q = 104579
S = 20261019   # semente (escolhi a data de hoje, só pra lembrar)


def eh_primo(n):
    """Teste de primalidade por divisão (serve porque os números são pequenos)."""
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def validar_parametros(p, q, s):
    """Confere as premissas do BBS. Se alguma falhar, para o programa."""
    assert p > 10000 and q > 10000, "p e q precisam ser maiores que 10000"
    assert eh_primo(p) and eh_primo(q), "p e q precisam ser primos"
    assert p != q, "p e q precisam ser diferentes"
    assert p % 4 == 3 and q % 4 == 3, "p e q precisam ser congruentes a 3 mod 4"
    assert gcd(s, p * q) == 1, "a semente s precisa ser coprima de n"
    assert s not in (0, 1), "s não pode ser 0 nem 1"


def blum_blum_shub(p, q, s, quantidade):
    """Gera 'quantidade' bits pseudoaleatórios e devolve numa lista."""
    n = p * q
    x = (s * s) % n            # x0 = s^2 mod n
    bits = []
    for _ in range(quantidade):
        x = (x * x) % n        # x(i+1) = x(i)^2 mod n
        bits.append(x & 1)     # pega só o último bit (LSB)
    return bits


if __name__ == "__main__":
    quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000

    validar_parametros(P, Q, S)
    n = P * Q

    print("=== Blum Blum Shub ===")
    print(f"p = {P}   (p mod 4 = {P % 4})")
    print(f"q = {Q}   (q mod 4 = {Q % 4})")
    print(f"s = {S}   (mdc(s, n) = {gcd(S, n)})")
    print(f"n = p * q = {n}")
    print(f"x0 = s^2 mod n = {(S * S) % n}")

    bits = blum_blum_shub(P, Q, S, quantidade)
    sequencia = "".join(str(b) for b in bits)

    # salva tudo numa linha só, pra colar no site do teste NIST
    with open("bits.txt", "w") as f:
        f.write(sequencia)

    print(f"\n{quantidade} bits gerados e salvos em bits.txt")
    print(f"Primeiros 64 bits: {sequencia[:64]}")
    print(f"Quantidade de 1s: {sum(bits)}  ({100 * sum(bits) / quantidade:.2f}%)")
