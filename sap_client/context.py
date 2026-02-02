from .registry import get_company_config


class CompanyContext:
    """
    Holds SAP configuration for ONE company
    """

    def __init__(self, company_code: str):
        self.company_code = company_code
        self.config = get_company_config(company_code)

    @property
    def hana(self):
        return self.config["hana"]

    @property
    def service_layer(self):
        return self.config["service_layer"]
