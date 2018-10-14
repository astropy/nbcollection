#!/usr/bin/env python3

from nbpages import make_parser, run_parsed

run_parsed(make_parser().parse_args(), output_type='RST')
