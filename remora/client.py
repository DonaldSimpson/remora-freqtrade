import requests
import os

class RemoraClient:

    def __init__(self, api_key: str | None = None):

        self.api_key = api_key or os.getenv("REMORA_API_KEY")

        if not self.api_key:

            raise ValueError("Remora API key missing. Set REMORA_API_KEY env var.")

        self.url = "https://api.remora-ai.com/context"

    def get_context(self, symbol: str):

        """

        Fetches real-time market context for a trading pair.

        Returns JSON dict:

            {

                "safe_to_trade": bool,

                "risk_score": float,

                "risk_class": str,

                "reasoning": [...],

                ...

            }

        """

        r = requests.get(

            self.url,

            params={"symbol": symbol},

            headers={"Authorization": f"Bearer {self.api_key}"},

            timeout=3,

        )

        r.raise_for_status()

        return r.json()

