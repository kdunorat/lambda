

import requests
from bs4 import BeautifulSoup


def get_csv(smiles):
    """Obtém o nome do arquivo csv gerado pelo smiles"""
    try:
        print("Trying request")
        path = ''
        url = f"https://admetmesh.scbdd.com/service/screening/cal"
        client = requests.session()
        client.get(url=url, timeout=10)
        #        print(client.cookies.get_dict())
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
        return csv, path
    except UnboundLocalError:
        return 0


def download_csv(smiles):
    """Faz o download do arquivo csv a partir do nome obtido de acordo com o smiles"""
    csv, path = get_csv(smiles)
    if path == 0:
        print('O smiles não foi encontrado ou não existe')
    else:
        download = requests.get(f'https://admetmesh.scbdd.com{path}')
        if download.status_code == 404:
            print("Deu ruim")
        else:
            with open(csv, 'wb') as file:
                file.write(download.content)
            print('Seu arquivo foi baixado!')


if __name__ == '__main__':
    smiles = "C1=CC=C(C=C1)C=O\r\nCC(=O)OC1=CC=CC=C1C(=O)O\r\nC1=CC(=C(C=C1/C=C\C(=O)O)O)O"
    sm = "C1=CC=C(C=C1)C=O"
    download_csv(smiles)
