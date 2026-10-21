# Prática: Modos de Operação de Cifra de Blocos (AES-128 com OpenSSL)

> Texto-base para a parte escrita do PDF. Onde aparecer **[seu número]** ou **[print]**,
> troque pelo que saiu no SEU terminal.

## 1. O que foi feito
1. Geração da chave de 128 bits com `openssl enc -pbkdf2 -aes-128-ecb -k ... -P`
   (a senha passa pelo PBKDF2 junto com um *salt* aleatório).
2. Geração de um IV de 128 bits com `openssl rand -hex 16`.
3. Download do Tux, conversão para PPM e separação em **cabeçalho** (3 primeiras linhas)
   e **corpo** (pixels). Só o corpo é cifrado, para a imagem continuar abrindo.
4. Cifragem do corpo com AES-128 nos modos **ECB, CBC, CFB, OFB e CTR**, recolocando o
   cabeçalho em cada resultado para poder visualizá-lo.

**[print do terminal: seções 1 a 4 do script]**

## 2. Resultados

**[print: saida/comparacao.png, com a imagem original e os cinco modos]**

| Modo | O que se vê na imagem | Blocos de 16 bytes repetidos | Tamanho do corpo |
|---|---|---|---|
| Original | Tux nítido | [seu número]% | [seu número] bytes |
| ECB | **O contorno do Tux continua visível** | [seu número]% | + 16 bytes (padding) |
| CBC | Ruído uniforme | 0% | + 16 bytes (padding) |
| CFB | Ruído uniforme | 0% | igual ao original |
| OFB | Ruído uniforme | 0% | igual ao original |
| CTR | Ruído uniforme | 0% | igual ao original |

**[print do terminal: seção 6, com `ls -l` e a tabela de blocos repetidos]**

## 3. Explicação dos resultados

**ECB (Electronic Codebook).** Cada bloco de 16 bytes é cifrado separadamente com a mesma
chave, então **blocos de texto claro iguais geram blocos cifrados iguais**. A imagem do Tux
tem grandes áreas de uma cor só (fundo, barriga, corpo), o que produz milhares de blocos
idênticos. O AES esconde o *valor* dos pixels, mas não esconde o *padrão* entre eles, por isso
o contorno do pinguim ainda aparece. O mesmo vale para o texto repetido da seção 3 do script:
no ECB os quatro blocos iguais viram quatro blocos cifrados iguais (o `od` mostra a linha
repetida como `*`). Conclusão: o ECB vaza informação e não deve ser usado para dados reais.

**CBC (Cipher Block Chaining).** Antes de cifrar, cada bloco de texto claro passa por um XOR
com o bloco cifrado anterior (o primeiro usa o IV). Assim, um bloco igual em posições
diferentes gera saídas diferentes, e o resultado parece ruído aleatório (0% de blocos
repetidos). Pontos de atenção: o IV deve ser imprevisível e a cifragem é sequencial (não
paraleliza). O CBC precisa de padding, por isso o arquivo cresceu 16 bytes.

**CFB e OFB.** Transformam a cifra de bloco em uma **cifra de fluxo**: o AES gera uma sequência
pseudoaleatória (*keystream*) que sofre XOR com o texto. No CFB o keystream depende do cifrado
anterior; no OFB depende só da saída anterior do AES (não do texto). Não precisam de padding
(arquivo com o mesmo tamanho) e também ocultam o padrão da imagem. O OFB é mais tolerante a
erros de transmissão (um bit errado afeta só um bit).

**CTR (Counter).** O keystream vem de cifrar um **contador** que incrementa a cada bloco, também
com XOR no texto. Sem padding, resultado em ruído, e cada bloco pode ser cifrado em paralelo,
o que o torna rápido (usado em hardware e no GCM).

**Observação de segurança:** no script o mesmo IV foi usado em vários modos só para comparar.
Em uso real, nos modos de fluxo (OFB, CTR, CFB) **nunca** se deve repetir o par chave + IV, pois
dois textos cifrados com o mesmo keystream permitem XOR entre si e revelam os textos.

## 4. Conclusão
Só o modo ECB deixou a imagem reconhecível. Isso mostra que o **modo de operação importa tanto
quanto o algoritmo**: o AES é forte, mas usado em ECB vaza a estrutura dos dados. CBC, CFB, OFB
e CTR esconderam o padrão por introduzirem dependência entre blocos (CBC, CFB), um keystream (OFB)
ou um contador (CTR).
