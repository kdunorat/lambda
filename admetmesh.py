#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
from sys import stderr


def get_csv(smiles):
    """Obtém o nome do arquivo csv gerado pelo smiles"""
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


def download_admet(smiles, append=False, filename=None, to_stdout=False, header=False, csv=False, arg_prefix='', prefix_list=None):
    """Faz o download da análise admet a partir do nome obtido de acordo com o smiles e cria com filename ou imprime
    no stdout"""
    if prefix_list:
        if len(prefix_list) != len(smiles):
            print('Prefix list and Smiles List have different lengths. They must be the same', file=stderr)
            exit(1)

        header = False
    
    path, admet = get_csv( ''.join(['\r\n'.join(smiles), '\r\n']) )
    if admet == 0:
        print("Smiles could not be found or don't exist", file=stderr)
    else:
        text_list = requests.get(f"https://admetmesh.scbdd.com{path}").text.split('\n')

        if csv:
            delimiter = ','
        else:
            delimiter = '\t'
        
        iterator = 1
        while iterator < len(text_list):
            if not text_list[iterator]:
                del text_list[iterator]
                continue
            
            text_list[iterator] = text_list[iterator][ text_list[iterator].find(',') + 1: ]
            if not csv:
                text_list[iterator] = text_list[iterator].replace(',', '\t')

            iterator += 1

        content = text_list[1:]

        for i in range(len(content)):
            if prefix_list:
                content[i] = f"{arg_prefix}{prefix_list[i]}{smiles[i]}{delimiter}{content[i]}"
            elif arg_prefix != '':
                content[i] = f"{arg_prefix}{smiles[i]}{delimiter}{content[i]}"
            else:
                content[i] = f"{smiles[i]}{delimiter}{content[i]}"

        if header:
            if csv:
                header_line = text_list[0]
            else:
                header_line = text_list[0].replace(',', '\t')

            if arg_prefix:
                header_line = f"{arg_prefix}{header_line}"

            content = ''.join( [header_line, '\n', '\n'.join(content), '\n'] )
            
        else:
            content = ''.join( ['\n'.join(content), '\n'] )
        
        if append:
            mode = 'a'
        else:
            mode = 'w'
        
        if to_stdout:
            from sys import stdout
            print(content, file=stdout)
        
        if filename is not None:
            with open(filename, mode) as file:
                file.write(content)
        else:
            from random import randint
            with open(f'admetlab2_script_result_{randint(1, 1000000000000000)}.{"csv" if csv else "tsv"}', mode) as file:
                file.write(content)
        
        if not to_stdout:
            print('Download complete')

