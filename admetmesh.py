#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup


def get_csv(smiles):
    """Obtém o nome e o path do arquivo csv gerado pelo smiles"""
    try:
        path = ''
        url = f"https://admetmesh.scbdd.com/service/screening/cal"
        client = requests.session()
        client.get(url=url, timeout=10)
        csrftoken = client.cookies["csrftoken"]
        payload = {
            "csrfmiddlewaretoken": csrftoken,
            "smiles-list": smiles,
            "method": "2"
        }

        r = client.post(url, data=payload, headers=dict(Referer=url))
        soup = BeautifulSoup(r.content, "html.parser")
        for a in soup.find_all('a', href=True):
            if '/tmp' in a['href']:
                path = a['href']
        csv = path.split('/')
        csv = csv[-1]
        return path, csv
    except UnboundLocalError:
        return 0


def download_admet(smiles, filename=None, to_stdout=False, header=False, csv=False):
    """Faz o download da análise admet a partir do nome obtido de acordo com o smiles e cria com filename ou imprime
    no stdout"""
    path, admet = get_csv(smiles)
    if admet == 0:
        print("Smiles could not be found or doesn't exist")
    else:
        download = requests.get(f'https://admetmesh.scbdd.com{path}')
        if header:
            content = download.text
        else:
            text = download.text
            first_index = text.find('\n')
            content = text[first_index + 1:]
        if not csv:
            content = content.replace(',', '\t')
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
            print('Download complete')
