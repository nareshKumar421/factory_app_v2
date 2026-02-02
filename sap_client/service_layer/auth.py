import requests


class ServiceLayerSession:

    def __init__(self, sl_config: dict):
        self.sl = sl_config

    def login(self):
        response = requests.post(
            f"{self.sl['base_url']}/b1s/v2/Login",
            json={
                "CompanyDB": self.sl["company_db"],
                "UserName": self.sl["username"],
                "Password": self.sl["password"],
            },
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        return response.cookies
