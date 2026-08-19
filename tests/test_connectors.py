from app.search.connectors import ConnectorResponse, execute_connector


class GoodConnector:
    def search(self, query):
        return []


class BadConnector:
    def search(self, query):
        raise RuntimeError("source unavailable")


def test_connector_success_is_normalized():
    response = execute_connector(GoodConnector(), "notebook")
    assert isinstance(response, ConnectorResponse)
    assert response.error is None


def test_connector_failure_does_not_escape():
    response = execute_connector(BadConnector(), "notebook")
    assert response.results == []
    assert response.error.startswith("connector error:")
