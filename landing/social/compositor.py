#!/usr/bin/env python3
"""
Compositor de posts Instagram — Atendente24h
Cena 3D base + texto via Pillow = zero erros de portugues
"""
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FONT_PATH = "/System/Library/Fonts/HelveticaNeue.ttc"
FONT_BLACK = 7   # HelveticaNeue Black/Bold variant
FONT_REG   = 0   # HelveticaNeue Regular

def add_gradient(img, height):
    """Adiciona gradiente escuro no rodape para o texto respirar."""
    arr = np.array(img).astype(np.float32)
    h, w = arr.shape[:2]
    gradient_start = int(h * 0.45)
    for y in range(gradient_start, h):
        alpha = min(1.0, (y - gradient_start) / (h - gradient_start) * 1.2)
        darkness = 1.0 - (alpha * 0.80)
        arr[y, :, :3] *= darkness
    return Image.fromarray(arr.astype(np.uint8))

def wrap_text(text, font, max_width, draw):
    """Quebra texto em linhas que cabem em max_width."""
    words = text.replace("\n", " \n ").split(" ")
    lines = []
    current = ""
    for word in words:
        if word == "\n":
            lines.append(current.strip())
            current = ""
            continue
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and current:
            lines.append(current.strip())
            current = word
        else:
            current = test
    if current.strip():
        lines.append(current.strip())
    return lines

def composite(scene_path, headline, suporte, output_path, width=1080, height=1350):
    # Abre e redimensiona a cena
    scene = Image.open(scene_path).convert("RGB")

    # Crop center para o aspect ratio correto
    sw, sh = scene.size
    target_ratio = width / height
    src_ratio = sw / sh

    if src_ratio > target_ratio:
        new_w = int(sh * target_ratio)
        x = (sw - new_w) // 2
        scene = scene.crop((x, 0, x + new_w, sh))
    else:
        new_h = int(sw / target_ratio)
        y = (sh - new_h) // 2
        scene = scene.crop((0, y, sw, y + new_h))

    scene = scene.resize((width, height), Image.LANCZOS)

    # Gradiente no rodape
    scene = add_gradient(scene, height)

    draw = ImageDraw.Draw(scene)

    padding = 60
    text_area_width = width - (padding * 2)

    # Fontes
    headline_size = int(width * 0.076)
    suporte_size  = int(width * 0.038)

    font_headline = ImageFont.truetype(FONT_PATH, headline_size, index=FONT_BLACK)
    font_suporte  = ImageFont.truetype(FONT_PATH, suporte_size,  index=FONT_REG)

    # Calcula altura do bloco de texto
    h_lines = wrap_text(headline, font_headline, text_area_width, draw)
    h_line_h = draw.textbbox((0, 0), "Ag", font=font_headline)[3]
    h_block_h = len(h_lines) * (h_line_h + 8)

    s_block_h = 0
    s_lines = []
    if suporte:
        s_lines = wrap_text(suporte, font_suporte, text_area_width, draw)
        s_line_h = draw.textbbox((0, 0), "Ag", font=font_suporte)[3]
        s_block_h = len(s_lines) * (s_line_h + 6) + 20  # 20px gap entre headline e suporte

    total_text_h = h_block_h + s_block_h
    bottom_margin = int(height * 0.065)
    text_y = height - bottom_margin - total_text_h

    # Desenha headline (branca)
    current_y = text_y
    for line in h_lines:
        draw.text((padding, current_y), line, font=font_headline, fill=(255, 255, 255))
        current_y += h_line_h + 8

    # Desenha suporte (branca 75%)
    if s_lines:
        current_y += 12
        for line in s_lines:
            draw.text((padding, current_y), line, font=font_suporte, fill=(191, 191, 191))
            current_y += s_line_h + 6

    scene.save(output_path, "PNG", optimize=True)
    print(f"  OK: {os.path.basename(output_path)}")
    return True


POSTS_DIR  = "/Users/eduardoarantes/agentes/atendimento24h/landing/social/posts"
SCENES_DIR = f"{POSTS_DIR}/scenes"

POSTS = [
    {
        "scene": f"{SCENES_DIR}/scene-moto.jpg",
        "headline": "Nunca para.\nNunca dorme.",
        "suporte": "Seu atendimento rodando enquanto voc\u00ea descansa.",
        "feed":  f"{POSTS_DIR}/feed-01.png",
        "story": f"{POSTS_DIR}/story-01.png",
        "caption": "Enquanto voc\u00ea dorme, seu bot est\u00e1 respondendo.\nAtendimento 24h no WhatsApp, a partir de R$197/m\u00eas.",
        "hashtags": "#atendente24h #botwhatsapp #automatizacaodevendas #whatsappbusiness #inteligenciaartificial #empreendedorismo #vendasonline #atendimentoaocliente #marketingdigital #startupbrasil",
    },
    {
        "scene": f"{SCENES_DIR}/scene-celular.jpg",
        "headline": "Ele responde.\nVoc\u00ea vende.",
        "suporte": "IA no WhatsApp, atendimento em segundos.",
        "feed":  f"{POSTS_DIR}/feed-02.png",
        "story": f"{POSTS_DIR}/story-02.png",
        "caption": "Cada mensagem respondida \u00e9 uma oportunidade de venda.\nO Atendente24h nunca deixa uma conversa sem resposta.",
        "hashtags": "#atendente24h #iaparaneg\u00f3cios #whatsappmarketing #bot #automatizacao #vendas #empreender #crescimentodigital #saas #tecnologiaparanegocios",
    },
    {
        "scene": f"{SCENES_DIR}/scene-pc.jpg",
        "headline": "247 respostas hoje.",
        "suporte": "Nenhuma digitada por voc\u00ea.",
        "feed":  f"{POSTS_DIR}/feed-03.png",
        "story": f"{POSTS_DIR}/story-03.png",
        "caption": "247 mensagens respondidas hoje. Zero digita\u00e7\u00f5es.\nIsso \u00e9 o que acontece quando voc\u00ea coloca a IA para trabalhar.",
        "hashtags": "#atendente24h #automacaodewhatsapp #whatsappbot #neg\u00f3ciodigital #produtividade #iabrasil #tecnologia #empreendedorismo #marketingdigital #resultados",
    },
    {
        "scene": f"{SCENES_DIR}/scene-cafe.jpg",
        "headline": "O neg\u00f3cio funciona.\nVoc\u00ea descansa.",
        "suporte": None,
        "feed":  f"{POSTS_DIR}/feed-04.png",
        "story": f"{POSTS_DIR}/story-04.png",
        "caption": "Liberdade de verdade: saber que o atendimento est\u00e1 rodando enquanto voc\u00ea toma um caf\u00e9.",
        "hashtags": "#atendente24h #liberdadefinanceira #empreendedor #whatsappautomatico #neg\u00f3ciosonline #botia #automatizacao #vidadeempreendedor #trabalhointeligente #iabrasil",
    },
    {
        "scene": f"{SCENES_DIR}/scene-thumbsup.jpg",
        "headline": "Cliente feliz.\nTodo dia.",
        "suporte": "Com ou sem voc\u00ea online.",
        "feed":  f"{POSTS_DIR}/feed-05.png",
        "story": f"{POSTS_DIR}/story-05.png",
        "caption": "Cliente satisfeito \u00e9 cliente que volta. E que indica.\nRespostas r\u00e1pidas mudam a percep\u00e7\u00e3o da sua marca.",
        "hashtags": "#atendente24h #satisfa\u00e7\u00e3odocliente #atendimentoaocliente #whatsappbot #ia #automatizacaocomercial #empreendedor #marketingdigital #crescimento #vendasonline",
    },
    {
        "scene": f"{SCENES_DIR}/scene-apontando.jpg",
        "headline": "Algu\u00e9m tentou\nte chamar agora.",
        "suporte": "Quantas mensagens voc\u00ea perdeu hoje?",
        "feed":  f"{POSTS_DIR}/feed-06.png",
        "story": f"{POSTS_DIR}/story-06.png",
        "caption": "Enquanto voc\u00ea l\u00ea isso, algu\u00e9m est\u00e1 tentando comprar de voc\u00ea no WhatsApp.\nO Atendente24h j\u00e1 respondeu.",
        "hashtags": "#atendente24h #whatsappvendas #n\u00e3opercastavendas #automacao #botwhatsapp #neg\u00f3cios #iacomercial #empreendedorismo #startupbr #atendimentoautomatico",
    },
    {
        "scene": f"{SCENES_DIR}/scene-correndo.jpg",
        "headline": "Mais r\u00e1pido que\nqualquer humano.",
        "suporte": "Resposta em segundos, 24 horas por dia.",
        "feed":  f"{POSTS_DIR}/feed-07.png",
        "story": f"{POSTS_DIR}/story-07.png",
        "caption": "Quem responde primeiro tem 80% de chance de fechar a venda.\nCom o Atendente24h, voc\u00ea responde em segundos. Sempre.",
        "hashtags": "#atendente24h #velocidadedevendas #botia #whatsappautomacao #vendas #empreender #automatizacao #respostar\u00e1pida #conversionrate #iabrasil",
    },
    {
        "scene": f"{SCENES_DIR}/scene-angulos.jpg",
        "headline": "Oi. Eu sou o\nAtendente24h.",
        "suporte": "Nunca durmo. Nunca perco uma mensagem.",
        "feed":  f"{POSTS_DIR}/feed-08.png",
        "story": f"{POSTS_DIR}/story-08.png",
        "caption": "Apresentando o Atendente24h: o atendente que nunca tira folga, nunca falta e custa menos que um dia de funcion\u00e1rio.",
        "hashtags": "#atendente24h #botwhatsapp #automatizacaocomercial #ia #iabrasil #empreendedorismo #whatsappbusiness #tecnologiaparanegocios #saas #atendimentointeligente",
    },
    {
        "scene": f"{SCENES_DIR}/scene-celebrando.jpg",
        "headline": "R$197 por m\u00eas.\nR$1.500 economizados.",
        "suporte": "Menos que um dia de funcion\u00e1rio. Atende o m\u00eas inteiro.",
        "feed":  f"{POSTS_DIR}/feed-09.png",
        "story": f"{POSTS_DIR}/story-09.png",
        "caption": "Contratou um atendente humano? R$1.500+ por m\u00eas. Com o Atendente24h? R$197. O mesmo resultado, sem ence cada de conta.",
        "hashtags": "#atendente24h #economiaparanegocios #automatizacao #whatsappbot #empreendedor #custobaixo #ia #negociosdigitais #saas #faturamento",
    },
    {
        "scene": f"{SCENES_DIR}/scene-split.jpg",
        "headline": "Antes: voc\u00ea.\nDepois: ele.",
        "suporte": "A virada que todo neg\u00f3cio precisa.",
        "feed":  f"{POSTS_DIR}/feed-10.png",
        "story": f"{POSTS_DIR}/story-10.png",
        "caption": "Antes: notifica\u00e7\u00f5es acumulando, clientes esperando, estresse constante. Depois: o bot resolve, voc\u00ea foca no que importa.",
        "hashtags": "#atendente24h #antesedepois #botwhatsapp #automatizacao #transformacaodigital #empreendedorismo #ia #liberdade #negociosonline #whatsappbusiness",
    },
    {
        "scene": f"{SCENES_DIR}/scene-relogio.jpg",
        "headline": "3h da manh\u00e3.\nBot no ar.",
        "suporte": "Enquanto voc\u00ea dorme, ele vende.",
        "feed":  f"{POSTS_DIR}/feed-11.png",
        "story": f"{POSTS_DIR}/story-11.png",
        "caption": "3h da manh\u00e3. Seu concorrente dorme. Seu atendente humano dorme. O Atendente24h? Respondendo e convertendo.",
        "hashtags": "#atendente24h #24horas #botwhatsapp #automatizacaodevendas #ia #empreendedor #whatsappmarketing #sempre ligado #saas #negociosonline",
    },
    {
        "scene": f"{SCENES_DIR}/scene-foguete.jpg",
        "headline": "Seu neg\u00f3cio\nna velocidade da IA.",
        "suporte": "Escale o atendimento sem escalar o custo.",
        "feed":  f"{POSTS_DIR}/feed-12.png",
        "story": f"{POSTS_DIR}/story-12.png",
        "caption": "Crescimento n\u00e3o deveria significar contratar mais. Com IA, voc\u00ea escala o atendimento sem escalar o custo.",
        "hashtags": "#atendente24h #crescimentodigital #ia #escalabilidade #whatsappbot #empreendedorismo #negociosonline #automatizacao #saas #tecnologia",
    },
    {
        "scene": f"{SCENES_DIR}/scene-estrelas.jpg",
        "headline": "5 estrelas\ntodo dia.",
        "suporte": "Resposta r\u00e1pida = cliente satisfeito = avalia\u00e7\u00e3o positiva.",
        "feed":  f"{POSTS_DIR}/feed-13.png",
        "story": f"{POSTS_DIR}/story-13.png",
        "caption": "Sabe por que alguns neg\u00f3cios t\u00eam 5 estrelas no Google? Respondem r\u00e1pido. O Atendente24h garante isso por voc\u00ea.",
        "hashtags": "#atendente24h #5estrelas #satisfa\u00e7\u00e3odocliente #avaliacao #botwhatsapp #ia #atendimentoaocliente #empreendedor #qualidade #whatsappbusiness",
    },
    {
        "scene": f"{SCENES_DIR}/scene-medalha.jpg",
        "headline": "Melhor atendimento\nda sua categoria.",
        "suporte": "Quem responde primeiro, fecha primeiro.",
        "feed":  f"{POSTS_DIR}/feed-14.png",
        "story": f"{POSTS_DIR}/story-14.png",
        "caption": "No mercado atual, velocidade de resposta \u00e9 diferencial competitivo. Seja o primeiro. Sempre.",
        "hashtags": "#atendente24h #diferencialcompetitivo #botwhatsapp #ia #vendas #empreendedor #automatizacao #whatsappmarketing #primeiro #negociosdigitais",
    },
    {
        "scene": f"{SCENES_DIR}/scene-dados.jpg",
        "headline": "Dados em tempo real.\nControle total.",
        "suporte": "Saiba exatamente o que est\u00e1 acontecendo no seu WhatsApp.",
        "feed":  f"{POSTS_DIR}/feed-15.png",
        "story": f"{POSTS_DIR}/story-15.png",
        "caption": "Quantas mensagens chegaram hoje? Quantas foram respondidas? Com o Atendente24h, voc\u00ea v\u00ea tudo no dashboard.",
        "hashtags": "#atendente24h #dashboard #dados #ia #whatsappbusiness #automatizacao #metricas #empreendedor #negociosonline #botwhatsapp",
    },
    {
        "scene": f"{SCENES_DIR}/scene-gigante.jpg",
        "headline": "Problema pequeno.\nSolu\u00e7\u00e3o grande.",
        "suporte": "Mensagens acumulando? Nunca mais.",
        "feed":  f"{POSTS_DIR}/feed-16.png",
        "story": f"{POSTS_DIR}/story-16.png",
        "caption": "O WhatsApp n\u00e3o para. As mensagens n\u00e3o param. Mas agora voc\u00ea tem algo maior do que o problema.",
        "hashtags": "#atendente24h #solucao #botwhatsapp #ia #empreendedor #automatizacaowhatsapp #vendas #negociosonline #whatsappmarketing #saas",
    },
    {
        "scene": f"{SCENES_DIR}/scene-descansando.jpg",
        "headline": "Voc\u00ea descansa.\nEle trabalha.",
        "suporte": "Atendimento acontece mesmo quando voc\u00ea est\u00e1 offline.",
        "feed":  f"{POSTS_DIR}/feed-17.png",
        "story": f"{POSTS_DIR}/story-17.png",
        "caption": "Feriado, final de semana, 23h de uma sexta. O Atendente24h n\u00e3o conhece essas palavras.",
        "hashtags": "#atendente24h #finalesemana #botwhatsapp #ia #empreendedor #liberdade #automatizacao #24horas #negociosonline #whatsappbot",
    },
    {
        "scene": f"{SCENES_DIR}/scene-whatsapp.jpg",
        "headline": "Zero mensagens\npendentes.",
        "suporte": "Todos os clientes respondidos. Toda hora.",
        "feed":  f"{POSTS_DIR}/feed-18.png",
        "story": f"{POSTS_DIR}/story-18.png",
        "caption": "Inbox zerado. Clientes satisfeitos. Vendas no piloto autom\u00e1tico. \u00c9 isso que o Atendente24h entrega.",
        "hashtags": "#atendente24h #inboxzero #botwhatsapp #ia #whatsappbusiness #automatizacao #vendas #empreendedor #atendimentointeligente #negociosonline",
    },
    {
        "scene": f"{SCENES_DIR}/scene-apresentando.jpg",
        "headline": "Pronto para\ncome\u00e7ar agora.",
        "suporte": "Configura\u00e7\u00e3o em minutos. Sem instalar nada.",
        "feed":  f"{POSTS_DIR}/feed-19.png",
        "story": f"{POSTS_DIR}/story-19.png",
        "caption": "Sem instalar nada. Sem contratar ningu\u00e9m. S\u00f3 acessar, configurar e ligar. Seu atendente IA est\u00e1 pronto em minutos.",
        "hashtags": "#atendente24h #facildeusur #botwhatsapp #ia #saas #empreendedor #automatizacao #configuracaorapida #negociosonline #whatsappbusiness",
    },
]

if __name__ == "__main__":
    for p in POSTS:
        if not os.path.exists(p["scene"]):
            print(f"  CENA AUSENTE: {p['scene']}")
            continue
        print(f"\n{p['feed']}...")
        composite(p["scene"], p["headline"], p["suporte"], p["feed"], 1080, 1350)
        composite(p["scene"], p["headline"], p["suporte"], p["story"], 1080, 1920)

    print("\nConcluido.")
