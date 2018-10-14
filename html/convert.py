#!/usr/bin/env python3

from nbpages import make_parser, run_parsed

run_parsed('.', output_type='HTML', args=make_parser().parse_args())
