import re

import dataset
import get_retries
from bs4 import BeautifulSoup
from dateutil import parser

db = dataset.connect("sqlite:///data.sqlite")

tab_incidents = db["incidents"]
tab_sources = db["sources"]
tab_chronicles = db["chronicles"]

# https://stackoverflow.com/a/7160778/4028896
def is_url(s):
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, s) is not None


tab_chronicles.upsert(
    {
        "iso3166_1": "DE",
        "iso3166_2": "DE-HB",
        "chronicler_name": "Keine Randnotiz",
        "chronicler_description": "keine-randnotiz.de ist ein unabhängiges Dokumentations- und Webprojekt von soliport - Betroffene rechter, rassistischer und antisemitischer Gewalt solidarisch beraten und unterstützen und des Mobilen Beratungsteams gegen Rechtsextremismus in Bremen und Bremerhaven (MBT).",
        "chronicler_url": "https://keine-randnotiz.de",
        "chronicle_source": "https://keine-randnotiz.de",
    },
    ["chronicler_name"],
)


url = "https://keine-randnotiz.de/api/incidents"

json_data = get_retries.get(url, verbose=True, max_backoff=128).json()


for x in json_data:
    data = dict(
        (k, x[k])
        for k in ("title", "city", "postal_code", "state", "latitude", "longitude")
    )
    data["chronicler_name"] = "Keine Randnotiz"
    data["rg_id"] = "keinerandnotiz-" + str(x["id"])
    data["date"] = parser.parse(x["date"])
    data["url"] = "https://keine-randnotiz.de"

    if data["date"] is None:
        print(x)

    introduction = (
        BeautifulSoup(x["introduction"], "lxml").get_text(separator="\n").strip()
    )

    body = BeautifulSoup(x["content"], "lxml")

    sources = []
    real_body = ""
    for st in body.strings:
        st = str(st)
        if st.startswith("Quelle:"):
            st = st.replace("Quelle:", "").strip()
            st_st = st.split()[0]
            if is_url(st_st):
                sources.append({"url": st_st, "name": st, "rg_id": data["rg_id"]})
            else:
                sources.append({"name": st, "rg_id": data["rg_id"]})
        else:
            real_body += "\n" + st.strip()

    # data['sources'] = sources
    data["description"] = introduction + "\n" + real_body

    data["address"] = x["address_line_1"]

    motives = []
    factums = []
    for tag in x["tags"]:
        if tag["type"] == "Kategorie":
            motives.append(tag["name"]["de"])
        elif tag["type"] == "Art":
            factums.append(tag["name"]["de"])
        else:
            # no other tags used
            print(tag)

    data["motives"] = ", ".join(motives)
    data["factums"] = ", ".join(factums)

    # print(data, sources)
    # print(motives, factums)

    # is None, always
    # print(x["address_line_2"])

    tab_incidents.upsert(data, ["rg_id"])

    for s in sources:
        tab_sources.upsert(s, ["rg_id", "name", "url"])
