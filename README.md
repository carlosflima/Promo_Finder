# Promo_Finder

Primeira versão do agente de pesquisa de promoções em Python + Flask.

## Executar no Windows

1. Instale Python 3.10+.
2. Execute `iniciar.bat`.
3. O script cria o ambiente virtual, instala as dependências e abre `http://127.0.0.1:5000`.

## Estrutura

```text
Promo_Finder/
├── agents/
│   ├── scraper.py
│   └── categorizer.py
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/index.html
├── utils/pdf_export.py
├── app.py
├── config.py
├── requirements.txt
└── iniciar.bat
```

## Recursos desta primeira versão

- Dashboard web.
- Coleta em fontes públicas de promoções e lojas.
- Classificação automática por categoria.
- Filtro por desconto.
- Atualização manual e agendada.
- Cache local em JSON.
- Exportação para PDF.
- Links para a oferta original.
- Fallback demonstrativo quando as fontes não respondem.

## Próxima fase

A próxima versão será a refatoração do núcleo, com Search Engine desacoplado, plugins de lojas, persistência estruturada, pesquisa por produto, CEP/frete, comparação por colunas, histórico e otimização de carrinho.

> Antes de usar scraping em produção, respeite os termos de uso e robots.txt de cada site. APIs oficiais e programas de afiliados devem ser priorizados quando disponíveis.
