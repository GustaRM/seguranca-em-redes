"""
Ferramentas de imagem para a Prática de Modos de Operação (Tux).

Por que isto existe? O roteiro usa o comando "convert" (ImageMagick), que no
Windows costuma não existir (e o "convert.exe" do Windows é outra coisa!).
Este script faz o mesmo trabalho só com Python + Pillow (pip install pillow).

Comandos:
  python imagem.py para-ppm  entrada.png saida.ppm
  python imagem.py para-png  entrada.ppm saida.png
  python imagem.py analisar  arq1 [arq2 ...]
  python imagem.py montagem  saida.png rotulo=arquivo.png [rotulo=arquivo.png ...]

Formato PPM (P6): cabeçalho de 3 linhas ("P6", "largura altura", "255")
seguido dos pixels crus (3 bytes por pixel: R, G, B). Como o cabeçalho tem
sempre 3 linhas, dá para separá-lo com "head -n 3" e "tail -n +4", como no roteiro.
"""

import sys
from collections import Counter
from PIL import Image, ImageDraw


def png_para_ppm(entrada, saida):
    img = Image.open(entrada)
    # O Tux tem fundo transparente. O PPM não tem transparência, então
    # colocamos a imagem sobre um fundo branco.
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        fundo = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(fundo, img)
    img = img.convert("RGB")
    largura, altura = img.size
    with open(saida, "wb") as f:
        f.write(f"P6\n{largura} {altura}\n255\n".encode())  # cabeçalho: 3 linhas
        f.write(img.tobytes())                               # pixels crus
    print(f"{saida}: {largura}x{altura} pixels")


def ppm_para_png(entrada, saida):
    with open(entrada, "rb") as f:
        dados = f.read()
    # separa as 3 linhas do cabeçalho do resto (o corpo pode ter bytes "\n")
    _, dimensoes, _, corpo = dados.split(b"\n", 3)
    largura, altura = map(int, dimensoes.split())
    esperado = largura * altura * 3
    # Nos modos ECB e CBC o OpenSSL acrescenta padding (até 16 bytes a mais):
    # ignoramos o excesso. Se faltar, completamos com zeros.
    corpo = corpo[:esperado].ljust(esperado, b"\x00")
    Image.frombytes("RGB", (largura, altura), corpo).save(saida)
    print(f"{saida} gerado")


def analisar(arquivos):
    """Conta blocos de 16 bytes repetidos: a 'impressão digital' do ECB."""
    print(f"{'Arquivo':<22}{'Blocos':>9}{'Distintos':>11}{'Repetidos':>11}{'% repet.':>10}")
    for caminho in arquivos:
        with open(caminho, "rb") as f:
            dados = f.read()
        blocos = [dados[i:i + 16] for i in range(0, len(dados) - 15, 16)]
        distintos = len(set(blocos))
        repetidos = len(blocos) - distintos
        pct = 100 * repetidos / len(blocos) if blocos else 0
        print(f"{caminho:<22}{len(blocos):>9}{distintos:>11}{repetidos:>11}{pct:>9.1f}%")


def montagem(saida, itens):
    """Junta várias imagens lado a lado, com um rótulo em cima de cada uma."""
    imagens = []
    for item in itens:
        rotulo, caminho = item.split("=", 1)
        imagens.append((rotulo, Image.open(caminho).convert("RGB")))
    larg = max(i.width for _, i in imagens)
    alt = max(i.height for _, i in imagens)
    topo = 24
    tela = Image.new("RGB", (larg * len(imagens), alt + topo), "white")
    desenho = ImageDraw.Draw(tela)
    for n, (rotulo, img) in enumerate(imagens):
        tela.paste(img, (n * larg, topo))
        desenho.text((n * larg + 6, 6), rotulo, fill="black")
    tela.save(saida)
    print(f"{saida} gerado")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "para-ppm" and len(sys.argv) == 4:
        png_para_ppm(sys.argv[2], sys.argv[3])
    elif cmd == "para-png" and len(sys.argv) == 4:
        ppm_para_png(sys.argv[2], sys.argv[3])
    elif cmd == "analisar" and len(sys.argv) >= 3:
        analisar(sys.argv[2:])
    elif cmd == "montagem" and len(sys.argv) >= 4:
        montagem(sys.argv[2], sys.argv[3:])
    else:
        print(__doc__)
        sys.exit(1)
