"""
Atividade 03 (parte 1) - Cifra de César
Disciplina: DCC075 - Segurança em Sistemas de Computação

A cifra de César é uma cifra de SUBSTITUIÇÃO: cada letra do texto claro
é trocada pela letra que está k posições à frente no alfabeto.
Exemplo com k = 3:   A -> D,  B -> E,  ...,  X -> A,  Y -> B,  Z -> C
(quando passa do Z, volta para o A, por isso usamos o resto da divisão).

Matematicamente, com as letras numeradas de 0 (A) a 25 (Z):
    cifrar:    C = (P + k) mod 26
    decifrar:  P = (C - k) mod 26
A chave é o próprio deslocamento k (de 1 a 25, já que k = 26 daria a
volta completa e o texto ficaria igual).
"""

import unicodedata

TAM = 26  # tamanho do alfabeto (A a Z)


def remover_acentos(texto):
    """Tira os acentos (ã -> a, ç -> c), pois o alfabeto da cifra só tem A-Z."""
    # NFD separa a letra do acento: 'ã' vira 'a' + '~'
    decomposto = unicodedata.normalize("NFD", texto)
    # categoria "Mn" = marca de acento; descartamos essas marcas
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def deslocar(texto, k):
    """Desloca cada letra k posições. Espaços, números e pontuação ficam iguais."""
    resultado = ""
    for c in texto:
        # descobre onde começa o alfabeto do caractere (maiúscula ou minúscula)
        if "a" <= c <= "z":
            base = ord("a")
        elif "A" <= c <= "Z":
            base = ord("A")
        else:
            resultado += c  # não é letra: não mexe
            continue

        posicao = ord(c) - base          # posição da letra: 0 a 25
        nova = (posicao + k) % TAM       # soma k e "dá a volta" se passar de 25
        resultado += chr(base + nova)    # volta de número para letra
    return resultado


def cifrar(texto, k):
    """Encriptação: remove acentos e desloca k posições para frente."""
    return deslocar(remover_acentos(texto), k)


def decifrar(texto, k):
    """Decriptação: é só deslocar para trás (k negativo)."""
    return deslocar(texto, -k)


def mostrar_alfabetos(k):
    """Mostra o alfabeto claro em cima e o cifrado embaixo (ajuda a entender)."""
    claro = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cifrado = deslocar(claro, k)
    print("  Claro:   ", claro)
    print("  Cifrado: ", cifrado)


# ======================================================================
# Programa principal: pergunta o texto e a chave e mostra o resultado
# ======================================================================
if __name__ == "__main__":
    texto = input("Digite o texto a cifrar: ")
    if texto.strip() == "":
        texto = "Segurança em Sistemas de Computação"  # texto padrão
        print(f"(usando o texto padrão: {texto})")

    try:
        k = int(input("Digite a chave k (1 a 25): "))
    except ValueError:
        print("A chave precisa ser um número inteiro.")
        raise SystemExit(1)

    if not 1 <= k <= TAM - 1:
        print("A chave deve estar entre 1 e 25.")
        raise SystemExit(1)

    cifrado = cifrar(texto, k)
    print(f"\nChave k = {k}")
    mostrar_alfabetos(k)
    print(f"\nTexto claro:   {texto}")
    print(f"Texto cifrado: {cifrado}")
    print(f"Decifrado:     {decifrar(cifrado, k)}  (confere: volta ao original sem acentos)")
