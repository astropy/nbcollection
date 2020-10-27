#!/usr/bin/env bash

set -e
cd "{{ build_context.build_dir }}"
source venv/bin/activate
if [ -f "environment.sh" ]; then
    source environment.sh
fi
mkdir -p "{{ notebook_context.artifact.dirpath }}"
nbcollection-ci metadata -c "{{ notebook_context.collection_name }}" -t "{{ notebook_context.category_name }}" -n "{{ notebook_context.notebook.name }}"
jupyter nbconvert --debug --to "{{ build_context.output_format }}" --execute "{{ notebook_context.path }}" --output "{{ notebook_context.artifact.path }}" --ExecutePreprocessor.timeout="{{ build_context.timeout }}"

cd -
exit 0
