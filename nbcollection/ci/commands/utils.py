import argparse

def validate_and_parse_inputs(options: argparse.Namespace) -> argparse.Namespace:
    options.collection_names = options.collection_names.split(',') if options.collection_names else []
    options.category_names = options.category_names.split(',') if options.category_names else []
    options.notebook_names = options.notebook_names.split(',') if options.notebook_names else []
