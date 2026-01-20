from src import webserver

def test_home_endpoint():
    client = webserver.app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.data == b"Discord bot ok"