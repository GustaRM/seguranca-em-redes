# Atividade 04 - Cifra de Feistel (16 rodadas)

Implementação em Python (só biblioteca padrão, nenhuma instalação necessária) de uma
rede de Feistel com **encriptação e decriptação**.

## Como funciona
O bloco de 64 bits é dividido em duas metades de 32 bits (L e R). Em cada uma das
16 rodadas:

```
L_novo = R
R_novo = L XOR f(R, subchave)
```

A decriptação é o **mesmo algoritmo com as subchaves na ordem inversa**. Isso funciona
porque o XOR é autorreversível, e mesmo que `f` não tivesse inversa, ela pode ser
recalculada (a entrada de `f` na rodada anterior é o L da rodada atual).

### Função f
1. XOR da metade com a subchave de 32 bits
2. S-box de 4 bits (a do algoritmo PRESENT) aplicada nos 8 nibbles
3. Rotação de 11 bits à esquerda

### Outros detalhes
- Subchaves: SHA-512 da senha cortado em 16 pedaços de 32 bits.
- Padding PKCS#7 para completar blocos de 8 bytes.
- Cada bloco é cifrado separadamente (como o modo ECB da Aula 08), então blocos iguais
  geram cifrados iguais. Para uso real seria preciso CBC, CTR etc.
- Esta cifra é didática e **não deve ser usada para proteger dados reais**.

## Como executar
Requer Python 3.

```bash
python3 feistel.py                         # demonstração com as 16 rodadas na tela
python3 feistel.py cifrar "meu texto" "minhasenha"
python3 feistel.py decifrar <hex_gerado_acima> "minhasenha"
```
No Windows use `python` no lugar de `python3`.

Exemplo:
```
$ python3 feistel.py cifrar "Olá, mundo! Ação 123" "senha123"
a748de95ad04a7583e817d90f8e9b7eddcf4077eedc3b7f6
$ python3 feistel.py decifrar a748de95ad04a7583e817d90f8e9b7eddcf4077eedc3b7f6 "senha123"
Olá, mundo! Ação 123
```
Com a senha errada o programa avisa que o padding é inválido.

## Testes feitos
- Ida e volta (cifrar e decifrar) com 300 textos aleatórios, incluindo vazio, acentos e emoji.
- Mudar 1 caractere do texto altera 36 dos 64 bits do bloco cifrado (efeito avalanche).
