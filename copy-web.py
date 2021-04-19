import re
import os
from requests_html import HTMLSession
from Class.Links import Links
from Class.Assets import Assets
from tqdm.auto import tqdm


log = []

site = ""


links = Links(log)
assets = Assets(site, log)

links_do_site = links.links_site(site)
links_do_site.append(f"{site}/404")

def clone(links_do_site):
    session = HTMLSession()

    for pagina in tqdm(links_do_site):
        assets.imagens(pagina)
        assets.file_head(pagina)
        assets.download_file(pagina)

clone(links_do_site)