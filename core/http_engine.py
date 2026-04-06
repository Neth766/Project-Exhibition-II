import requests

class HTTPEngine:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, params):
        r = self.session.get(self.base_url, params=params)
        return {
            "status": r.status_code,
            "text": r.text,
            "length": len(r.text)
        }
