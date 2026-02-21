import functools
import json
import logging
import os
from typing import Protocol
from typing import TypedDict

import requests

type ItemIDRaw = str  # json requires string keys
type ItemPrice = int
type ItemPriceMap = dict[ItemIDRaw, ItemPrice]


class PriceManifest(TypedDict):
    last_update: int
    data: ItemPriceMap


class PriceProvider(Protocol):
    def load(self) -> PriceManifest | None: ...


class LocalPriceProvider:
    def __init__(self, filename):
        self.filename = filename

    def load(self) -> PriceManifest | None:
        filename = self.filename
        if not os.path.exists(filename):
            logging.warning(f"local prices not available. {filename} not found")
            return None
        logging.info("loading local prices from {filename}")
        with open(filename) as f:
            prices = json.load(f)
            return prices


class WebPriceProvider:
    def __init__(self, prices_server):
        self.prices_server = prices_server

    def load(self) -> PriceManifest | None:
        logging.info("loading web prices")
        prices = dl_price_data(prices_server=self.prices_server)
        return prices


@functools.cache
def dl_price_data(prices_server) -> PriceManifest | None:
    try:
        URLS = {
            "nord": "https://melbalabs.com/static/twowprices.json",
            "telabim": "https://melbalabs.com/static/twowprices-telabim.json",
            "ambershire": "https://raw.githubusercontent.com/whtmst/twow-ambershire-prices/refs/heads/main/ambershire-prices-filtered.json",
        }
        url = URLS[prices_server]
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data: PriceManifest = resp.json()
        return data
    except requests.exceptions.RequestException:
        logging.warning("web prices not available")
        return None
