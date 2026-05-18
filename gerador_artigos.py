import os
from google import genai
from google.genai import types

# 1. Configuração da API (Chave configurada corretamente)
API_KEY = "AIzaSyDBFLmPPAN8IWFsL8KiiQEbwNnObCgrw0w" 
client = genai.Client(api_key=API_KEY)

def gerar_artigo_completo(tema, palavra_chave_imagem):
    """
    Gera um artigo HTML completo, estruturado com Bootstrap, pronto para o Guia do Útil.
    """
    
    prompt = f"""
    Atue como um redator profissional de SEO e Copywriting para o portal 'Guia do Útil'.
    Gere um artigo extremamente completo, detalhado, com muito conteúdo escrito e bem aprofundado sobre o tema: "{tema}".
    
    O retorno deve ser APENAS o código HTML de dentro do artigo (não inclua as tags <html>, <head> ou <body>, apenas as tags de estrutura interna).
    
    Siga rigidamente estas regras de formatação:
    1. Use títulos marcantes (<h2>, <h3>) com classes do Bootstrap (ex: class="fw-bold mt-5 mb-3").
    2. Escreva parágrafos longos, explicativos e ricos em informação (<p class="lead" ou class="text-muted").
    3. Inclua listas estruturadas (<ul> ou <ol>) e caixas de destaque utilizando os alertas do Bootstrap (ex: <div class="alert alert-primary">).
    4. Crie uma seção de recomendação de infoproduto ou produto físico relacionado ao tema no meio do artigo.
    """

    print(f"🤖 Gerando artigo aprofundado sobre: {tema}...")
    
    # Ajustado para usar o identificador aceito pela API do Google
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    conteudo_html = response.text
    
    # 2. Imagem dinâmica via Unsplash (Alta Resolução)
    url_imagem = "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80" 

    # 3. Montando a estrutura final com o padrão visual do Guia do Útil
    html_final = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tema} | Guia do Útil</title>
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
    <h1 class="fw-800 display-4 mb-4">{tema}</h1>
    
    <div class="ad-space">PUBLICIDADE GOOGLE ADSENSE (TOPO)</div>

    <img src="{url_imagem}" class="img-banner" alt="{tema}">

    {conteudo_html}

    <div class="ad-space">PUBLICIDADE GOOGLE ADSENSE (RODAPÉ)</div>
</article>

<footer class="bg-light py-4 text-center">© 2026 Guia do Útil</footer>
</body>
</html>"""

    return html_final

# --- CONFIGURAÇÃO DO TEMA ---
if __name__ == "__main__":
    tema_artigo = "O Impacto da Inteligência Artificial na Automação de Processos em 2026"
    termo_imagem = "technology" 
    
    artigo_pronto = gerar_artigo_completo(tema_artigo, termo_imagem)
    
    os.makedirs("artigo", exist_ok=True)
    
    nome_arquivo = "artigo/artigo-automacao-ia.html"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(artigo_pronto)
        
    print(f"✨ Sucesso! Artigo salvo com muito conteúdo em: {nome_arquivo}")