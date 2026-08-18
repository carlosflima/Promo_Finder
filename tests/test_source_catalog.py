from app.search.source_catalog import SearchSource, SourceCatalog, SourceType


def test_catalog_keeps_store_and_marketplace_types():
    catalog = SourceCatalog([
        SearchSource("store.example", SourceType.STORE),
        SearchSource("market.example", SourceType.MARKETPLACE),
    ])
    assert [source.source_type for source in catalog.enabled()] == [SourceType.STORE, SourceType.MARKETPLACE]


def test_catalog_can_disable_and_enable_source():
    catalog = SourceCatalog([SearchSource("shop.example", SourceType.STORE)])
    catalog.disable("shop.example")
    assert catalog.enabled() == []
    catalog.enable("SHOP.EXAMPLE")
    assert len(catalog.enabled()) == 1
