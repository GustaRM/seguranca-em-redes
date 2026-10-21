#!/usr/bin/env bash
# =====================================================================
# Atividade 06 - Modos de operação com OpenSSL (imagem do Tux)
#
# Roda TODA a prática de uma vez e imprime cada comando antes de executá-lo
# (assim o terminal já fica pronto para tirar o print).
#
# Onde executar: Linux, WSL ou "Git Bash" no Windows (precisa de openssl,
# curl e Python 3 com Pillow:  pip install pillow).
#
#   bash executar_pratica.sh
# =====================================================================
set -e
cd "$(dirname "$0")"
mkdir -p saida

# Procura um Python que tenha o Pillow instalado
PY=""
for c in python3 python py; do
  if command -v $c >/dev/null 2>&1 && $c -c "import PIL" >/dev/null 2>&1; then PY=$c; break; fi
done
if [ -z "$PY" ]; then
  echo "Python com Pillow não encontrado. Instale com: pip install pillow"; exit 1
fi

# Função auxiliar: mostra o comando (com "$") e depois executa
mostrar() { echo; echo "\$ $*"; eval "$*"; }

echo "================ 0. Ambiente ================"
mostrar "openssl version"

echo; echo "================ 1. Chave simétrica (PBKDF2) ================"
echo "\$ openssl enc -pbkdf2 -aes-128-ecb -k my-secret-passphrase -P"
SAIDA=$(openssl enc -pbkdf2 -aes-128-ecb -k my-secret-passphrase -P)
echo "$SAIDA"
KEY=$(echo "$SAIDA" | grep '^key=' | cut -d= -f2)   # pega só o valor da chave
echo "\$ echo $KEY > key.priv"
echo "$KEY" > key.priv

echo; echo "================ 2. Vetor de inicialização (IV) ================"
mostrar "openssl rand -hex 16 > iv.txt"
mostrar "cat iv.txt"

echo; echo "================ 3. Demonstração rápida com texto repetido ================"
# 4 blocos IGUAIS de 16 caracteres: no ECB eles geram 4 blocos cifrados iguais
printf 'BLOCO-IGUAL-1234BLOCO-IGUAL-1234BLOCO-IGUAL-1234BLOCO-IGUAL-1234' > repetido.txt
echo "--- ECB (cada linha = 1 bloco de 16 bytes cifrado)"
mostrar "openssl enc -aes-128-ecb -in repetido.txt -K \$(cat key.priv) | od -An -tx1 -w16"
echo "--- CBC"
mostrar "openssl enc -aes-128-cbc -in repetido.txt -K \$(cat key.priv) -iv \$(cat iv.txt) | od -An -tx1 -w16"

echo; echo "================ 4. Imagem do Tux ================"
if [ ! -f Tux.png ]; then
  mostrar "curl -L -A 'Mozilla/5.0' -o Tux.png https://upload.wikimedia.org/wikipedia/commons/a/af/Tux.png"
fi
mostrar "$PY imagem.py para-ppm Tux.png tux.ppm"
mostrar "head -n 3 tux.ppm > header.txt"
mostrar "tail -n +4 tux.ppm > body.bin"
mostrar "cat header.txt"

echo; echo "================ 5. Encriptação em cada modo ================"
for modo in ecb cbc cfb ofb ctr; do
  if [ "$modo" = "ecb" ]; then
    # ECB não usa IV
    mostrar "openssl enc -aes-128-$modo -in body.bin -K \$(cat key.priv) -out body.$modo.enc"
  else
    mostrar "openssl enc -aes-128-$modo -in body.bin -K \$(cat key.priv) -iv \$(cat iv.txt) -out body.$modo.enc"
  fi
  mostrar "cat header.txt body.$modo.enc > tux-$modo-enc.ppm"
  $PY imagem.py para-png tux-$modo-enc.ppm saida/tux-$modo-enc.png
done

echo; echo "================ 6. Resultados ================"
$PY imagem.py para-png tux.ppm saida/tux-original.png
mostrar "ls -l body.bin body.*.enc"
echo
echo "Blocos de 16 bytes repetidos em cada arquivo:"
$PY imagem.py analisar body.bin body.ecb.enc body.cbc.enc body.cfb.enc body.ofb.enc body.ctr.enc
$PY imagem.py montagem saida/comparacao.png original=saida/tux-original.png \
    ECB=saida/tux-ecb-enc.png CBC=saida/tux-cbc-enc.png CFB=saida/tux-cfb-enc.png \
    OFB=saida/tux-ofb-enc.png CTR=saida/tux-ctr-enc.png

echo
echo "Pronto! Abra a pasta 'saida' e veja as imagens (saida/comparacao.png junta todas)."
