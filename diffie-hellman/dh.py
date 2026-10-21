"""
Atividade 08 - Diffie-Hellman (DH)
Disciplina: DCC075 - Segurança em Sistemas de Computação

O DH deixa duas pessoas (Alice e Bob) combinarem um segredo s pelo canal
aberto, sem nunca mandarem o segredo em si. Passo a passo:

  1. Os dois combinam publicamente um primo p e uma raiz primitiva g mod p
  2. Alice escolhe a (secreto)  e manda  A = g^a mod p
  3. Bob   escolhe b (secreto)  e manda  B = g^b mod p
  4. Alice calcula  s = B^a mod p
     Bob   calcula  s = A^b mod p
  Os dois chegam no mesmo valor, pois (g^b)^a = (g^a)^b = g^(ab) mod p.

Quem está espiando (Eve) só vê p, g, A e B. Pra achar s ela precisaria
descobrir a (ou b) a partir de A = g^a mod p, o "logaritmo discreto",
que é muito difícil quando p é grande.

Uso:  python3 dh.py            (roda os 3 exemplos)
      python3 dh.py --novo-p   (gera um primo seguro novo de 256 bits)
"""

import secrets
import sys


# ----------------------------------------------------------------------
# Funções auxiliares (primo, fatores, raiz primitiva)
# ----------------------------------------------------------------------

def eh_primo(n, rodadas=40):
    """Teste de Miller-Rabin (probabilístico). Divisão simples não serve pra p grande."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    # escreve n-1 = d * 2^r com d ímpar
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rodadas):
        a = secrets.randbelow(n - 3) + 2          # base aleatória em [2, n-2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False                           # é composto com certeza
    return True                                    # provavelmente primo


def gerar_primo_seguro(bits):
    """
    Procura p = 2q + 1 com q também primo (primo "seguro").
    Pra esse tipo de primo fica fácil fatorar p-1 = 2 * q, o que ajuda a
    achar a raiz primitiva.
    """
    while True:
        # q com 'bits-1' bits, bit mais alto = 1 e ímpar
        q = secrets.randbits(bits - 1) | (1 << (bits - 2)) | 1
        if eh_primo(q) and eh_primo(2 * q + 1):
            return 2 * q + 1


def fatores_primos(n):
    """
    Fatores primos de n. Tiro os fatores pequenos por tentativa e, se sobrar
    um número grande, vejo se ele é primo (caso do p seguro: p-1 = 2 * q).
    """
    fatores = set()
    d = 2
    while d < 100000 and d * d <= n:
        while n % d == 0:
            fatores.add(d)
            n //= d
        d += 1
    if n > 1:
        if eh_primo(n):
            fatores.add(n)
        else:
            raise ValueError("não consegui fatorar p-1 (use um primo seguro)")
    return fatores


def eh_raiz_primitiva(g, p, fatores):
    """
    g é raiz primitiva mod p se a ordem dele for p-1, ou seja, se
    g^((p-1)/f) != 1 (mod p) para TODO fator primo f de p-1.
    """
    return all(pow(g, (p - 1) // f, p) != 1 for f in fatores)


def achar_raiz_primitiva(p):
    """Devolve a menor raiz primitiva de p (e os fatores de p-1)."""
    fatores = fatores_primos(p - 1)
    g = 2
    while not eh_raiz_primitiva(g, p, fatores):
        g += 1
    return g


# ----------------------------------------------------------------------
# O protocolo Diffie-Hellman
# ----------------------------------------------------------------------

def diffie_hellman(p, g, a, b):
    """Executa o DH com os segredos a (Alice) e b (Bob). Devolve tudo num dicionário."""
    A = pow(g, a, p)        # Alice -> Bob   (pública)
    B = pow(g, b, p)        # Bob   -> Alice (pública)
    s_alice = pow(B, a, p)  # Alice calcula o segredo com o B de Bob
    s_bob = pow(A, b, p)    # Bob   calcula o segredo com o A de Alice
    return {"A": A, "B": B, "s_alice": s_alice, "s_bob": s_bob}


def mostrar(p, g, a, b):
    r = diffie_hellman(p, g, a, b)
    print(f"p (primo)          = {p}")
    print(f"g (raiz primitiva) = {g}")
    print(f"a (secreto Alice)  = {a}")
    print(f"b (secreto Bob)    = {b}")
    print(f"A = g^a mod p      = {r['A']}")
    print(f"B = g^b mod p      = {r['B']}")
    print(f"s (Alice) = B^a    = {r['s_alice']}")
    print(f"s (Bob)   = A^b    = {r['s_bob']}")
    print("Segredos iguais?   =", r["s_alice"] == r["s_bob"])
    return r


# ----------------------------------------------------------------------
# Valores usados na entrega
# ----------------------------------------------------------------------

# Exemplo pequeno (o clássico da Wikipédia) só pra conferir a lógica
P_PEQ, G_PEQ, A_PEQ, B_PEQ = 23, 5, 6, 15

# Exemplo grande: primo seguro de 256 bits (gerado com gerar_primo_seguro(256)).
# g = menor raiz primitiva, achada com achar_raiz_primitiva(P).
# a e b foram sorteados com secrets.randbelow (aqui ficam fixos só pra entrega
# ser reproduzível; num uso real eles NUNCA aparecem no código nem na tela).
P = 91968614663333001359732462613504843415210995925369141928228899021272355533083
G = 2
A_PRIV = 43375646396213544966052051347786005282075117287134079075646793577096902219365
B_PRIV = 72928476973422965632467730146431736394074046644765371786922567414218744169654


def eve_forca_bruta(p, g, A, B):
    """
    A Eve só conhece p, g, A e B. Tenta todos os expoentes x até achar g^x = A.
    Com p pequeno isso é instantâneo; com p de 256 bits seria impossível.
    """
    for x in range(1, p):
        if pow(g, x, p) == A:
            return x, pow(B, x, p)   # achou 'a' e já calcula o segredo
    return None, None


if __name__ == "__main__":
    if "--novo-p" in sys.argv:
        novo = gerar_primo_seguro(256)
        print("novo p =", novo)
        print("menor raiz primitiva g =", achar_raiz_primitiva(novo))
        raise SystemExit

    # ---------------- Exemplo 1: p pequeno ----------------
    print("=== Exemplo 1: p = 23 (conferindo a lógica) ===")
    print("raízes primitivas de 23:",
          [x for x in range(2, 23) if eh_raiz_primitiva(x, 23, fatores_primos(22))])
    r = mostrar(P_PEQ, G_PEQ, A_PEQ, B_PEQ)

    # ---------------- Exemplo 2: Eve ataca o p pequeno ----------------
    print("\n=== Exemplo 2: a Eve atacando o p = 23 ===")
    a_eve, s_eve = eve_forca_bruta(P_PEQ, G_PEQ, r["A"], r["B"])
    print(f"Eve viu A={r['A']} e B={r['B']} e achou a={a_eve} -> s={s_eve}")
    print("Acertou o segredo?", s_eve == r["s_alice"], "(com p pequeno é fácil quebrar)")

    # ---------------- Exemplo 3: p grande ----------------
    print("\n=== Exemplo 3: p de 256 bits ===")
    assert eh_primo(P) and eh_primo((P - 1) // 2), "P não é primo seguro"
    assert eh_raiz_primitiva(G, P, fatores_primos(P - 1)), "G não é raiz primitiva"
    print(f"p tem {P.bit_length()} bits ({len(str(P))} dígitos), é primo e (p-1)/2 também")
    print("g é raiz primitiva de p: conferido\n")
    r = mostrar(P, G, A_PRIV, B_PRIV)
