"""
Atividade 04 - Cifra de Feistel com 16 rodadas
Disciplina: DCC075 - Segurança em Sistemas de Computação

IDEIA DA REDE DE FEISTEL
Divide o bloco em duas metades, L (esquerda) e R (direita), e repete
várias rodadas. Em cada rodada:

        L_novo = R
        R_novo = L XOR f(R, subchave)

A função f pode ser qualquer coisa (até irreversível!). A reversão
funciona porque o XOR desfaz a si mesmo: na rodada seguinte, quem
chega até nós é L_novo = R, então conseguimos recalcular f(R, subchave)
e "tirar" ela do R_novo com outro XOR. Por isso, para DECRIPTAR basta
rodar o MESMO algoritmo usando as subchaves na ORDEM INVERSA.

PARÂMETROS DESTA IMPLEMENTAÇÃO
  - bloco de 64 bits (8 bytes), metades de 32 bits
  - 16 rodadas, uma subchave de 32 bits por rodada
  - função f = XOR com a subchave -> S-BOX -> rotação de bits
  - modo de operação: cada bloco é cifrado separadamente (tipo ECB)
"""

import argparse
import hashlib

NUM_RODADAS = 16
TAM_BLOCO = 8              # bytes (64 bits)
MASCARA32 = 0xFFFFFFFF     # para manter os números com 32 bits

# S-box de 4 bits -> 4 bits (a mesma do algoritmo PRESENT).
# O enunciado permite usar S-boxes de outros algoritmos sem se preocupar
# em construir uma forte. Cada valor de 0 a 15 aparece uma única vez.
SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD,
        0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
assert sorted(SBOX) == list(range(16))  # confere que é uma permutação


# ----------------------------------------------------------------------
# Peças da função f
# ----------------------------------------------------------------------

def rotacionar_esq(valor, n):
    """Gira os 32 bits para a esquerda n posições (o que sai volta pela direita)."""
    return ((valor << n) | (valor >> (32 - n))) & MASCARA32


def aplicar_sbox(x):
    """Troca cada um dos 8 grupos de 4 bits (nibbles) pelo valor da S-box."""
    resultado = 0
    for i in range(8):
        nibble = (x >> (4 * i)) & 0xF           # pega 4 bits
        resultado |= SBOX[nibble] << (4 * i)    # substitui e põe de volta
    return resultado


def funcao_f(metade, subchave):
    """
    Função f da rodada.
      1) XOR com a subchave      -> mistura a chave no dado
      2) S-box                   -> não linearidade (confusão)
      3) rotação de 11 bits      -> espalha os bits entre os nibbles (difusão)
    """
    x = metade ^ subchave
    x = aplicar_sbox(x)
    x = rotacionar_esq(x, 11)
    return x


# ----------------------------------------------------------------------
# Geração das subchaves
# ----------------------------------------------------------------------

def gerar_subchaves(chave):
    """
    Transforma a senha (texto) em 16 subchaves de 32 bits.
    Para ficar simples, usamos o SHA-512 da senha (64 bytes) e cortamos
    em 16 pedaços de 4 bytes. (Cifras reais usam um "key schedule" próprio.)
    """
    digest = hashlib.sha512(chave.encode("utf-8")).digest()
    return [int.from_bytes(digest[4 * i: 4 * i + 4], "big")
            for i in range(NUM_RODADAS)]


# ----------------------------------------------------------------------
# O coração da cifra: processar UM bloco de 8 bytes
# ----------------------------------------------------------------------

def processar_bloco(bloco, subchaves, mostrar=False):
    """
    Aplica as 16 rodadas de Feistel em um bloco.
    Serve para encriptar (subchaves na ordem normal) e
    para decriptar (subchaves na ordem inversa).
    """
    valor = int.from_bytes(bloco, "big")
    L = valor >> 32            # metade esquerda (32 bits de cima)
    R = valor & MASCARA32      # metade direita (32 bits de baixo)

    if mostrar:
        print(f"  início      L={L:08x}  R={R:08x}")

    for i, k in enumerate(subchaves):
        # a rodada de Feistel: o R antigo vira o L; o novo R usa XOR com f
        L, R = R, L ^ funcao_f(R, k)
        if mostrar:
            print(f"  rodada {i + 1:2d}   L={L:08x}  R={R:08x}  (subchave {k:08x})")

    # Troca final das metades: é o que faz a decriptação ser idêntica
    # à encriptação (só muda a ordem das subchaves).
    L, R = R, L
    return ((L << 32) | R).to_bytes(TAM_BLOCO, "big")


# ----------------------------------------------------------------------
# Preenchimento (padding): o texto precisa ser múltiplo de 8 bytes
# ----------------------------------------------------------------------

def adicionar_padding(dados):
    """Completa com N bytes de valor N (padrão PKCS#7). Sempre adiciona algo."""
    faltam = TAM_BLOCO - (len(dados) % TAM_BLOCO)
    return dados + bytes([faltam]) * faltam


def remover_padding(dados):
    """Lê o último byte para saber quantos bytes de padding retirar."""
    if not dados:
        raise ValueError("dados vazios")
    n = dados[-1]
    if n < 1 or n > TAM_BLOCO or dados[-n:] != bytes([n]) * n:
        raise ValueError("padding inválido (chave errada ou dados corrompidos)")
    return dados[:-n]


# ----------------------------------------------------------------------
# Funções para o usuário: cifrar e decifrar mensagens inteiras
# ----------------------------------------------------------------------

def cifrar(texto, chave, mostrar=False):
    """Recebe texto e senha; devolve o texto cifrado em hexadecimal."""
    subchaves = gerar_subchaves(chave)
    dados = adicionar_padding(texto.encode("utf-8"))
    saida = b""
    for i in range(0, len(dados), TAM_BLOCO):          # bloco a bloco
        bloco = dados[i: i + TAM_BLOCO]
        saida += processar_bloco(bloco, subchaves, mostrar and i == 0)
    return saida.hex()


def decifrar(hexa, chave, mostrar=False):
    """Recebe o cifrado em hexadecimal e a senha; devolve o texto original."""
    dados = bytes.fromhex(hexa)
    if len(dados) == 0 or len(dados) % TAM_BLOCO != 0:
        raise ValueError("o texto cifrado deve ter múltiplos de 8 bytes (16 hex)")
    # O PULO DO GATO: mesmas operações, subchaves em ordem inversa
    subchaves = gerar_subchaves(chave)[::-1]
    saida = b""
    for i in range(0, len(dados), TAM_BLOCO):
        bloco = dados[i: i + TAM_BLOCO]
        saida += processar_bloco(bloco, subchaves, mostrar and i == 0)
    return remover_padding(saida).decode("utf-8")


# ----------------------------------------------------------------------
# Demonstração e linha de comando
# ----------------------------------------------------------------------

def demonstracao():
    texto = "Feistel 16 rodadas!"
    chave = "minha-senha"
    print(f"Texto:  {texto}")
    print(f"Chave:  {chave}\n")

    print("Encriptação do primeiro bloco, rodada a rodada:")
    cifrado = cifrar(texto, chave, mostrar=True)
    print(f"\nTexto cifrado (hex): {cifrado}\n")

    print("Decriptação do primeiro bloco (mesmo algoritmo, subchaves invertidas):")
    original = decifrar(cifrado, chave, mostrar=True)
    print(f"\nTexto decifrado: {original}")
    print("Confere!" if original == texto else "ERRO: não voltou ao original")


def main():
    parser = argparse.ArgumentParser(description="Cifra de Feistel com 16 rodadas")
    sub = parser.add_subparsers(dest="comando")

    p1 = sub.add_parser("cifrar", help="cifra um texto")
    p1.add_argument("texto")
    p1.add_argument("chave")

    p2 = sub.add_parser("decifrar", help="decifra um texto em hexadecimal")
    p2.add_argument("hexa")
    p2.add_argument("chave")

    sub.add_parser("demo", help="demonstração com rastreio das rodadas")

    args = parser.parse_args()

    try:
        if args.comando == "cifrar":
            print(cifrar(args.texto, args.chave))
        elif args.comando == "decifrar":
            print(decifrar(args.hexa, args.chave))
        else:
            demonstracao()  # sem argumentos: roda a demonstração
    except ValueError as erro:
        print(f"Erro: {erro}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
