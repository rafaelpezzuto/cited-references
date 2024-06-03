#!/bin/bash

JUMP=$1
STOP=$2

python /home/rafaeljpd/Repos/science/cited-references/core/matchers/enrich_references.py \
    --issnl_to_all /home/rafaeljpd/Data/cimetrias/correction-bases/v0.8/issn_to_all.v0.8b.csv \
    --title_year_volume_to_issn /home/rafaeljpd/Data/cimetrias/correction-bases/v0.6c/base_year_volume_v0.6c.csv \
    --artifitial_title_year_volume_to_issn /home/rafaeljpd/Data/cimetrias/correction-bases/v0.6c/base_year_volume_artifitial_v0.6c.csv \
    --equations /home/rafaeljpd/Data/cimetrias/correction-bases/v0.6c/equations_issn_v0.6c.csv \
    --use_fuzzy \
    --output "output.$JUMP.$STOP.csv" \
    --input /home/rafaeljpd/Data/cimetrias/elsevier/references/proj_056_bradfordzones_export_20230705.csv \
    --input_format elsevier \
    --ignore_previous_result \
    --jump "$JUMP" \
    --stop "$STOP"
