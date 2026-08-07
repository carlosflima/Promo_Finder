# -*- coding: utf-8 -*-
"""Configurações centrais do Agente de Promoções."""

MIN_DISCOUNT_PERCENT = 25
AUTO_REFRESH_MINUTES = 30
MAX_ITEMS_PER_SITE = 40
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
REQUEST_TIMEOUT = 12
REQUEST_DELAY = 1.5
RESOLVE_EXTERNAL_LINKS = True
RESOLVE_TIMEOUT = 6
MAX_RESOLUTIONS_PER_AGENT = 40
ENABLE_GOOGLE_SHOPPING = True
SEARCH_QUERIES = [
    "smart tv 4k oferta",
    "smartphone promoção",
    "notebook oferta",
    "fone de ouvido bluetooth oferta",
    "air fryer oferta",
    "geladeira frost free oferta",
    "tênis esportivo promoção",
    "perfume importado oferta",
]
DATA_DIR = "data"
CACHE_FILE = f"{DATA_DIR}/products.json"
HISTORY_DIR = f"{DATA_DIR}/historico"
CATEGORY_KEYWORDS = {
    "Eletrônicos": ["celular", "smartphone", "iphone", "tv", "notebook", "tablet", "fone", "smartwatch", "câmera", "monitor", "console", "playstation", "xbox", "caixa de som", "carregador", "hd ", "ssd"],
    "Eletrodomésticos": ["geladeira", "fogão", "micro-ondas", "lava", "aspirador", "ventilador", "ar-condicionado", "ar condicionado", "liquidificador", "airfryer", "air fryer", "cafeteira", "panela"],
    "Moda": ["camisa", "camiseta", "calça", "vestido", "tênis", "sapato", "bolsa", "jaqueta", "blusa", "short", "saia", "sandália", "relógio"],
    "Casa e Decoração": ["sofá", "mesa", "cadeira", "cama", "colchão", "cortina", "tapete", "luminária", "travesseiro", "organizador"],
    "Beleza e Saúde": ["perfume", "maquiagem", "shampoo", "creme", "hidratante", "batom", "protetor solar", "suplemento", "vitamina"],
    "Games": ["jogo", "game", "gamer", "controle", "headset gamer", "cadeira gamer"],
    "Bebês e Crianças": ["fralda", "brinquedo", "carrinho de bebê", "berço", "mamadeira"],
    "Esporte e Lazer": ["bicicleta", "bike", "academia", "musculação", "camping", "mochila", "suplemento esportivo"],
    "Livros e Papelaria": ["livro", "caderno", "mochila escolar", "caneta"],
    "Ferramentas": ["furadeira", "parafusadeira", "serra", "chave de fenda", "ferramenta"],
}
DEFAULT_CATEGORY = "Outros"
