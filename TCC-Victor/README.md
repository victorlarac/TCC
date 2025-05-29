# 🕵️‍♂️ PDF Crawler LGPD Checker – CEFET-MG

Este script realiza buscas por arquivos PDF hospedados em um domínio específico (ex: `cefetmg.br`) e analisa seu conteúdo em busca de informações sensíveis como **CPF**, **CNPJ** e **telefones**, apontando possíveis **vazamentos de dados pessoais** que violam a **LGPD (Lei Geral de Proteção de Dados)**.

---

## ⚙️ Pré-requisitos

- Python 3.8+
- Conta Google para acessar a [Google Custom Search API](https://programmablesearchengine.google.com/)
- Ambiente virtual (recomendado no Kali Linux ou sistemas baseados em Debian)

---

## ✅ Passo a passo

### 1. Clone o repositório ou salve o código

```bash
git clone https://github.com/seu-usuario/crawler-lgpd.git
cd crawler-lgpd
```

Ou simplesmente copie o script Python `crawler_lgpd.py` para seu diretório.

---

### 2. Crie e ative um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Instale as dependências

```bash
pip install requests PyPDF2 google-api-python-client
```

---

### 4. Configure suas credenciais da Google Custom Search

#### a. Crie uma API key:
1. Acesse [console.developers.google.com](https://console.developers.google.com/)
2. Crie um projeto
3. Ative a **Custom Search API**
4. Vá em **Credenciais > Criar chave de API**

#### b. Crie um Search Engine ID:
1. Acesse [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Clique em **Criar mecanismo de pesquisa**
3. Configure o domínio: `cefetmg.br`
4. Salve o **Search Engine ID**

#### c. Edite o script:

No trecho abaixo do script Python, substitua:

```python
developerKey="SUA_CHAVE_API"
cx="SEU_ENGINE_ID"
```

---

### 5. Execute o script

```bash
python crawler_lgpd.py
```

---

## 🧪 Exemplo de saída

```text
Arquivo PDF 1 encontrado: https://www.cefetmg.br/documento1.pdf
⚠️ Este arquivo PDF 1 contém dados pessoais que violam a LGPD.

Arquivo PDF 2 encontrado: https://www.cefetmg.br/documento2.pdf
✅ Este arquivo PDF 2 não contém violações da LGPD.

⚠️ Links que violam a LGPD:
https://www.cefetmg.br/documento1.pdf
```

---

## 🔐 O que o script detecta?

O script analisa texto dos PDFs buscando:

- Palavras-chave como: `CPF`, `CNPJ`, `telefone`
- Padrões como:
  - CPF: `000.000.000-00`
  - CNPJ: `00.000.000/0000-00`
  - Telefone: `(00) 00000-0000`

---

## 🔒 Recomendação

Use este script apenas em domínios que você tem permissão legal para auditar. Vazamentos identificados devem ser tratados conforme a LGPD, respeitando a privacidade das pessoas.

---

## 🛠️ Integração com Burp Suite (opcional)

Para inspecionar o tráfego HTTP manualmente:

1. **Abra o Burp Suite Community Edition**
2. Vá em `Proxy > Options` e confirme o proxy ativo em `127.0.0.1:8080`
3. No script, adicione:

```python
self.session.proxies.update({
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
})
self.session.verify = False
```

4. Execute o script com o Burp Suite aberto
5. Veja as requisições em `Proxy > HTTP history`

---

## 📄 Licença

Este projeto é apenas para fins educacionais e de pesquisa acadêmica.
