import requests
import json
from itertools import product

def nicehash_price_info(coins):
    try:
        api = requests.get("https://api2.nicehash.com/exchange/api/v2/info/prices").text
    except:
        print("Could not get nicehash price info")
        return 0
    api = json.loads(api)
    exchanges = [exchange[0] for exchange in list(api.items())]
    exchanges = [list(_) + [api[''.join(_)]] for _ in product(coins, coins) if ''.join(_) in exchanges and _[1] not in ["EURS", "USDC"]] #thx stackoverflow

    prices = {"BTC": api["BTCUSDT"], "USDT": 1, "USDC": 1, "EURS": api["USDTEURS"]}
    prices.update({exchange[0]: exchange[2] * prices[exchange[1]] for exchange in exchanges})
    return prices

def nicehash_info():
    try:
        api = requests.get("https://api2.nicehash.com/main/api/v2/public/service/fee/info").text
    except:
        print("Could not get nicehash info")
    return json.loads(api)

nhinfo_full = nicehash_info()
nhinfo = nhinfo_full["withdrawal"]["BITGO"]["rules"]
nhinfo_coinbase = nhinfo_full["withdrawal"]["COINBASE"]["rules"]

coinlist = [coin["coin"] for coin in nhinfo.values()]

pricelist = nicehash_price_info(coinlist)

foundcoins = []
for coin in coinlist:
    try:
        print("Found", coin, "-", pricelist[coin], "USD")
        foundcoins.append(coin)
    except:
        print("Could not find", coin)

print("Found", len(foundcoins), "out of", len(coinlist), "coins.")
print("-"*32)

foundcoins = {
    coin: {
        "id": nhinfo[coin]["coin"],
        "price": float(pricelist[coin]),
        "minUSD": float(pricelist[coin]) * nhinfo[coin]["intervals"][0]["start"],
        "mincoin": nhinfo[coin]["intervals"][0]["start"],
        "fee": (nhinfo[coin]["intervals"][0]["element"]["value"], nhinfo[coin]["intervals"][0]["element"]["type"]),
        "sndfee": (nhinfo[coin]["intervals"][0]["element"]["sndValue"], nhinfo[coin]["intervals"][0]["element"]["sndType"])
    }
    for coin in foundcoins}

foundcoins["BTC (via Coinbase)"] = {
    "id": "BTC",
    "price": foundcoins["BTC"]["price"], 
    "minUSD": foundcoins["BTC"]["price"] * nhinfo_coinbase["BTC"]["intervals"][0]["start"],
    "mincoin": nhinfo_coinbase["BTC"]["intervals"][0]["start"],
    "fee": (nhinfo_coinbase["BTC"]["intervals"][0]["element"]["value"], nhinfo_coinbase["BTC"]["intervals"][0]["element"]["type"]),
    "sndfee": (0, 0)
}

for coin in sorted(foundcoins.items(), key=lambda x: x[1]["minUSD"], reverse=True):
    print(coin[0], "-", round(coin[1]["minUSD"], 2), "USD", "("+str(coin[1]["mincoin"]), coin[1]["id"] + ((" or " + str(round(coin[1]["minUSD"] / foundcoins["BTC"]["price"], 5)) + " BTC") if coin[1]["id"] != "BTC" else "") + ")", "losing", round(coin[1]["price"] * (coin[1]["mincoin"] * coin[1]["fee"][0] + coin[1]["sndfee"][0]), 2), "USD", "in fees")

input("Press Enter to quit.")