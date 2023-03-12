#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import time


def get_csv(smiles, method):
    """Obtém o nome do arquivo csv gerado pelo smiles"""
    try:
        print("Trying request")
        link = ''
        service_type = 'evaluation' if method == "1" else 'screening'
        smiles_key = "smiles" if method == "1" else "smiles-list"
        url = f"https://admetmesh.scbdd.com/service/{service_type}/cal"
        client = requests.session()
        client.get(url=url, timeout=10)
        #        print(client.cookies.get_dict())
        csrftoken = client.cookies["csrftoken"]
        payload = {
            "csrfmiddlewaretoken": csrftoken,
            smiles_key: smiles,
            "method": method
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


def download_csv(smiles, method):
    """Faz o download do arquivo csv a partir do nome obtido de acordo com o smiles"""
    csv = get_csv(smiles, method)
    if csv == 0:
        print('O smiles não foi encontrado ou não existe')
    else:
        download_url = 'https://admetmesh.scbdd.com/static/files/evaluation/result/tmp/'
        download = requests.get(f'{download_url}{csv}')
        with open(csv, 'wb') as file:
            file.write(download.content)
        print('Seu arquivo foi baixado!')


if __name__ == '__main__':
    smiles = "C1=CC=C(C=C1)C=O\r\nCC(=O)OC1=CC=CC=C1C(=O)O\r\nC1=CC(=C(C=C1/C=C\C(=O)O)O)O"
    aspirin_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    download_csv(smiles, "2")
