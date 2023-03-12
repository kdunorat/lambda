#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup


def get_csv(smiles):
    """Obtém o nome do arquivo csv gerado pelo smiles"""
    try:
        link = ''
        url = 'https://admetmesh.scbdd.com/service/evaluation/cal'
        client = requests.session()
        client.get(url=url, timeout=10)
        #        print(client.cookies.get_dict())
        csrftoken = client.cookies["csrftoken"]
        payload = {
            "csrfmiddlewaretoken": csrftoken,
            "smiles": smiles,
            "method": "1"
        }

        r = client.post(url, data=payload, headers=dict(Referer=url))
        soup = BeautifulSoup(r.content, "html.parser")
        for a in soup.find_all('a', href=True):
            if '/tmp' in a['href']:
                link = a['href']
        csv = link.split('/')
        csv = csv[-1]
        return csv
    except UnboundLocalError:
        return 0


def download_admet(smiles, filename=None, to_stdout=False, header=False, csv=False):
    """Faz o download da análise admet a partir do nome obtido de acordo com o smiles e cria com filename ou imprime
    no stdout"""
    admet = get_csv(smiles)
    if admet == 0:
        print('O smiles não foi encontrado ou não existe')
    else:
        #        print(admet)
        download_url = 'https://admetmesh.scbdd.com/static/files/evaluation/result/tmp/'
        download = requests.get(f'{download_url}{admet}')
        if header:
            content = download.text
        else:
            text = download.text
            first_index = text.find('\n')
            content = text[first_index + 1:]
        print(content)
        if not csv:
            content = content.replace(',', '\t')
        #        print(content)
        if to_stdout:
            from sys import stdout
            print(content, file=stdout)
        elif filename is not None:
            with open(filename, 'w') as file:
                file.write(content)
        else:
            with open(admet, 'w') as file:
                file.write(content)
        if not to_stdout:
            print('Seu arquivo foi baixado!')
