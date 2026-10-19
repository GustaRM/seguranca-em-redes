"""
Prática AES — VERSÃO DO ALUNO
"AES por dentro: confusão, difusão e efeito avalanche"

A cifra AES-128 opera sobre um bloco de 128 bits.
NÃO usamos nenhum modo de operação (isso vem em aulas futuras).

>>> A PARTE 1 JÁ VEM RESOLVIDA, como exemplo de referência. <<<
Estude como ela mede o efeito avalanche e use o MESMO padrão para
completar as Partes 2 e 3 (trechos marcados com # TODO).

Requisitos: apenas biblioteca padrão do Python 3.
Execute:    python3 aluno.py
"""

# =====================================================================
# NÚCLEO AES-128 (bloco único) — JÁ PRONTO, não precisa alterar
# =====================================================================
SBOX = [
0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16,
]
RCON = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36]

def xtime(a):
    a <<= 1
    if a & 0x100:
        a ^= 0x11b
    return a & 0xff

def gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        b >>= 1
        a = xtime(a)
    return p

def key_expansion(key):
    assert len(key) == 16
    words = [list(key[i:i+4]) for i in range(0, 16, 4)]
    for i in range(4, 44):
        temp = list(words[i-1])
        if i % 4 == 0:
            temp = temp[1:] + temp[:1]
            temp = [SBOX[b] for b in temp]
            temp[0] ^= RCON[i//4 - 1]
        words.append([words[i-4][j] ^ temp[j] for j in range(4)])
    return [sum(words[4*r:4*r+4], []) for r in range(11)]

def add_round_key(state, rk): return [state[i] ^ rk[i] for i in range(16)]
def sub_bytes(state):         return [SBOX[b] for b in state]

def shift_rows(s):
    return [s[0], s[5], s[10], s[15],
            s[4], s[9], s[14], s[3],
            s[8], s[13], s[2], s[7],
            s[12], s[1], s[6], s[11]]

def mix_columns(s):
    out = [0]*16
    for c in range(4):
        col = s[c*4:c*4+4]
        out[c*4+0] = gmul(col[0],2) ^ gmul(col[1],3) ^ col[2] ^ col[3]
        out[c*4+1] = col[0] ^ gmul(col[1],2) ^ gmul(col[2],3) ^ col[3]
        out[c*4+2] = col[0] ^ col[1] ^ gmul(col[2],2) ^ gmul(col[3],3)
        out[c*4+3] = gmul(col[0],3) ^ col[1] ^ col[2] ^ gmul(col[3],2)
    return out

def encrypt_block(pt, key, rounds=10, use_mixcolumns=True):
    """
    Cifra UM bloco de 16 bytes.
      rounds        : nº de rodadas (1..10). rounds=10 + use_mixcolumns=True
                      reproduz o AES-128 real (casa com o FIPS-197).
      use_mixcolumns: se False, remove MixColumns de TODAS as rodadas.
    A última rodada nunca aplica MixColumns (como no AES real).
    """
    assert len(pt) == 16 and 1 <= rounds <= 10
    rk = key_expansion(key)
    state = add_round_key(list(pt), rk[0])
    for r in range(1, rounds):
        state = sub_bytes(state)
        state = shift_rows(state)
        if use_mixcolumns:
            state = mix_columns(state)
        state = add_round_key(state, rk[r])
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, rk[rounds])
    return bytes(state)


# =====================================================================
# FERRAMENTA — JÁ PRONTA
# =====================================================================
def flip_bit(data: bytes, bit_index: int) -> bytes:
    """Retorna 'data' com um único bit (0..len*8-1) invertido."""
    b = bytearray(data)
    b[bit_index // 8] ^= (1 << (bit_index % 8))
    return bytes(b)


# =====================================================================
# VALIDAÇÃO — confirme o núcleo antes de começar (JÁ PRONTA)
# =====================================================================
def validar_fips():
    pt  = bytes.fromhex("00112233445566778899aabbccddeeff")
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    ct = encrypt_block(pt, key).hex()
    assert ct == "69c4e0d86a7b0430d8cdb78070b4c55a", f"nucleo quebrado: {ct}"
    print(f"[FIPS-197] AES-128 OK  ct={ct}\n")


import os, statistics

# =====================================================================
# FERRAMENTA — distância de Hamming  (JÁ RESOLVIDA — use nas Partes 2 e 3)
# =====================================================================
def hamming(a: bytes, b: bytes) -> int:
    """Número de BITS que diferem entre a e b (mesmo tamanho)."""
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


# =====================================================================
# PARTE 1 — Efeito avalanche  ★ RESOLVIDA (exemplo de referência) ★
# ---------------------------------------------------------------------
# Invertendo UM único bit da entrada, ~metade dos bits do ciphertext
# muda. Medimos isso em média sobre muitas amostras aleatórias, para
# (a) o texto claro e (b) a chave.  Estude este padrão: as Partes 2 e 3
# são variações diretas dele.
# =====================================================================
def parte1_avalanche(amostras=2000):
    dists_pt  = []   # distâncias quando viramos 1 bit do TEXTO
    dists_key = []   # distâncias quando viramos 1 bit da CHAVE

    for _ in range(amostras):
        pt  = os.urandom(16)          # texto claro aleatório (16 bytes)
        key = os.urandom(16)          # chave aleatória (16 bytes)
        bit = os.urandom(1)[0] % 128  # qual dos 128 bits inverter

        # (a) mesma chave, 1 bit do texto invertido
        c0 = encrypt_block(pt, key)
        c1 = encrypt_block(flip_bit(pt, bit), key)
        dists_pt.append(hamming(c0, c1))

        # (b) mesmo texto, 1 bit da chave invertido
        c0k = encrypt_block(pt, key)
        c1k = encrypt_block(pt, flip_bit(key, bit))
        dists_key.append(hamming(c0k, c1k))

    mpt  = statistics.mean(dists_pt)
    mkey = statistics.mean(dists_key)
    print("[P1] Efeito avalanche (AES completo, bloco de 128 bits)")
    print(f"[P1]  1 bit no TEXTO -> {mpt:.1f}/128 ({mpt/128*100:.1f}%)")
    print(f"[P1]  1 bit na CHAVE -> {mkey:.1f}/128 ({mkey/128*100:.1f}%)")
    print(f"[P1]  (esperado ~64/128 = 50%)\n")
    return mpt, mkey


# =====================================================================
# PARTE 2 — Difusão rodada a rodada  (~20 min)   [VOCÊ IMPLEMENTA]
# ---------------------------------------------------------------------
# Igual à Parte 1(a), mas variando rounds = 1..10. A avalanche deve
# partir de poucos bits e crescer até saturar em ~50%.
# =====================================================================
def parte2_por_rodada(amostras=1500):
    print("[P2] Avalanche vs numero de rodadas")
    curva = {}
    for R in range(1, 11):
        d = []
        for _ in range(amostras):
            pt  = os.urandom(16); key = os.urandom(16)
            bit = os.urandom(1)[0] % 128
            # TODO 2 (resolvido): igual à Parte 1(a), mas limitando o AES
            # a R rodadas nas DUAS cifragens (rounds=R), para ver como a
            # diferença de 1 bit vai se espalhando rodada a rodada.
            c0 = encrypt_block(pt, key, rounds=R)                  # texto original
            c1 = encrypt_block(flip_bit(pt, bit), key, rounds=R)   # 1 bit invertido
            d.append(hamming(c0, c1))   # quantos bits do ciphertext mudaram
        m = statistics.mean(d)
        curva[R] = m
        print(f"[P2]  {R:2d} rodada(s): {m:5.1f}/128 ({m/128*100:4.1f}%) {'#'*int(m/128*40)}")
    print()
    return curva


# =====================================================================
# PARTE 3 — Isolando MixColumns  (~10 min)       [VOCÊ IMPLEMENTA]
# ---------------------------------------------------------------------
# Igual à Parte 2, mas com use_mixcolumns=False. Sem a difusão do
# MixColumns, a mudança de 1 bit NAO se espalha: fica presa em poucos
# bits, por mais rodadas que se apliquem.
# =====================================================================
def parte3_sem_mixcolumns(amostras=1500):
    print("[P3] Difusao SEM MixColumns")
    for R in (2, 4, 6, 10):
        d = []
        for _ in range(amostras):
            pt  = os.urandom(16); key = os.urandom(16)
            bit = os.urandom(1)[0] % 128
            # TODO 3 (resolvido): igual à Parte 2, mas com use_mixcolumns=False
            # nas duas cifragens. Sem o MixColumns (a difusão), a diferença
            # de 1 bit só muda de lugar (ShiftRows) e de valor (SubBytes),
            # mas não se espalha pelos outros bytes do bloco.
            c0 = encrypt_block(pt, key, rounds=R, use_mixcolumns=False)
            c1 = encrypt_block(flip_bit(pt, bit), key, rounds=R, use_mixcolumns=False)
            d.append(hamming(c0, c1))
        m = statistics.mean(d)
        print(f"[P3]  {R:2d} rodada(s) sem MixColumns: {m:5.1f}/128 ({m/128*100:4.1f}%)")
    print()


if __name__ == "__main__":
    validar_fips()
    parte1_avalanche()      # já funciona
    parte2_por_rodada()     # implemente
    parte3_sem_mixcolumns() # implemente
    print("=== EXPERIMENTOS CONCLUÍDOS ===")
