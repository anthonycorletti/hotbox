from hotbox import gunicorn_conf


def test_gunicorn_settings() -> None:
    assert gunicorn_conf.worker_class == "uvicorn.workers.UvicornWorker"
    assert gunicorn_conf.port == 8420
    assert gunicorn_conf.bind == ":8420"
    assert gunicorn_conf.workers == 1
