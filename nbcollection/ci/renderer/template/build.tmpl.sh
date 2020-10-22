#!/usr/bin/env bash

set -e
cd "{{ build_context.build_dir }}"
source venv/bin/activate
if [ -f "environment.sh" ]; then
    source environment.sh
fi
mkdir -p "{{ artifact.dirpath }}"
nbcollection-ci metadata --input "{{ notebook.path }}" --output "{{ artifact.metadata_path }}"
jupyter nbconvert --debug --to "{{ build_context.output_format }}" --execute "{{ notebook.path }}" --output "{{ artifact.path }}" --ExecutePreprocessor.timeout="{{ build_context.timeout }}"

cd -
exit 0
