import os
import re
from requests_html import HTMLSession


class Assets:
    def __init__(self, url_base, log):
        self.session = HTMLSession()
        self.log = log
        self.url_base = url_base
        self.raiz = url_base.split('/')[2].replace('www.', '')

    #Validar se o code é 200 antes de baixar o arquivo (Pendente)
    def imagens(self, url):
        r = self.session.get(url)
        imagens = r.html.xpath('//img/@src')
        for img in imagens:
            try:
                img_thumbs = f'(h.*)?inc/scripts/thumbs.php\?w=(.*?)&(amp;)?h=(.*?)\&(amp;)?imagem='
                img_tim = f'(h.*)?tim\.php\?src='
                img = re.sub(f'({img_thumbs}|{img_tim})', r'', img)

                if "?" in img:
                    img = img.split('?')[0]

                if "&" in img:
                    img = img.split('&')[0]

                img_local = img.replace(self.url_base, '')

                if not os.path.isfile(img_local):
                    diretorio = img_local.split('/')[:-1]

                    if not os.path.isdir(f"{self.raiz}/{'/'.join(diretorio)}"):
                        os.makedirs(f"{self.raiz}/{'/'.join(diretorio)}")

                    with open(f"{self.raiz}/{img_local}", "wb") as arquivo:
                        arquivo.write(self.session.get(img).content)

            except:
                self.log.append(f'Não foi possível baixar a imagem: {img}')


    def file_head(self, url):
        r = self.session.get(url)
        head_links = r.html.xpath('//link/@href | //script/@src')
        links_js = re.findall('script\([\'\"](.*?)[\'\"]\)\.wait', r.html.html)
        links_in_css = re.findall('url\([\'"]?(.*?)[\'"]?\)', r.html.html)

        scanner_file_css = [x for x in head_links if ".css" in x]
        for file in scanner_file_css:
            try:
                if not "http" in file:
                    file = f"{self.url_base}{file}"

                css = self.session.get(file)
                path_in_css = re.findall('url\([\'"]?(.*?)[\'"]?\)', css.html.html)
                path_in_css = [re.sub(r'<\?=.*?\?>', r'', x) for x in path_in_css]
                [head_links.append(x) for x in path_in_css]

            except:
                self.log.append(f"Não foi possível baixar o arquivo {file} ")

        [head_links.append(x) for x in links_in_css]
        [head_links.append(x) for x in links_js]
        [head_links.remove(x) for x in head_links if 'http' in x and not self.raiz in x]  
        head_links.remove(url) if url in head_links else None
        
        head_links = [x for x in head_links if not "flags/" in x]

        for head_link in head_links:
            try:
                head_link = head_link.replace('../', '')
                local = re.sub(f'.*?{self.raiz}/', r'', head_link)
                if "?" in local:
                    local = local.split('?')[0]

                if not os.path.isfile(local) and len(local) > 0:
                    diretorio = local.split('/')[:-1]

                    if not os.path.isdir(f"{self.raiz}/{'/'.join(diretorio)}"):
                        os.makedirs(f"{self.raiz}/{'/'.join(diretorio)}")

                    if not "http" in head_link:
                        head_link = f"{self.url_base}{head_link}"

                    if not self.is_404(f'{self.url_base}{local}'):
                        with open(f"{self.raiz}/{local}", "wb") as arquivo:
                            arquivo.write(self.session.get(head_link).content)
            except:
                self.log.append(f"Não foi possível baixar o arquivo {head_link} ")


    def download_file(self, url):
        try:
            name_page = url.replace(self.url_base, '') if  url != self.url_base else "index"
            if "?" in name_page:
                name_page = name_page.split('?')[0]

            if not os.path.isfile(name_page) and len(name_page) > 0:
                diretorio = name_page.split('/')[:-1]

            if not os.path.isdir(f"{self.raiz}/{'/'.join(diretorio)}"):
                os.makedirs(f"{self.raiz}/{'/'.join(diretorio)}")
            
            r = self.session.get(url)
            html = r.html.html
            url_regex = f"(http://|https://)?(www.)?{self.raiz}/"

            html = re.sub(r'<base href=".*?">', r'', html)


            img_thumbs = f'(h.*)?inc/scripts/thumbs.php\?w=(.*?)&(amp;)?h=(.*?)\&(amp;)?imagem='
            img_tim = f'(h.*)?tim\.php\?src='
            html = re.sub(f'({img_thumbs}|{img_tim})', r'', html)
            html = re.sub(f'<img(.*?)(src ?= ?)[\'\"](.*?)(\&.*?)[\'\"]', r'<img\1\2"\3"', html)


            html = html.replace(f'../', '{{ path }}')
            html = re.sub(f'href="{url_regex}"', f'href="' + '{{ path }}' + 'index.html"', html)
            html = re.sub(f'<a(.*?)href="{url_regex}(.*?)"', r'<a\1href="'+ '{{ path }}' + r'\4.html"', html)
            html = re.sub(f'href="(.*?\..*?)\.html"', r'href="\1"', html)
            html = html.replace(f'{self.url_base}', '{{ path }}')
            html = html.replace('{{ path }}', '../' * len(diretorio))

            with open(f"{self.raiz}/{name_page}.html", "w", encoding="utf-8") as arquivo:
                arquivo.write(str(html))
        except:
            self.log.append(f"Não foi possível baixar o arquivo {name_page}")


    def is_404(self, link):
        try:
            location = self.session.head(link).headers["Location"]

        except:
            return False

        else:
            if location.endswith("/404"):
                return True

