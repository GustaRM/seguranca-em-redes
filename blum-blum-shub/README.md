# Atividade 07 - Blum Blum Shub + testes da suíte NIST

## Parâmetros usados
| | Valor |
|---|---|
| **p** | 104723 |
| **q** | 104579 |
| **s** (semente) | 20261019 |
| n = p·q | 10951826617 |
| x0 = s² mod n | 1573833350 |

### Por que esses valores atendem às premissas do BBS
- **p e q > 10000**: os dois são maiores que 10000 e estão na lista dos 10000 primos do Wikibooks.
- **p e q primos**: conferido no código (`eh_primo`).
- **p ≡ 3 (mod 4) e q ≡ 3 (mod 4)**: 104723 = 4·26180 + 3 e 104579 = 4·26144 + 3. É a condição para o BBS funcionar.
- **p ≠ q**.
- **mdc(s, n) = 1**: a semente não é múltiplo de p nem de q.
- **Ciclo longo**: escolhi p e q "primos seguros" (p = 2p' + 1 e q = 2q' + 1, com p' = 52361 e q' = 52289 primos). Assim a sequência só se repete depois de ~2,7 bilhões de passos, bem mais que o 1.000.000 de bits usados. Conferi que não há estado repetido nesses 1.000.000 de passos.

## Como executar
Só precisa de Python 3 (biblioteca padrão).
```bash
python3 bbs.py            # gera 1.000.000 de bits em bits.txt
python3 bbs.py 100000     # ou outra quantidade de bits
```

## Como testar na suíte NIST
1. Abra https://mzsoltmolnar.github.io/random-bitstream-tester/
2. Em **Manual bitstream input**, cole o conteúdo de `bits.txt` (uma linha só, 1.000.000 de 0/1).
3. Clique em **Insert Input Stream** e depois em **Start Test**.
4. Tire o print da tabela com os 14 testes e salve como `resultado_nist.png` nesta pasta.

> Um teste passa quando o p-valor é ≥ 0,01 (nível de significância de 0,01 usado pelo NIST).

## Resultado
![Resultado da suíte NIST](resultado_nist.png)

## Observações
- Antes de usar o site, eu conferi sozinho alguns testes (monobit, bloco, runs, maior sequência, cusum, entropia aproximada e serial) e todos deram p-valor acima de 0,01.
- Este BBS usa números pequenos (n tem ~34 bits). Serve para a prática, mas **não é seguro de verdade**: para uso criptográfico, p e q precisam ter centenas de dígitos.
