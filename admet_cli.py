#!/usr/bin/env python3

from math import ceil
from sys import argv
from sys import exit
from sys import stdin
from sys import stderr
from collections import deque
from os.path import isfile
from admetmesh import download_admet


# Prints the help message and exits the program with the given exit code
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
                                      "admetlab2_script_result_processid" ,
                                      only applicable if no "--output-file" is
                                      specified and "--no-stdout" is used).
        -e, --error-file <file>     : Output errors with processing the smiles
                                      on the site to this file. The name
                                      passed will have the ".err" sufix added
                                      to it. (Default: "admetlab_errors", only
                                      used if no "--error-file" is specified
                                      and "--no-smiles-error" is used).
        
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
default error filename.

If a error file that already exists is used, the contents of new error
smiles messages will be appended to the err file."""

    if exit_code == 0:
        print(usage)
    else:
        print(usage, file=stderr)

    exit(exit_code)


# Checks whether the index for the arg (which corresponds to a short parameter) corresponds to the last character
def is_param_next(arg, i):
    if i < len(arg) - 1:
        print('Options with parameters must be immediately followed by their parameters.', file=stderr)
        exit(1)


# Changes state of use_stdin boolean variable
def opt_use_stdin(boolean):
    global use_stdin
    use_stdin = boolean


# Changes state of use_stdout boolean variable
def opt_no_stdout(boolean):
    global use_stdout
    use_stdout = boolean


# Changes state of use_smiles_err boolean variable (controls whether to print the smiles that give errors at site to stderr)
def opt_no_smiles_err(boolean):
    global use_smiles_err
    use_smiles_err = boolean


# Changes state of append boolean variable (controls whether to append or overwrite the output file, in case it already exists)
def opt_append(boolean):
    global append
    append = boolean


# Changes state of force boolean variable (if true, allows overwriting the output file, in case it already exists)
def opt_force(boolean):
    global force
    force = boolean


# Adds a valid file path to the input_file global variable
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


# Adds a file path to the input_file global variable.
# Fails if the file already exists and neither append nor force are true.
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
                f'File {ifile} already exists. To overwrite it, use the -f option too.'
                'To append to it, use the -a option.',
                file=stderr)
            exit(1)
    else:
        print(f'Argument must be followed by a filename.', file=stderr)
        exit(1)


# Adds a path to the err_file global variable
def opt_err_file(arg='', i=0):
    global args_raw
    global err_file

    if arg:
        is_param_next(arg, i)

    if args_raw:
        err_file = f"{args_raw.popleft()}.err"
    else:
        print(f'Argument must be followed by a filename.', file=stderr)
        exit(1)


# Adds an string to the arg_prefix global variable
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


# Changes the value of the delimiter global variable.
def opt_delimiter(arg='', i=0):
    global args_raw
    global delimiter

    if arg:
        is_param_next(arg, i)

    if args_raw:
        delimiter = args_raw.popleft()
    else:
        print(f'Argument must be followed by a string (the delimiter).', file=stderr)
        exit(1)


# Changes state of header boolean variable
def opt_header(boolean):
    global header
    header = boolean


# Changes state of csv boolean variable
def opt_csv(boolean):
    global csv
    csv = boolean


def cli():
    global use_stdin # Whether to use stdin as input
    global use_stdout # Whether to use stdout as output
    global use_smiles_err # Whether to print smiles that give errors on the site to stderr
    global header # Whether to keep the header that the admetlab portal adds to their results
    global csv # Whether to keep admetlab's results in csv format or convert it to tsv
    global input_file # Input file to be used (if any)
    global output_file # Output file to be used (if any)
    global err_file # Error file path for smiles that give errors to be used (if any)
    global arg_prefix # Command line specified prefix to be added at the beggining of every result line
    global prefix_smi # Line specific prefix to be added to the its corresponding line on the results
    global delimiter # Delimiter to be used in order to detect line specific prefixes when using input file and stdin

    global args_raw # Input arguments to be processed
    
    """
    Smiles lists:
    
    Smiles from command line and from input file or stdin ar handled differently because only the later two may
    have line specific prefixes.
    """
    arg_smiles = [] # List of smiles passed as command line arguments
    smiles = [] # List of smiles passed by input file or stdin

    # Arguments and parameters parsed loop
    while args_raw:
        arg = args_raw.popleft() # Argument to be processed on this iteration
        if arg.startswith('--'): # Handling long options
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
        elif arg.startswith('-'): # Handling short options
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
        else: # If the arguments doesn't start with a '-' it is assumed to be a smiles
            arg_smiles.append(arg)

    # If no input file nor command line smiles are specified, it is assumed that the input will come from stdin
    if not input_file and len(arg_smiles) == 0:
        opt_use_stdin(True)

    # Disables header if either input file or stdin are used
    if input_file or use_stdin:
        header = False

    # Creates the prefix list if either a input file or stdin are used
    if input_file or use_stdin:
        prefix_smi = []

    # Handles input file
    if input_file:
        with open(input_file, 'r') as ifile:
            for line in ifile.read().splitlines():
                if not line: # If the line is empty, skip it
                    continue

                deli = line.rfind(delimiter) # Detect last occurence of delimiter
                if deli == -1: # If the delimiter is not detected
                    smiles.append(line)
                    prefix_smi.append('')
                else: # If the delimiter is detected
                    del_end = deli + len(delimiter)
                    smiles.append(line[del_end:])
                    prefix_smi.append(line[:del_end])

    # Handles stdin
    if use_stdin:
        for line in stdin:
            line = line.rstrip()
            if not line: # If the line is empty, skip it
                continue

            deli = line.rfind(delimiter) # Detect last occurence of delimiter
            if deli == -1: # If the delimiter is not detected
                smiles.append(line)
                prefix_smi.append('')
            else: # If the delimiter is detected
                del_end = deli + len(delimiter)
                smiles.append(line[del_end:])
                prefix_smi.append(line[:del_end])

    # Uses default error file name if none has been specified and error smiles are not to be printed to stderr
    if not err_file and not use_smiles_err:
        err_file = 'admetlab_errors.err'

    # Downloads results and creates appropriate files (if any) for command line smiles
    if arg_smiles:
        try:
            download_admet(smiles=arg_smiles,
                           append=append,
                           filename=output_file,
                           err_file=err_file,
                           smiles_err=use_smiles_err,
                           to_stdout=use_stdout,
                           header=header,
                           csv=csv,
                           arg_prefix=arg_prefix)
        except ValueError as error:
            print(repr(error), file=stderr)
            exit(1)

    # Downloads results and creates appropriate files (if any) for smiles from input file and stdin
    if smiles:
        try:
            download_admet(smiles=smiles,
                           append=append,
                           filename=output_file,
                           err_file=err_file,
                           smiles_err=use_smiles_err,
                           to_stdout=use_stdout,
                           header=header,
                           csv=csv,
                           arg_prefix=arg_prefix,
                           prefix_list=prefix_smi)
        except ValueError as error:
            print(repr(error), file=stderr)
            exit(1)


# Entry point for command line interface (cli)
if __name__ == '__main__':
    # Default values for the global variables
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

    # Removes the script's own name from the list of arguments and adds it to the args_raw variable as a doubly linked queue.
    args_raw = deque(argv[1:])

    cli()
