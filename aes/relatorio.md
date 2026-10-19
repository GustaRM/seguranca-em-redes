# Relatório - Prática AES: confusão, difusão e efeito avalanche

**Aluno(a)/Dupla:** ______________________  **Disciplina:** DCC075

## Resultados medidos
| Experimento | Bits alterados (de 128) |
|---|---|
| Avalanche, AES completo: 1 bit no texto / na chave | 64,0 (50,0%) / 63,8 (49,8%) |
| Com MixColumns: 1 / 2 / 3 rodadas | 4,1 (3,2%) / 16,1 (12,5%) / 64,2 (50,2%) |
| Com MixColumns: 4 a 10 rodadas | ≈ 64 (≈ 50%), estável |
| Sem MixColumns: 2 / 4 / 6 / 10 rodadas | ≈ 4,0 a 4,1 (≈ 3,1 a 3,2%) em todos os casos |

## Parágrafo técnico
**Confusão** é tornar complexa e não linear a relação entre chave e texto cifrado; no AES ela vem do **SubBytes** (a S-box). **Difusão** é espalhar a influência de cada bit de entrada por muitos bits de saída; no AES ela vem do **ShiftRows**, que move os bytes entre colunas, e principalmente do **MixColumns**, que mistura os 4 bytes de cada coluna. O **AddRoundKey** é o único estágio que usa a chave.
Nos meus dados, a avalanche chegou a ~50% com **3 rodadas** (3,2% → 12,5% → 50,2%). A explicação está na estrutura: como a última rodada não tem MixColumns, com 1 rodada a diferença fica em 1 byte (~4 bits). A rodada 1 com MixColumns espalha a diferença por uma coluna (4 bytes, 12,5%), e o MixColumns da rodada 2, combinado com o ShiftRows, a leva às 4 colunas, saturando em 50%. Sem o MixColumns, a diferença ficou presa em ~4 bits para qualquer número de rodadas, pois SubBytes e ShiftRows só trocam valores e posições de bytes sem misturá-los. Logo, a difusão é essencial.

## Parágrafo crítico
O AES-128 usa 10 rodadas, mas a avalanche satura com 3, e isso **não** significa que 3 rodadas sejam seguras. A avalanche é uma condição necessária, não suficiente: ataques de criptoanálise exploram estruturas que um teste estatístico simples não enxerga. Existem ataques publicados contra versões reduzidas do AES-128 (cerca de 7 rodadas, segundo o roteiro), enquanto o AES completo permanece sem ataque prático; os melhores ataques teóricos contra as 10 rodadas ganham muito pouco sobre a força bruta (ordem de 2^126 contra 2^128).
Projetar com **margem** é uma decisão de engenharia de segurança: os ataques só melhoram com o tempo, então a distância entre o ataque mais forte conhecido (7 rodadas) e o número real de rodadas (10) absorve técnicas ainda desconhecidas. O custo é pequeno (mais rodadas = pouco desempenho a menos, e os processadores têm instruções AES dedicadas), enquanto o custo de uma quebra seria enorme, como acontece em projetos de pontes ou aviões, que usam fatores de segurança acima da carga esperada.
