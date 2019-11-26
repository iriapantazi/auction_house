#! /usr/bin/env python 

import argparse
import sys
from auction_house import AuctionHouse 

def process_arguments():
    """
    process_arguments:
    This function is an argument parser
    that 
    """
    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('-i', '--input',
             help='specify name of input file')
    parser.add_argument('-o', '--output',
            help='specify name of output file')
    args = parser.parse_args()
    return args


def process_auction_input_file(infile):
    """
    process_auction_input_file:
    This function opens the input file specified by the user,
    or the default specified. In case that an error is raised,
    the program exits, otherwise each line is processed by the 
    module auction_house.
    """
    try:
        f = open(infile, 'r')
    except Exception as e:
        print('exits because of error: {}'.format(str(e)))
        sys.exit(-1)

    for line in f.readlines():
        ebay = AuctionHouse(line)
        isValid = ebay.message_isValid()
        if isValid:
            if (line.find('|') == -1):
                line = line.strip('\n')
                ebay.process_timestamp(line)
                ebay.print_outcome()
            else:
                line = line.strip('\n')
                line = line.split('|')
                if ('SELL' in line):
                    ebay.process_message_sell(line)
                else:
                    ebay.process_message_bid(line)
        else:
            print('Exiting.')
            sys.exit(-1)
        


def main():
    """
    main:
    This function ia calling the process_arguments module that
    returns the arguments parsed by the user. Then the
    process_auction_input_file module is called with
    the input file arguments.
    """
    args = process_arguments()
    process_auction_input_file(args.input)


if __name__ == "__main__":
    main()
