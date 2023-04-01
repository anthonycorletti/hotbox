from hotbox.services import HotboxService


class AppService(HotboxService):
    def __init__(self) -> None:
        super().__init__()

    def create_app_bundle(self) -> None:
        pass

    def upload_app_bundle(self) -> None:
        pass

    def create(self) -> None:
        pass

    def get(self) -> None:
        pass

    def delete(self) -> None:
        pass


app_svc = AppService()
