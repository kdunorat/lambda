#!/usr/bin/env python

import requests
from admetmesh import get_csv


def download_csv(smiles):
    """Faz o download do arquivo csv a partir do nome obtido de acordo com o smiles"""
    csv = get_csv(smiles)
    if csv == 0:
        print('O smiles não foi encontrado ou não existe')
    else:
        download_url = 'https://admetmesh.scbdd.com/static/files/evaluation/result/tmp/'
        download = requests.get(f'{download_url}{csv}')
        with open(csv, 'wb') as file:
            file.write(download.content)
        print('Seu arquivo foi baixado!')


if __name__ == '__main__':
    aspirin_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    download_csv(aspirin_smiles)
