#!/bin/bash
. "/home/rafaeljpd/.virtualenvs/cimetrias/bin/activate"
cd "/home/rafaeljpd/Data/cimetrias/elsevier/databricks/scripts/cited-references/core/matchers"

JUMP=$1
STOP=$2

python /home/rafaeljpd/Data/cimetrias/elsevier/databricks/scripts/cited-references/core/matchers/enrich_references.py \
    --title_to_issnl /home/rafaeljpd/Data/cimetrias/correction-bases/current-v0.6c/base_title2issnl_v0.6c.csv \
    --issnl_to_all /home/rafaeljpd/Data/cimetrias/correction-bases/current-v0.6c/base_issnl2all_v0.6c.csv \
    --title_year_volume_to_issn /home/rafaeljpd/Data/cimetrias/correction-bases/current-v0.6c/base_year_volume_v0.6c.csv \
    --artifitial_title_year_volume_to_issn /home/rafaeljpd/Data/cimetrias/correction-bases/current-v0.6c/base_year_volume_artifitial_v0.6c.csv \
    --equations /home/rafaeljpd/Data/cimetrias/correction-bases/current-v0.6c/equations_issn_v0.6c.csv \
    --use_fuzzy \
    --output "output.$JUMP.$STOP.csv" \
    --input /home/rafaeljpd/Data/cimetrias/elsevier/databricks/references/test_56_export.sanitized.csv \
    --input_format elsevier \
    --ignore_previous_result \
    --jump "$JUMP" \
    --stop "$STOP"
