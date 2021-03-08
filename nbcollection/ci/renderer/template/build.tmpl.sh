#!/usr/bin/env bash

set -e
cd "{{ build_context.build_dir }}"
source bin/activate
if [ -f "environment.sh" ]; then
    source environment.sh
fi
mkdir -p "{{ notebook_context.artifact.dirpath }}"
jupyter nbconvert --debug --to "{{ build_context.output_format }}" --execute "{{ notebook_context.path }}" --output "{{ notebook_context.artifact.path }}" --ExecutePreprocessor.timeout="{{ build_context.timeout }}"
cd -
exit 0
