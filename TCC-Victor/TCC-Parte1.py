import logging
import re
import requests
import PyPDF2
from io import BytesIO
from bs4 import BeautifulSoup
import time


class PDFValidator:
    def __init__(self, domain, filetype, num_results=2000, lang="pt"):
        self.domain = domain
        self.filetype = filetype
        self.num_results = num_results
        self.lang = lang
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.violating_links = []
        self.counter = 0

    def search_and_validate(self):
        start_index = 0
        while start_index < self.num_results:
            search_url = f"http://{self.domain}"
            response = self.session.get(search_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            search_results = soup.find_all("a")
            for result in search_results:
                link = result.get("href", "")
                if link.endswith('.pdf'):
                    self.counter += 1
                    print(f"Arquivo PDF {self.counter} encontrado: {link}")
                    if self.check_pdf_violations(link):
                        print(f"Este arquivo PDF {self.counter} contém dados pessoais que violam a LGPD.")
                        self.violating_links.append(link)
                    else:
                        print(f"Este arquivo PDF {self.counter} não contém violações da LGPD.")
                    if self.counter >= self.num_results:
                        break
            start_index += 1

        if self.violating_links:
            print("Links que violam a LGPD:")
            for link in self.violating_links:
                print(link)
        else:
            print("Nenhum link que viola a LGPD foi encontrado.")

    def check_pdf_violations(self, pdf_url):
        try:
            response = self.session.get(pdf_url, headers=self.headers, allow_redirects=True)
            response.raise_for_status()
            pdf_content = response.content
            pdf_file = PyPDF2.PdfFileReader(BytesIO(pdf_content))
            violation_found = False
            for page in range(pdf_file.numPages):
                page_text = pdf_file.getPage(page).extractText()
                if self.check_keywords(page_text) or self.check_patterns(page_text):
                    violation_found = True
                    break
            return violation_found
        except requests.exceptions.RequestException as e:
            logging.exception(f'Erro ao fazer o download do arquivo PDF: {e}')
            return False
        except requests.exceptions.HTTPError as e:
            logging.exception(f'Erro HTTP ao acessar a URL do arquivo PDF: {e}')
            return False

    def check_keywords(self, text):
        keywords = ["CPF", "CNPJ", "telefone"]
        text = text.lower()
        return any(keyword.lower() in text for keyword in keywords)

    def check_patterns(self, text):
        cpf_pattern = r"\d{3}\.\d{3}\.\d{3}-\d{2}"
        cnpj_pattern = r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
        phone_pattern = r"\(\d{2}\) \d{4,5}-\d{4}"
        return bool(re.search(cpf_pattern, text) or re.search(cnpj_pattern, text) or re.search(phone_pattern, text))


# Exemplo de uso
validator = PDFValidator(domain="cefetmg.br", filetype="pdf", num_results=2000)
validator.search_and_validate()
