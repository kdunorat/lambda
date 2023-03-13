#!/usr/bin/env python

from sys import argv
from sys import exit
from sys import stdin
from collections import deque
from os.path import isfile
from admetmesh import download_admet


def cli():

    usage = f"""Usage: {argv[0]} [options] (smiles [filename])...

    Downloads ADMET analysis for smiles in csv format file downloaded from
    admetlab2 web portal.

    Options:
            -s, --smiles-only           : Doesn't expect filenames to be passed.
                                          Saves with default name provided by the
                                          portal. (Default: False)
            -H, --header                : Include header on downloaded csv.
                                          (Default: False)
            -c, --csv                   : Whether to keep contents of admet
                                          analysis as a csv or convert it to a tsv
                                          one. (Default: False)

            - , --stdin                 : Take input smiles from stdin. (Default:
                                          False).
            -O, --stdout                : Prints results to stdout instead of file.
                                          (Default: False)
            -i, --input-file <file>     : File from which to take the input smiles.

            -h, --help                  : Prints this message.

If using smiles and filenames (so, if '-s' / '--smiles-only' or '-O' /
'--stdout'are not used), each smiles must be followed by a whitespace and
its respective filename when passed as a command line argument or followed
by a tab and the filename if the input method is a file or stdin.

Input smiles passed as arguments by command line are always processed
first. To use the other input methods, their respective flags are
necessary.

If both - (stdin) and -i (--input-file) are used, the input file is
processed first."""

    only_smiles = False
    use_stdin = False
    use_stdout = False
    header = False
    csv = False

    input_file = None

    args_raw = deque(argv[1:])
    args = deque([])
    smiles_list = ''

    while args_raw:
        arg = args_raw.popleft()
        if arg.startswith('--'):
            if arg == '--help':
                print(usage)
                exit(0)
            elif arg == '--smiles-only':
                only_smiles = True
            elif arg == '--stdin':
                use_stdin = True
            elif arg == '--stdout':
                use_stdout = True
            elif arg == '--input-file':
                if args_raw:
                    ifile = args_raw.popleft()
                    if isfile(ifile):
                        input_file = ifile
                    else:
                        print(f'File {ifile} does not exist. Ignoring option.')
                else:
                    print(f'Argument {arg} must be followed by a filename.')
                    exit(1)
            elif arg == '--header':
                header = True
            elif arg == '--csv':
                csv = True
            else:
                print(f"Unknown option: {arg}\n")
                print(usage)
                exit(1)
        elif arg.startswith('-'):
            if arg == '-':

                use_stdin = True
            else:
                arg = arg[1:]
                for i in range(len(arg)):
                    if arg[i] == 'h':
                        print(usage)
                        exit(0)
                    elif arg[i] == 's':
                        only_smiles = True
                    elif arg[i] == 'O':
                        use_stdout = True
                    elif arg[i] == 'i':
                        if i >= len(arg):
                            print('Parametrized options must be immediately followed by their parameters.')
                            exit(1)

                        if args_raw:
                            ifile = args_raw.popleft()
                            if isfile(ifile):
                                input_file = ifile
                            else:
                                print(f'File {ifile} does not exist. Ignoring option.')
                        else:
                            print(f'Argument {arg} must be followed by a filename.')
                            exit(1)
                    elif arg[i] == 'H':
                        header = True
                    elif arg[i] == 'c':
                        csv = True
                    else:
                        print(f'Unknown option: {arg}\n')
                        print(usage)
                        exit(1)
        else:
            args.append(arg)

    if not only_smiles and not use_stdout and input_file is None and len(args) % 2 == 1:
        print("Error: You must use pairs of (smile filename) or use the -s (--smiles-only) or the -O (--stdout) "
              " or the -i (--input-file <file>) options.\n")
        print(usage)
        exit(1)

    smiles = []

    while args:
        arg = args.popleft()
        if only_smiles or use_stdout:
            smiles.append(arg)
        elif args:
            smiles.append((arg, args.popleft()))

    if input_file:
        smiles_list = ""
        with open(input_file, 'r') as ifile:
            if only_smiles or use_stdout:
                for line in ifile.read().splitlines():
                    smiles.append(line)

            else:
                for line in ifile.read().splitlines():
                    line = line.split(' ')
                    print(line)
                    print(f'smiles: {line[0]}, file: {line[1]}')
                    smiles.append((line[0], line[1]))
    for smi in smiles:
        smiles_list += f"{smi}\r\n"

    if use_stdin:
        if only_smiles or use_stdout:
            for line in stdin:
                line = line.rstrip()
                smiles.append(line)
        else:
            for line in stdin:
                line = line.rstrip().split('\t')
                smiles.append((line[0], line[1]))

    else:
        if only_smiles or use_stdout:
            download_admet(smiles_list, to_stdout=use_stdout, header=header, csv=csv)
        else:
            for smi in smiles:
                print(f'smiles: {smi[0]} , filename: {smi[1]}')
                download_admet(smi[0], filename=smi[1], header=header, csv=csv)


if __name__ == '__main__':
    cli()
