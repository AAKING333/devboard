def test_secret_key_is_configured(app):
    assert app.config["SECRET_KEY"] is not None