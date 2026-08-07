# Promo_Finder — arquitetura v0.2

A segunda versão começa a separar o núcleo de pesquisa da aplicação Flask legada.

## Camadas

- `app/core`: configuração e primitivas compartilhadas.
- `app/search`: modelos, normalização, ranking e orquestração paralela.
- `agents`: compatibilidade com os coletores existentes; será migrado gradualmente para plugins.
- `tests`: testes automatizados do novo núcleo.

## Regras do Search Engine

1. Um erro em uma fonte não interrompe a pesquisa das demais.
2. Termos são normalizados antes da busca.
3. Resultados duplicados são removidos.
4. Resultados são ordenados pelo custo total quando o frete está disponível.
5. O limite padrão é de cinco resultados por site.
6. O motor não depende do Flask e poderá ser reutilizado por API, interface web ou futuros clientes.

## Próximas etapas

- Interface de plugin para lojas.
- Adaptador de busca por site com URL e termos configuráveis.
- CEP e cálculo de frete.
- Persistência SQLAlchemy.
- Histórico de preços.
- Marketplaces e agrupamento por vendedor.
