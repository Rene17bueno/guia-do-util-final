import os
import re
import tkinter as tk
from tkinter import simpledialog, messagebox
from google import genai
from google.genai import types
from pydantic import BaseModel

# 1. Configuração Segura da API do Gemini
# O Python agora busca a chave de forma oculta e protegida diretamente no seu Windows
client = genai.Client()

# Estrutura de dados para garantir o retorno perfeito da IA
class ArtigoEstruturado(BaseModel):
    categoria: str
    titulo: str
    resumo_card: str
    termo_imagem_principal: str  # Termo em inglês para a foto de capa
    termo_imagem_corpo: str      # Termo em inglês para a foto do meio do texto
    conteudo_html_interno: str

class ListaDeArtigos(BaseModel):
    artigos: list[ArtigoEstruturado]

def gerar_lote_de_artigos(tema_central):
    """Pedi à API para criar 3 artigos relevantes com base no tema digitado."""
    prompt = f"""
    Você é o especialista principal em SEO e conteúdo do portal 'Guia do Útil'.
    Com base no tema central dado pelo usuário: "{tema_central}", identifique os 3 subassuntos/tópicos mais relevantes e distintos em 2026.
    
    Para CADA um desses 3 subassuntos, gere um artigo longo, aprofundado e rico em conteúdo descritivo.
    
    No campo 'termo_imagem_principal', dê 1 palavra em inglês para a imagem de capa (ex: 'kitchen', 'workspace').
    No campo 'termo_imagem_corpo', dê outra palavra em inglês relacionada para a imagem do meio do texto (ex: 'tools', 'gadget').
    
    Regras para o campo 'conteudo_html_interno':
    - Retorne APENAS as tags de texto internas (<h2>, <h3>, <p>, <ul>, <ol>, <div class="alert alert-primary">).
    - Não inclua as tags estruturais <html>, <head> ou <body>.
    - Use títulos marcantes com classes do Bootstrap (ex: class="fw-bold mt-5 mb-3").
    - Inclua uma seção recomendando um produto ou infoproduto útil no meio do texto.
    """

    print(f"🤖 Conectando de forma segura ao Gemini... Analisando o tema '{tema_central}'...")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ListaDeArtigos,
        ),
    )
    return response.parsed

def criar_pagina_artigo_html(artigo, nome_arquivo, img_capa, img_corpo):
    """Monta a página HTML final do artigo injetando dinamicamente as duas imagens."""
    
    # Dividimos o conteúdo inserido pela IA para injetar a segunda imagem bem no meio do texto
    paragrafos = artigo.conteudo_html_interno.split('</p>')
    meio = len(paragrafos) // 2
    
    if len(paragrafos) > 2:
        # Injeta uma imagem responsiva com bordas arredondadas e sombra no meio do artigo
        tag_imagem_corpo = f'\n<img src="{img_corpo}" class="img-fluid rounded-4 my-4 shadow-sm" style="width: 100%; max-height: 380px; object-fit: cover;" alt="Conteúdo complementar">\n'
        paragrafos.insert(meio, tag_imagem_corpo)
        conteudo_final_html = "</p>".join(paragrafos)
    else:
        conteudo_final_html = artigo.conteudo_html_interno

    html_template = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{artigo.titulo} | Guia do Útil</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #2d3436; }}
        .container-article {{ max-width: 800px; margin: 40px auto; padding: 20px; }}
        .img-banner {{ width: 100%; max-height: 450px; object-fit: cover; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 30px 0; }}
        .ad-space {{ background: #f1f2f6; border: 1px dashed #ccc; padding: 30px; text-align: center; margin: 30px 0; border-radius: 15px; color: #999; }}
    </style>
</head>
<body>

<nav class="navbar navbar-light bg-white border-bottom">
    <div class="container"><a class="navbar-brand fw-bold" href="../index.html">← Voltar ao GUIA DO ÚTIL</a></div>
</nav>

<article class="container-article">
    <h1 class="fw-800 display-4 mb-4">{artigo.titulo}</h1>
    
    <div class="ad-space">PUBLICIDADE GOOGLE ADSENSE (TOPO)</div>

    <img src="{img_capa}" class="img-banner" alt="{artigo.titulo}">

    {conteudo_final_html}

    <div class="ad-space">PUBLICIDADE GOOGLE ADSENSE (RODAPÉ)</div>
</article>

<footer class="bg-light py-4 text-center">© 2026 Guia do Útil</footer>
</body>
</html>"""

    os.makedirs("artigo", exist_ok=True)
    caminho_completo = os.path.join("artigo", nome_arquivo)
    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write(html_template)

def injetar_card_no_index(artigo, nome_arquivo, url_imagem):
    """Injeta de forma automatizada o card correspondente na home."""
    caminho_index = "index.html"
    if not os.path.exists(caminho_index):
        return

    with open(caminho_index, "r", encoding="utf-8") as f:
        conteudo_index = f.read()

    cor_badge = "bg-primary"
    cat_upper = artigo.categoria.upper()
    if "FINAN" in cat_upper or "ECONO" in cat_upper:
        cor_badge = "bg-success"
    elif "CASA" in cat_upper or "ORGANIZ" in cat_upper or "DECOR" in cat_upper:
        cor_badge = "bg-warning text-dark"

    novo_card_html = f"""
        <div class="col-md-6 col-lg-4">
            <div class="card-topic">
                <img src="{url_imagem}" class="w-100" style="aspect-ratio: 16/9; object-fit: cover;" alt="{artigo.titulo}">
                <div class="p-4">
                    <span class="badge {cor_badge} mb-2">{artigo.categoria.upper()}</span>
                    <h4 class="fw-bold">{artigo.titulo}</h4>
                    <p class="text-muted small">{artigo.resumo_card}</p>
                    <a href="artigo/{nome_arquivo}" class="btn-main">Ler Artigo Completo</a>
                </div>
            </div>
        </div>"""

    if '<div class="row g-4">' in conteudo_index:
        partes = conteudo_index.split('<div class="row g-4">')
        conteudo_updated = partes[0] + '<div class="row g-4">' + novo_card_html + partes[1]
        with open(caminho_index, "w", encoding="utf-8") as f:
            f.write(conteudo_updated)

def iniciar_interface():
    """Gera a interface gráfica para capturar o tema desejado."""
    root = tk.Tk()
    root.withdraw() 
    
    tema_usuario = simpledialog.askstring(
        "Guia do Útil - Gerador Protegido", 
        "Qual o assunto principal para a IA pesquisar e trabalhar hoje?"
    )
    
    if tema_usuario:
        try:
            dados_gerados = gerar_lote_de_artigos(tema_usuario)
            
            for idx, artigo in enumerate(dados_gerados.artigos):
                slug = re.sub(r'[^a-zA-Z0-9 ]', '', artigo.titulo.lower()).replace(' ', '-')
                nome_arquivo_html = f"artigo-auto-{idx + 1}-{slug}.html"
                
                # Definição dos termos de imagem gerados pela IA
                termo_1 = artigo.termo_imagem_principal if artigo.termo_imagem_principal else "lifestyle"
                termo_2 = artigo.termo_imagem_corpo if artigo.termo_imagem_corpo else "technology"
                
                # Links de imagens dinâmicas do Unsplash baseadas no assunto real
                img_capa = f"https://images.unsplash.com/featured/1200x630/?{termo_1}&sig={idx}"
                img_corpo = f"https://images.unsplash.com/featured/800x500/?{termo_2}&sig={idx+10}"
                
                # Executa a geração das páginas e atualização da home
                criar_pagina_artigo_html(artigo, nome_arquivo_html, img_capa, img_corpo)
                injetar_card_no_index(artigo, nome_arquivo_html, img_capa)
            
            messagebox.showinfo("Sucesso!", "Perfeito! Os 3 artigos com múltiplas imagens por página foram gerados com sucesso e o index.html atualizado!")
            
        except Exception as e:
            messagebox.showerror("Erro de Processamento", f"Ocorreu um detalhe técnico:\n{str(e)}")
    else:
        print("Operação cancelada.")

if __name__ == "__main__":
    iniciar_interface()