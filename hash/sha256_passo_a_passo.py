"""
Atividade 09 (item 1, material de apoio) - SHA-256 passo a passo

Implementação "na mão" do SHA-256 mostrando cada etapa, para acompanhar a
explicação do arquivo parte1_sha256_passo_a_passo.txt. Usa o exemplo "abc".
No final comparo com o hashlib (biblioteca pronta) pra ver se acertei.

Uso:  python3 sha256_passo_a_passo.py            (mensagem "abc")
      python3 sha256_passo_a_passo.py "outro texto"
"""

import hashlib
import sys

MASC = 0xFFFFFFFF  # mantém tudo em 32 bits


def primos(qtd):
    """Os 'qtd' primeiros números primos (2, 3, 5, 7, ...)."""
    lista, n = [], 2
    while len(lista) < qtd:
        if all(n % p for p in lista):
            lista.append(n)
        n += 1
    return lista


def raiz_frac_32(n, grau):
    """
    Primeiros 32 bits da parte fracionária da raiz de n (grau 2 = quadrada,
    grau 3 = cúbica). Faço com inteiros pra não ter erro de ponto flutuante:
    floor(raiz(n) * 2^32) mod 2^32  ==  floor(raiz(n * 2^(32*grau))) mod 2^32
    """
    alvo = n << (32 * grau)
    # busca binária da raiz inteira de 'alvo'
    baixo, alto = 0, 1 << 70
    while baixo < alto:
        meio = (baixo + alto + 1) // 2
        if meio ** grau <= alvo:
            baixo = meio
        else:
            alto = meio - 1
    return baixo & MASC


# Valores iniciais H0..H7: raiz quadrada dos 8 primeiros primos
H_INICIAL = [raiz_frac_32(p, 2) for p in primos(8)]
# Constantes K0..K63: raiz cúbica dos 64 primeiros primos
K = [raiz_frac_32(p, 3) for p in primos(64)]


def rotr(x, n):
    """Rotação à direita de n bits numa palavra de 32 bits."""
    return ((x >> n) | (x << (32 - n))) & MASC


# Funções lógicas do SHA-256
def ch(e, f, g):  return (e & f) ^ (~e & MASC & g)           # "escolha": e escolhe entre f e g
def maj(a, b, c): return (a & b) ^ (a & c) ^ (b & c)          # "maioria" dos 3 bits
def sigma0_maiusc(a): return rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)   # Σ0
def sigma1_maiusc(e): return rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)   # Σ1
def sigma0_minusc(x): return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)      # σ0
def sigma1_minusc(x): return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)    # σ1


def preencher(msg):
    """
    Padding: acrescenta o bit 1, zeros, e o tamanho original (64 bits)
    até o total ser múltiplo de 512 bits (64 bytes).
    """
    tamanho_bits = len(msg) * 8
    msg = msg + b"\x80"                          # bit '1' seguido de zeros (0x80 = 10000000)
    while len(msg) % 64 != 56:                   # deixa 8 bytes livres no fim do bloco
        msg += b"\x00"
    return msg + tamanho_bits.to_bytes(8, "big") # tamanho original em 64 bits


def agenda_de_mensagem(bloco):
    """Expande as 16 palavras do bloco em 64 palavras W0..W63."""
    W = [int.from_bytes(bloco[4 * i: 4 * i + 4], "big") for i in range(16)]
    for t in range(16, 64):
        W.append((sigma1_minusc(W[t - 2]) + W[t - 7] +
                  sigma0_minusc(W[t - 15]) + W[t - 16]) & MASC)
    return W


def comprimir(H, bloco, detalhar=False):
    """Processa um bloco de 512 bits: 64 rodadas e soma final nos H."""
    W = agenda_de_mensagem(bloco)
    a, b, c, d, e, f, g, h = H
    for t in range(64):
        T1 = (h + sigma1_maiusc(e) + ch(e, f, g) + K[t] + W[t]) & MASC
        T2 = (sigma0_maiusc(a) + maj(a, b, c)) & MASC
        h, g, f = g, f, e
        e = (d + T1) & MASC
        d, c, b = c, b, a
        a = (T1 + T2) & MASC
        if detalhar and t in (0, 1, 63):
            print(f"  rodada {t:2d}: a={a:08x} b={b:08x} c={c:08x} d={d:08x} "
                  f"e={e:08x} f={f:08x} g={g:08x} h={h:08x}")
    # soma final (mod 2^32) com os valores que tínhamos antes do bloco
    return [(x + y) & MASC for x, y in zip(H, [a, b, c, d, e, f, g, h])]


def sha256(msg, detalhar=False):
    if detalhar:
        print("1) Valores iniciais H0..H7 (raiz quadrada dos 8 primeiros primos):")
        print("  ", " ".join(f"{x:08x}" for x in H_INICIAL))
        print("2) Primeiras constantes K0..K3 (raiz cúbica dos primos):",
              " ".join(f"{x:08x}" for x in K[:4]), "...")
    preenchida = preencher(msg)
    if detalhar:
        print(f"3) Mensagem após o padding ({len(preenchida)} bytes = "
              f"{len(preenchida) // 64} bloco(s) de 512 bits):")
        print("  ", preenchida.hex())
    H = list(H_INICIAL)
    for i in range(0, len(preenchida), 64):
        bloco = preenchida[i: i + 64]
        if detalhar:
            W = agenda_de_mensagem(bloco)
            print(f"4) Agenda de mensagem do bloco: W0={W[0]:08x} W1={W[1]:08x} ... "
                  f"W15={W[15]:08x} | W16={W[16]:08x} W17={W[17]:08x} ... W63={W[63]:08x}")
            print("5) Rodadas de compressão (a..h):")
        H = comprimir(H, bloco, detalhar)
    if detalhar:
        print("6) Hash final = H0..H7 concatenados:")
    return "".join(f"{x:08x}" for x in H)


if __name__ == "__main__":
    texto = sys.argv[1] if len(sys.argv) > 1 else "abc"
    meu = sha256(texto.encode(), detalhar=True)
    oficial = hashlib.sha256(texto.encode()).hexdigest()
    print("  ", meu)
    print("\nhashlib:", oficial)
    print("Bateu com a biblioteca?", meu == oficial)
