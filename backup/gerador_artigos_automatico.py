import os
import re
from google import genai
from google.genai import types
from pydantic import BaseModel

# 1. Configuração da API
API_KEY = "AIzaSyDBFLmPPAN8IWFsL8KiiQEbwNnObCgrw0w"
client = genai.Client(api_key=API_KEY)

# Definimos a estrutura que a IA DEVE seguir para nos entregar os artigos
class ArtigoEstruturado(BaseModel):
    categoria: str
    titulo: str
    resumo_card: str
    conteudo_html_interno: str

class ListaDeArtigos(BaseModel):
    artigos: list[ArtigoEstruturado]

def gerar_lote_de_artigos(tema_central):
    """
    Pede à API para criar uma lista de artigos relevantes baseados no tema central,
    já estruturados para o banco de dados do Python.
    """
    prompt = f"""
    Você é o especialista principal em SEO e conteúdo do portal 'Guia do Útil'.
    Com base no tema central "{tema_central}", identifique os 3 assuntos/subtópicos mais relevantes e urgentes para o público em 2026.
    
    Para CADA um desses 3 assuntos, gere um artigo extremamente robusto, longo, com muito conteúdo escrito e aprofundado.
    
    Regras para o campo 'conteudo_html_interno':
    - Retorne APENAS as tags internas (<h2>, <h3>, <p>, <ul>, <ol>, <div class="alert alert-primary">).
    - Não inclua as tags estruturais <html>, <head> ou <body>.
    - Use títulos marcantes com classes do Bootstrap (ex: class="fw-bold mt-5 mb-3").
    - Inclua uma seção recomendando um produto ou infoproduto útil no meio do texto.
    """

    print(f"🤖 Analisando o tema central e expandindo para múltiplos artigos relevantes...")
    
    # Forçamos o Gemini a responder seguindo a estrutura do Pydantic
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ListaDeArtigos,
        ),
    )
    
    # A biblioteca oficial já converte o JSON automaticamente para nós
    return response.parsed

def criar_pagina_artigo_html(artigo, nome_arquivo, url_imagem):
    """
    Monta o arquivo HTML final completo do artigo na pasta correta.
    """
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

    <img src="{url_imagem}" class="img-banner" alt="{artigo.titulo}">

    {artigo.conteudo_html_interno}

    <div class="ad-space">PUBLICIDADE GOOGLE ADSENSE (RODAPÉ)</div>
</article>

<footer class="bg-light py-4 text-center">© 2026 Guia do Útil</footer>
</body>
</html>"""

    os.makedirs("artigo", exist_ok=True)
    caminho_completo = os.path.join("artigo", nome_arquivo)
    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"💾 Arquivo de artigo criado: {caminho_completo}")

def injetar_card_no_index(artigo, nome_arquivo, url_imagem):
    """
    Abre o index.html, localiza a linha correta de artigos e insere o novo card de forma automática.
    """
    caminho_index = "index.html"
    if not os.path.exists(caminho_index):
        print("⚠️ Erro: index.html não foi encontrado na pasta raiz.")
        return

    with open(caminho_index, "r", encoding="utf-8") as f:
        conteudo_index = f.read()

    # Define a cor do Badge do Bootstrap dependendo da categoria do assunto
    cor_badge = "bg-primary"
    cat_upper = artigo.categoria.upper()
    if "FINAN" in cat_upper or "ECONO" in cat_upper:
        cor_badge = "bg-success"
    elif "CASA" in cat_upper or "ORGANIZ" in cat_upper:
        cor_badge = "bg-warning text-dark"

    # Estrutura perfeita do Card baseada no seu design atual do Guia do Útil
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

    # Localiza o fechamento da linha de cards (<div class="row g-4"> ... </div>) para injetar o novo antes de fechar
    # Buscamos pela div de fechamento que antecede a section ou o fechamento da div container externa
    if '<div class="row g-4">' in conteudo_index:
        # Injeta logo após a abertura da row para novos artigos aparecerem no topo, ou antes do fechamento
        partes = conteudo_index.split('<div class="row g-4">')
        conteudo_atualizado = partes[0] + '<div class="row g-4">' + novo_card_html + partes[1]
        
        with open(caminho_index, "w", encoding="utf-8") as f:
            f.write(conteudo_atualizado)
        print(f"⚡ Card adicionado com sucesso ao index.html para: {artigo.titulo}")
    else:
        print("⚠️ Não foi possível encontrar a tag <div class="row g-4"> no seu index.html")

# --- EXECUÇÃO DO FLUXO ---
if __name__ == "__main__":
    # DIGITE O TEMA CENTRAL AQUI (O script vai destrinchar em múltiplos assuntos e criar um artigo para cada)
    tema_da_vez = "Automação residencial e Ferramentas Inteligentes para o Lar"
    
    # 1. Pede os múltiplos artigos estruturados para a IA
    dados_gerados = gerar_lote_de_artigos(tema_da_vez)
    
    # Banco de imagens estáticas do Unsplash de acordo com o tema para ilustrar lindamente
    imagens_sugestao = [
        "https://images.unsplash.com/photo-1558002038-1055907df827?auto=format&fit=crop&w=800&q=80", # Casa inteligente
        "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", # Interior moderno
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=800&q=80"  # Tecnologia aplicada
    ]

    # 2. Varre os artigos gerados pela IA, salva os arquivos e atualiza o site
    for idx, artigo in enumerate(dados_gerados.artigos):
        # Cria um nome limpo e seguro para o arquivo .html
        slug = re.sub(r'[^a-zA- Direct1-9]', '', artigo.titulo.lower()).replace(' ', '-')
        nome_arquivo_html = f"artigo-auto-{idx + 1}-{slug}.html"
        
        # Seleciona uma imagem da nossa lista de sugestões
        img_url = imagens_sugestao[idx % len(imagens_sugestao)]
        
        # Executa as ações automáticas
        criar_pagina_artigo_html(artigo, nome_arquivo_html, img_url)
        injetar_card_no_index(artigo, nome_arquivo_html, img_url)

    print("\n🚀 Todos os artigos foram criados e o index.html foi atualizado automaticamente!")
    print("👉 Agora é só rodar o 'salvar.bat' para enviar tudo para o ar no GitHub Pages!")