from tqdm.auto import tqdm
from requests_html import HTMLSession


class Links:
    def __init__(self, log):
        self.session = HTMLSession()
        self.log = log

    def links_site(self, url):
        self.linksConfirmados = []
        self.rastrear(url)
        self.valida_404(self.linksConfirmados)
        return self.linksConfirmados

    def valida_url(self, url):
        return (
            True
            if "?" not in url
            and "#" not in url
            and ".jpg" not in url
            and ".JPG" not in url
            and ".jpeg" not in url
            and ".JPEG" not in url
            and ".png" not in url
            and ".PNG" not in url
            and "tel:" not in url
            and "mailto:" not in url
            else False
        )

    def rastrear(self, url):
        links = [url]

        for link in tqdm(links, unit=" links", desc=" Rastreando e categorizando os links", leave=False):
            try:
                r = self.session.get(link)
                links_pagina = r.html.absolute_links

            except Excpet as erro:
                self.log.append(f"{link} - ERRO: link não rastreado")

            else:
                for link_pagina in links_pagina:
                    if self.url_base(url) in link_pagina and self.valida_url(link_pagina):
                        if link_pagina not in links:
                            links.append(link_pagina)

        self.linksConfirmados = links.copy()

    def valida_404(self, links):
        for link in tqdm(links, unit=" links", desc=" Verificando se há links levando para página 404", leave=False):
        # for link in links:
            try:
                location = self.session.head(link).headers["Location"]

            except:
                continue

            else:
                if not location.endswith("/404"):
                    links.remove(link)

    def url_base(self, url, mpitemporario=False):
        url = url.split("//")
        url = url[1].split("/")
        url = url[0] if mpitemporario else [x for x in url if x][-1]
        return url.replace('www.', '')

