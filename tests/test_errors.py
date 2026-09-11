def test_404_page(client):
    response = client.get("/this-page-does-not-exist")

    assert response.status_code == 404
    assert b"Page Not Found" in response.data
    assert b"Back to Dashboard" in response.data