#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from sys import stderr
from math import ceil


def get_csv(smiles):
    """Obtém o nome do arquivo csv gerado pelo smiles"""
    path = ''
    invalids = []
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

    # Checks if the site considered all smiles invalid and, if so, raises an TypeError
    if soup.find_all(class_="alert alert-warning"):
        raise TypeError('All smiles are invalid')

    tags = soup.find_all("li", class_="list-group-item text-center")
    for invalid in tags:
        invalids.append(invalid.text)
    for a in soup.find_all('a', href=True):
        if '/tmp' in a['href']:
            path = a['href']
    csv = path.split('/')
    csv = csv[-1]

    if csv == 0:
        raise TypeError('No csv returned by the site')

    return path, csv, invalids


def download_admet(smiles, append=False, filename=None, err_file=None, smiles_err=True, to_stdout=False, header=False,
                   csv=False, arg_prefix='', prefix_list=None):
    """Faz o download da análise admet a partir do nome obtido de acordo com o smiles e cria com filename ou imprime
    no stdout"""

    if prefix_list:
        if len(prefix_list) != len(smiles):
            raise ValueError('Prefix list and Smiles List have different lengths. They must be the same.')

        header = False

    if csv:
        delimiter = ','
    else:
        delimiter = '\t'

    if append:
        mode = 'a'
    else:
        mode = 'w'

    for sub_c in range(1, ceil(len(smiles) / 500) + 1):
        if sub_c > 1:
            mode = 'a'

        smi = smiles[(sub_c - 1) * 500: sub_c * 500]
        if prefix_list:
            pre_list = prefix_list[(sub_c - 1) * 500: sub_c * 500]

        try:
            path, admet, invalids = get_csv(''.join(['\r\n'.join(smi), '\r\n']))
        except TypeError as error:
            if pre_list != 0:
                for iterator in range(len(smi)):
                    smi[iterator] = f"{pre_list[iterator]}{smi[iterator]}"

            smi = '\n'.join(smi)
            err_msg = f"{repr(error)}\nAll lines for only invalid smiles case:\n{smi}"

            if smiles_err:
                print(err_msg, file=stderr)

            if err_file:
                with open(err_file, 'a') as err:
                    err.write(err_msg)
            continue

        if len(invalids) != 0:
            err_msg = f"You submitted {len(invalids)} lines with invalid smiles:\n"

            for invalid in invalids:
                i = 0
                # Find the corresponding line on the prefix_list
                while i < len(pre_list):
                    if invalid == smi[i]:
                        break
                    i += 1

                if len(pre_list) != 0:
                    err_msg = f"{err_msg}{pre_list[i]}{invalid}\n"
                    del pre_list[i]
                else:
                    err_msg = f"{err_msg}{invalid}\n"

                del smi[i]

            if smiles_err:
                print(err_msg, file=stderr)

            if err_file:
                with open(err_file, 'a') as err:
                    err.write(err_msg)

        content = requests.get(f"https://admetmesh.scbdd.com{path}").text.split('\n')

        # Removes smiles from the results of the site. Also removes any possible empty lines.
        iterator = 1
        while iterator < len(content):
            if not content[iterator]:
                del content[iterator]
                continue

            content[iterator] = content[iterator][content[iterator].find(',') + 1:]
            if not csv:
                content[iterator] = content[iterator].replace(',', '\t')

            iterator += 1

        for i in range(len(content) - 1):
            if pre_list:
                content[i + 1] = f"{arg_prefix}{pre_list[i]}{smi[i]}{delimiter}{content[i + 1]}"
            else:
                content[i + 1] = f"{arg_prefix}{smi[i]}{delimiter}{content[i + 1]}"

        if header:
            if not csv:
                content[0] = content[0].replace(',', '\t')

            if arg_prefix:
                content[0] = f"{arg_prefix}{content[0]}"
        else:
            content = content[1:]

        content = ''.join(['\n'.join(content), '\n'])

        if to_stdout:
            from sys import stdout
            print(content, file=stdout)

        if filename is not None:
            with open(filename, mode) as file:
                file.write(content)
        else:
            from os import getpid
            with open(f'admetlab2_script_result_{getpid()}.{"csv" if csv else "tsv"}', mode) as file:
                file.write(content)

        if not to_stdout:
            print('Download complete')
