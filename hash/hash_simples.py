"""
Atividade 09 (item 3) - Hash simples com XOR e rotação

Dois hashes de 32 bits que eu mesmo fiz, só pra entender o conceito:

  hash_xor      -> divide a mensagem em blocos de 4 bytes e faz XOR de todos
  hash_xor_rot  -> igual, mas a cada bloco gira (rotaciona) o estado 5 bits
                   e no fim mistura o tamanho da mensagem

No final o programa mostra por que NENHUM dos dois é seguro: a saída muda
pouco quando mexemos num bit (sem efeito avalanche) e é fácil achar colisões.

Uso: python3 hash_simples.py
"""

import hashlib
import os
import random

MASC = 0xFFFFFFFF
TAM_BLOCO = 4                 # 4 bytes = 32 bits por bloco
IV = 0x12345678               # valor inicial do estado (escolhi qualquer um)


def rotl(x, n):
    """Rotação à esquerda de n bits numa palavra de 32 bits."""
    return ((x << n) | (x >> (32 - n))) & MASC


def blocos(dados):
    """Completa com zeros até múltiplo de 4 bytes e separa em blocos de 32 bits."""
    while len(dados) % TAM_BLOCO != 0:
        dados += b"\x00"
    return [int.from_bytes(dados[i:i + TAM_BLOCO], "big")
            for i in range(0, len(dados), TAM_BLOCO)]


def hash_xor(dados):
    """Versão 1: XOR puro de todos os blocos."""
    h = 0
    for b in blocos(dados):
        h ^= b
    return h


def hash_xor_rot(dados):
    """Versão 2: XOR + rotação a cada bloco + tamanho no final."""
    h = IV
    for b in blocos(dados):
        h = rotl(h ^ b, 5)         # mistura o bloco e gira 5 bits
    h ^= len(dados)                # evita que "a" e "a\x00" deem o mesmo hash
    return rotl(h, 5)


def em_hex(h):
    return f"{h:08x}"


def bits_diferentes(a, b, tamanho_bits):
    return bin(a ^ b).count("1") / tamanho_bits * 100


def trocar_um_bit(dados):
    """Devolve a mensagem com um bit aleatório invertido."""
    i = random.randrange(len(dados) * 8)
    novo = bytearray(dados)
    novo[i // 8] ^= 1 << (i % 8)
    return bytes(novo)


if __name__ == "__main__":
    random.seed(7)

    # ------------------------------------------------------------
    print("=== 1) Hashes de alguns textos ===")
    for texto in ["abc", "abd", "Segurança em Redes", "Segurança em redes"]:
        d = texto.encode()
        print(f"{texto!r:24} xor={em_hex(hash_xor(d))}  xor_rot={em_hex(hash_xor_rot(d))}")

    # ------------------------------------------------------------
    print("\n=== 2) Efeito avalanche (trocando 1 bit da mensagem) ===")
    print("Num bom hash, ~50% dos bits da saída mudam.")
    n = 2000
    soma_x = soma_xr = soma_sha = 0
    for _ in range(n):
        m = os.urandom(16)
        m2 = trocar_um_bit(m)
        soma_x += bits_diferentes(hash_xor(m), hash_xor(m2), 32)
        soma_xr += bits_diferentes(hash_xor_rot(m), hash_xor_rot(m2), 32)
        s1 = int(hashlib.sha256(m).hexdigest(), 16)
        s2 = int(hashlib.sha256(m2).hexdigest(), 16)
        soma_sha += bits_diferentes(s1, s2, 256)
    print(f"hash_xor     : {soma_x / n:5.1f}% dos bits mudam")
    print(f"hash_xor_rot : {soma_xr / n:5.1f}% dos bits mudam")
    print(f"SHA-256      : {soma_sha / n:5.1f}% dos bits mudam")

    # ------------------------------------------------------------
    print("\n=== 3) Colisão no hash_xor: trocar a ordem dos blocos ===")
    m1, m2 = b"AAAABBBB", b"BBBBAAAA"
    print(f"{m1!r} -> {em_hex(hash_xor(m1))}")
    print(f"{m2!r} -> {em_hex(hash_xor(m2))}   (mensagens diferentes, mesmo hash!)")

    # ------------------------------------------------------------
    print("\n=== 4) Colisão no hash_xor_rot (construída) ===")
    # Com 2 blocos: h = rotl(IV^b0,10) ^ rotl(b1,5) ... (tudo é linear).
    # Se mexo em b0 com um valor d, basta mexer em b1 com rotl(d,5) pra compensar.
    b0, b1 = 0x41424344, 0x45464748
    d = 0x0000ABCD
    ma = b0.to_bytes(4, "big") + b1.to_bytes(4, "big")
    mb = (b0 ^ d).to_bytes(4, "big") + (b1 ^ rotl(d, 5)).to_bytes(4, "big")
    print(f"{ma!r} -> {em_hex(hash_xor_rot(ma))}")
    print(f"{mb!r} -> {em_hex(hash_xor_rot(mb))}")
    print("Mesmo hash?", hash_xor_rot(ma) == hash_xor_rot(mb), "| mensagens diferentes?", ma != mb)

    # ------------------------------------------------------------
    print("\n=== 5) Colisão por força bruta (paradoxo do aniversário) ===")
    vistos = {}
    tentativas = 0
    while True:
        m = os.urandom(8)
        tentativas += 1
        h = hash_xor_rot(m)
        if h in vistos and vistos[h] != m:
            print(f"Achei depois de {tentativas} tentativas (esperado ~ 2^16 = 65536):")
            print(f"  {vistos[h].hex()} e {m.hex()} -> {em_hex(h)}")
            break
        vistos[h] = m
