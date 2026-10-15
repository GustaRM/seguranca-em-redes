"""
Atividade 03 (parte 2) - Criptoanálise da cifra de César por frequência

Ideia: a cifra de César troca cada letra SEMPRE pela mesma outra letra.
Então a "assinatura" estatística do idioma continua no texto cifrado,
só que deslocada. Em português, a letra A é a mais comum (~14,6%),
seguida de E (~12,6%) e O (~10,7%). Se no texto cifrado a letra mais
frequente for, por exemplo, H, é provável que H = A, e a chave seria
k = H - A = 7.

Duas abordagens aqui:
  1) Palpite simples: a letra mais frequente do cifrado corresponde ao 'A'.
  2) Teste das 25 chaves: decifra com cada k e vê qual resultado tem a
     distribuição de letras mais parecida com a do português
     (medida pelo qui-quadrado, quanto MENOR, mais parecido).

Obs.: funciona melhor com textos longos. Em textos muito curtos as
frequências variam demais e o palpite pode errar.

Uso:
    python3 criptoanalise.py                  -> demonstração com texto de exemplo
    python3 criptoanalise.py arquivo.txt      -> ataca um texto cifrado em arquivo
"""

import sys
from collections import Counter
from cesar import cifrar, decifrar, remover_acentos, TAM

# Frequência (%) de cada letra na língua portuguesa
# (valores aproximados, conforme a tabela da Wikipédia indicada na atividade)
FREQ_PT = {
    "a": 14.63, "b": 1.04, "c": 3.88, "d": 4.99, "e": 12.57, "f": 1.02,
    "g": 1.30, "h": 1.28, "i": 6.18, "j": 0.40, "k": 0.02, "l": 2.78,
    "m": 4.74, "n": 5.05, "o": 10.73, "p": 2.52, "q": 1.20, "r": 6.53,
    "s": 7.81, "t": 4.34, "u": 4.63, "v": 1.67, "w": 0.01, "x": 0.21,
    "y": 0.01, "z": 0.47,
}

TEXTO_EXEMPLO = (
    "A segurança da informação depende de uma boa escolha de algoritmos e "
    "também de uma boa gestão das chaves. A cifra de César é uma das "
    "técnicas mais antigas de criptografia e foi usada pelos romanos para "
    "proteger mensagens militares. Ela funciona deslocando cada letra do "
    "alfabeto por um número fixo de posições, mas como existem apenas "
    "vinte e cinco chaves possíveis, qualquer pessoa consegue quebrar essa "
    "cifra com um pouco de paciência. Além disso, a análise de frequência "
    "mostra que a língua portuguesa tem uma forte preferência por algumas "
    "letras, como a vogal A, a vogal E e a vogal O, e essa característica "
    "continua visível no texto cifrado, o que facilita muito o trabalho do "
    "atacante que deseja descobrir a mensagem original."
)


def contar_letras(texto):
    """Conta quantas vezes cada letra aparece (ignorando acento e maiúscula)."""
    texto = remover_acentos(texto).lower()
    letras = [c for c in texto if "a" <= c <= "z"]  # só as letras
    return Counter(letras), len(letras)


def mostrar_histograma(contagem, total):
    """Imprime a frequência de cada letra com barrinhas de '#'."""
    print("Frequência das letras no texto cifrado:")
    for i in range(TAM):
        letra = chr(ord("a") + i)
        pct = 100 * contagem[letra] / total if total else 0
        print(f"  {letra.upper()}: {pct:5.2f}%  {'#' * round(pct)}")


def palpite_simples(contagem, letra_alvo="a"):
    """Abordagem 1: assume que a letra mais comum do cifrado é o 'A'."""
    mais_comum = contagem.most_common(1)[0][0]
    # k = posição da letra cifrada - posição da letra clara
    k = (ord(mais_comum) - ord(letra_alvo)) % TAM
    return mais_comum, k


def qui_quadrado(texto):
    """
    Mede o quanto o texto se parece com o português.
    Para cada letra compara o que apareceu (observado) com o que seria
    esperado pela tabela de frequências. Quanto menor o valor, mais parecido.
    """
    contagem, total = contar_letras(texto)
    soma = 0.0
    for letra, freq in FREQ_PT.items():
        esperado = freq / 100 * total
        observado = contagem[letra]
        soma += (observado - esperado) ** 2 / esperado
    return soma


def atacar(texto_cifrado):
    """Abordagem 2: testa k = 1..25 e ordena do mais ao menos provável."""
    resultados = []
    for k in range(1, TAM):
        candidato = decifrar(texto_cifrado, k)
        resultados.append((qui_quadrado(candidato), k, candidato))
    resultados.sort()  # menor qui-quadrado primeiro
    return resultados


def main():
    # Escolhe o texto: arquivo passado na linha de comando ou demonstração
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            texto_cifrado = f.read()
        chave_real = None
    else:
        chave_real = 7  # só para a demonstração: sabemos a resposta certa
        texto_cifrado = cifrar(TEXTO_EXEMPLO, chave_real)
        print(f"[Demonstração] Texto cifrado com k = {chave_real} (o atacante não sabe):")
        print(texto_cifrado, "\n")

    contagem, total = contar_letras(texto_cifrado)
    if total == 0:
        print("O texto não tem letras para analisar.")
        return

    # 1) histograma
    mostrar_histograma(contagem, total)

    # 2) palpite simples
    letra, k_simples = palpite_simples(contagem)
    print(f"\nPalpite simples: a letra mais frequente é '{letra.upper()}'.")
    print(f"Se ela for o 'A', a chave seria k = {k_simples}.")

    # 3) teste das 25 chaves
    ranking = atacar(texto_cifrado)
    print("\nTop 3 chaves pelo teste de frequência (qui-quadrado menor = melhor):")
    for qui, k, candidato in ranking[:3]:
        print(f"  k = {k:2d}  qui² = {qui:8.1f}  ->  {candidato[:60]}...")

    melhor_k = ranking[0][1]
    print(f"\nChave mais provável: k = {melhor_k}")
    print("\nTexto recuperado:")
    print(ranking[0][2])

    if chave_real is not None:
        resultado = "ACERTOU" if melhor_k == chave_real else "ERROU"
        print(f"\nChave real: {chave_real} -> a criptoanálise {resultado}.")


if __name__ == "__main__":
    main()
