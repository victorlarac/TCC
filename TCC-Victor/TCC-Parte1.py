import logging
import re
import requests
from PyPDF2 import PdfReader, errors
from io import BytesIO
from urllib.parse import urlparse
from googleapiclient.discovery import build
import time

class PDFValidator:
    def __init__(self, domain, filetype, num_results=200, lang="pt"):
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
        self.service = build("customsearch", "v1", developerKey="AIzaSyCAhaqz9Zjf0RgYPRvzKZaew-LjbUtb1Oo")

    def search_and_validate(self):
        query = f"{self.domain} {self.filetype}"
        start_index = 1
        while start_index <= self.num_results:
            try:
                response = self.service.cse().list(
                    q=query,
                    cx="a72fced6edd0640ee",
                    num=1,
                    start=start_index,
                    lr=f"lang_{self.lang}"
                ).execute()
            except Exception as e:
                logging.error(f"Erro na busca: {e}")
                break

            items = response.get("items", [])
            if not items:
                break

            result = items[0]
            link = result.get("link", "")
            start_index += 1

            if link and link.endswith('.pdf'):
                self.counter += 1
                print(f"Arquivo PDF {self.counter} encontrado: {link}")
                if self.check_pdf_violations(link):
                    print(f"⚠️ Este arquivo PDF {self.counter} contém dados pessoais que violam a LGPD.")
                    self.violating_links.append(link)
                else:
                    print(f"✅ Este arquivo PDF {self.counter} não contém violações da LGPD.")

        if self.violating_links:
            print("\n⚠️ Links que violam a LGPD:")
            for link in self.violating_links:
                print(link)
        else:
            print("\n✅ Nenhum link que viola a LGPD foi encontrado.")

    def check_pdf_violations(self, pdf_url):
        try:
            response = self.session.get(pdf_url, headers=self.headers, allow_redirects=True, verify=False)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                time.sleep(retry_after)
                response = self.session.get(pdf_url, headers=self.headers, allow_redirects=True, verify=False)

            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("application/pdf"):
                logging.warning(f"Conteúdo inválido (não é PDF): {pdf_url}")
                return False

            pdf_content = response.content

            # Salvar temporariamente para debug (opcional)
            with open("debug_downloaded_file.pdf", "wb") as f:
                f.write(pdf_content)

            pdf_file = PdfReader(BytesIO(pdf_content))

            for page in pdf_file.pages:
                try:
                    page_text = page.extract_text() or ""
                except Exception as e:
                    logging.warning(f"Erro ao extrair texto da página: {e}")
                    page_text = ""

                if page_text and (self.check_keywords(page_text) or self.check_patterns(page_text)):
                    return True
            return False

        except errors.PdfReadError as e:
            logging.error(f"Erro ao processar o PDF (formato inválido): {e}")
            return False
        except requests.exceptions.RequestException as e:
            logging.exception(f"Erro ao fazer o download do arquivo PDF: {e}")
            return False
        except Exception as e:
            logging.exception(f"Erro geral ao processar o PDF: {e}")
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


# Exemplo de uso:
if __name__ == "__main__":
    domain = "cefetmg.br"
    filetype = "pdf"
    num_results = 200

    validator = PDFValidator(domain, filetype, num_results)
    validator.search_and_validate()
