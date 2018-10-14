#!/usr/bin/env python3

from nbpages import make_parser, run_parsed

run_parsed('notebooks', output_type='RST', args=make_parser().parse_args())
