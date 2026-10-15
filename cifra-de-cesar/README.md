# Atividade 03 - Cifra de César e criptoanálise

## O que tem aqui
| Arquivo | O que faz |
|---|---|
| `cesar.py` | Cifra (e decifra) de César com chave k de 1 a 25 |
| `criptoanalise.py` | Quebra a cifra usando a frequência das letras do português |
| `exemplo_cifrado.txt` | Texto de exemplo cifrado com k = 11, para testar o ataque via arquivo |

## Como funciona
Cada letra é trocada pela letra k posições à frente (`C = (P + k) mod 26`).
Espaços, números e pontuação não mudam. Acentos são removidos antes de cifrar
(o alfabeto da cifra só tem A-Z).

## Como executar
```bash
python3 cesar.py                              # pergunta texto e chave k
python3 criptoanalise.py                      # demonstração (cifra com k=7 e ataca)
python3 criptoanalise.py exemplo_cifrado.txt  # ataca um texto cifrado em arquivo
```

## Criptoanálise
A cifra preserva a "assinatura" do idioma: em português, A (~14,6%), E (~12,6%) e
O (~10,7%) são as letras mais comuns. O programa:
1. Conta as letras do texto cifrado e mostra o histograma.
2. Faz um palpite simples: a letra mais frequente corresponde ao `A`.
3. Testa as 25 chaves e escolhe a que deixa o texto com a distribuição mais parecida
   com a do português (medida pelo qui-quadrado; menor = melhor).

Nos testes, o ataque acertou a chave nas 25 possibilidades usando o texto de exemplo.

## Limitações
- Textos muito curtos têm frequências instáveis e o ataque pode errar.
- As frequências usadas são aproximadas (tabela da Wikipédia para o português).
- O espaço de chaves é de só 25 valores, por isso a força bruta também quebra a cifra.
