#!/usr/bin/env python

from math import ceil
from sys import argv
from sys import exit
from sys import stdin
from sys import stderr
from collections import deque
from os.path import isfile
from admetmesh import download_admet


def help(exit_code):
    usage = f"""Usage: {argv[0]} [options] [-o <output-file>] (smiles)...

Downloads ADMET analysis for smiles in csv format downloaded from admetlab2 web
portal. Outputs into stdout by defualt.

Options:
        -H, --header                : Include header on downloaded csv.
                                      (Default: False)
        -c, --csv                   : Keep contents of admet analysis as a csv
                                      instead of converting it to a tsv one.
                                      (Default: False)
        -p, --prefix <prefix>       : Prefixes every smiles' result with the
                                      given string.
        -d, --delimiter <del>       : Used with "stding" or "input file". Uses
                                      the given delimiter to identify where
                                      the prefix ends and the smiles begins.
                                      (Default: Tabulation "\\t" )
        -a, --append                : Append to output file instead of
                                      overwriting. Must be specified before the
                                      "--output-file" option. (Default: False)
        -f, --force                 : If the "--output-file" already exists and
                                      "--append" is False, just overwrite it.
                                      By default, returns an error. Must be
                                      specified before the "--output-file"
                                      option. (Default: False)

        - , --stdin                 : Take input smiles from stdin. (Default:
                                      False).
        -o, --output-file <file>    : Output result to file. (Default:
                                      admetlab2_script_result_randomnumber , 
                                      where the randomnumber is anywhere from
                                      1 to 1000000000000000)
        -e, --error-file <file>     : Output errors with processing the smiles
                                      on the site to this file. The named
                                      passed will have the ".err" sufix added
                                      to it. (Default: "admetlab_errors")
        
        -N, --no-stdout             : Disable printing to stdout.
        -E, --no-smiles-error       : Don't print invalid smiles to stderr.
        -i, --input-file <file>     : File from which to take the input smiles.

        -h, --help                  : Prints this message.

The smiles on the resulting output is the one passed as input, not the one
returned by the admetlab2 web.

The prefix passed through the parameters is repeated at the beggining of every
smiles result. If passed multiple times on the script's arguments all of them
are concatenated in the order they were inputed.

The options "--stdin" and "--input-file" process their own prefixes based on
the delimiter (which can be specified by the "--delimiter" option). For each
line, they find the last occurrence of the delimiter and consider everything
before (delimiter included) as the prefix and everything after (delimiter
excluded) the smiles. This way, a smiles specific prefix can be used. To not
use such prefix, just make sure the delimiter doesn't happen on the file or
stdin.

If both the command line "--prefix" option and the smiles specific prefixes
on stdin and input file are used, they are concatenated: first the command
line option, then the smiles specific one.

If "--header" is true, the "--prefix" option will add its contents before
the header as well

Using the options "--stdin" or "--input-file" disables the header, even if
its flag was passed.

If no input option is used (no "--input-file" nor "--stdin" nor smiles
passed as arguments) stdin is used.

Input processing order:

Input smiles passed as arguments by command line are always processed
first. To use the other input methods, their respective flags are
necessary.

If both - (stdin) and -i (--input-file) are used, the input file has its
contents read first. After both have been read, they are processed together.

Empty lines are ignored.

Smiles with errors:

If any smiles give errors when submitted, they are ignored on the program
regular output.

By default, a message is printed to stderr with the error smiles.

If "--no-smiles-error" is used and no error file is specified, it uses the
default error filename."""

    if exit_code == 0:
        print(usage)
    else:
        print(usage, file=stderr)

    exit(exit_code)


def is_param_next(arg, i):
    if i < len(arg) - 1:
        print('Options with parameters must be immediately followed by their parameters.', file=stderr)
        exit(1)


def counter_err_file(ifile=''):
    if not ifile:
        ifile = f'admetlab_errors'

    counter = 1
    while isfile(f"{ifile}_{counter}.err"):
        counter += 1
    return f"{ifile}_{counter}.err"


def opt_use_stdin(boolean):
    global use_stdin
    use_stdin = boolean


def opt_no_stdout(boolean):
    global use_stdout
    use_stdout = boolean


def opt_no_smiles_err(boolean):
    global use_smiles_err
    use_smiles_err = boolean


def opt_append(boolean):
    global append
    append = boolean


def opt_force(boolean):
    global force
    force = boolean


def opt_input_file(arg='', i=0):
    global args_raw
    global input_file

    if arg:
        is_param_next(arg, i)

    if args_raw:
        ifile = args_raw.popleft()
        if isfile(ifile):
            input_file = ifile
        else:
            print(f'File {ifile} does not exist. Ignoring option.', file=stderr)
    else:
        print(f'Argument must be followed by a filename.', file=stderr)
        exit(1)


def opt_output_file(arg='', i=0):
    global args_raw
    global output_file
    global append
    global force

    if arg:
        is_param_next(arg, i)

    if args_raw:
        ifile = args_raw.popleft()
        if not isfile(ifile) or append or force:
            output_file = ifile
        else:
            print(
                f'File {ifile} already exists. To overwrite it, use the -f option too. To append to it, use the -a option.',
                file=stderr)
            exit(1)
    else:
        print(f'Argument must be followed by a filename.', file=stderr)
        exit(1)


def opt_err_file(arg='', i=0):
    global args_raw
    global err_file

    if arg:
        is_param_next(arg, i)

    if args_raw:
        ifile = args_raw.popleft()
        if not isfile(f"{ifile}.err"):
            err_file = f"{ifile}.err"
        else:
            err_file = counter_err_file(ifile)
    else:
        print(f'Argument must be followed by a filename.', file=stderr)
        exit(1)


def opt_arg_prefix(arg='', i=0):
    global args_raw
    global arg_prefix

    if arg:
        is_param_next(arg, i)

    if args_raw:
        arg_prefix = f"{arg_prefix}{args_raw.popleft()}"
    else:
        print(f'Argument must be followed by a filename.', file=stderr)
        exit(1)


def opt_delimiter(arg='', i=0):
    global args_raw
    global delimiter

    if arg:
        is_param_next(arg, i)

    if args_raw:
        delimiter = args_raw.popleft()
    else:
        print(f'Argument must be followed by a filename', file=stderr)
        exit(1)


def opt_header(boolean):
    global header
    header = boolean


def opt_csv(boolean):
    global csv
    csv = boolean


def cli():
    global use_stdin
    global use_stdout
    global use_smiles_err
    global header
    global csv
    global input_file
    global output_file
    global err_file
    global arg_prefix
    global delimiter

    global args_raw

    smiles_list = ''
    arg_smiles = []
    smiles = []

    while args_raw:
        arg = args_raw.popleft()
        if arg.startswith('--'):
            if arg == '--help':
                help(0)
            elif arg == '--stdin':
                opt_use_stdin(True)
            elif arg == '--no-stdout':
                opt_no_stdout(False)
            elif arg == '--no-smiles-error':
                opt_no_smiles_err(False)
            elif arg == '--append':
                opt_append(True)
            elif arg == '--force':
                opt_force(True)
            elif arg == '--input-file':
                opt_input_file()
            elif arg == '--output-file':
                opt_output_file()
            elif arg == '--error-file':
                opt_err_file()
            elif arg == '--prefix':
                opt_arg_prefix()
            elif arg == '--delimiter':
                opt_delimiter()
            elif arg == '--header':
                opt_header(True)
            elif arg == '--csv':
                opt_csv(True)
            else:
                print(f"Unknown option: {arg}\n", file=stderr)
                help(1)
        elif arg.startswith('-'):
            if arg == '-':
                opt_use_stdin(True)
            else:
                arg = arg[1:]
                for i in range(len(arg)):
                    if arg[i] == 'h':
                        help(0)
                    elif arg[i] == 'N':
                        opt_no_stdout(False)
                    elif arg[i] == 'E':
                        opt_no_smiles_err(False)
                    elif arg[i] == 'a':
                        opt_append(True)
                    elif arg[i] == 'f':
                        opt_force(True)
                    elif arg[i] == 'i':
                        opt_input_file(arg, i)
                    elif arg[i] == 'o':
                        opt_output_file(arg, i)
                    elif arg[i] == 'e':
                        opt_err_file(arg, i)
                    elif arg[i] == 'p':
                        opt_arg_prefix(arg, i)
                    elif arg[i] == 'd':
                        opt_delimiter(arg, i)
                    elif arg[i] == 'H':
                        opt_header(True)
                    elif arg[i] == 'c':
                        opt_csv(True)
                    else:
                        print(f'Unknown option: {arg}\n', file=stderr)
                        help(1)
        else:
            arg_smiles.append(arg)

    if not input_file and len(arg_smiles) == 0:
        opt_use_stdin(True)

    if input_file or use_stdin:
        prefix_smi = []

    if input_file:
        with open(input_file, 'r') as ifile:
            for line in ifile.read().splitlines():
                if not line:
                    continue

                deli = line.rfind(delimiter)
                if deli == -1:
                    smiles.append(line)
                    prefix_smi.append('')
                else:
                    del_end = deli + len(delimiter)
                    smiles.append(line[del_end:])
                    prefix_smi.append(line[:del_end])

    if use_stdin:
        for line in stdin:
            line = line.rstrip()
            if not line:
                continue

            deli = line.rfind(delimiter)
            if deli == -1:
                smiles.append(line)
                prefix_smi.append('')
            else:
                del_end = deli + len(delimiter)
                smiles.append(line[del_end:])
                prefix_smi.append(line[:del_end])

    if input_file or use_stdin:
        header = False

    if not err_file and not use_smiles_err:
        err_file = counter_err_file()

    if arg_smiles:
        arg_append = append
        for i in range(1, ceil(len(arg_smiles) / 500) + 1):
            if i > 1:
                arg_append = True

            download_admet(smiles=arg_smiles[(i - 1) * 500: i * 500],
                           append=arg_append,
                           filename=output_file,
                           err_file=err_file,
                           smiles_err=use_smiles_err,
                           to_stdout=use_stdout,
                           header=header,
                           csv=csv,
                           arg_prefix=arg_prefix)

    if input_file or use_stdin:
        arg_append = append
        for i in range(1, ceil(len(smiles) / 500) + 1):
            if i > 1:
                arg_append = True

            download_admet(smiles=smiles[(i - 1) * 500: i * 500],
                           append=arg_append,
                           filename=output_file,
                           err_file=err_file,
                           smiles_err=use_smiles_err,
                           to_stdout=use_stdout,
                           header=header,
                           csv=csv,
                           arg_prefix=arg_prefix,
                           prefix_list=prefix_smi[(i - 1) * 500: i * 500])


if __name__ == '__main__':
    use_stdin = False
    use_stdout = True
    use_smiles_err = True
    header = False
    csv = False
    append = False
    force = False
    input_file = None
    output_file = None
    err_file = None
    arg_prefix = ""
    delimiter = "\t"

    args_raw = deque(argv[1:])

    cli()
