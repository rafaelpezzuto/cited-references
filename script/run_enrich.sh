#!/bin/bash
. "/home/rafaeljpd/Repos/science/cited-references/venv/bin/activate"
cd "/home/rafaeljpd/Repos/science/cited-references/core/matchers"

FILE=$1
JUMP=$2
STOP=$3

python /home/rafaeljpd/Repos/science/cited-references/core/matchers/enrich_references.py \
    --issnl_to_all /media/rafaeljpd/Dados/data/pi/scl/correction-bases/v0.8/issn_to_all.v0.8b.csv \
    --title_year_volume_to_issn /media/rafaeljpd/Dados/data/pi/scl/correction-bases/v0.6c/base_year_volume_v0.6c.csv \
    --artifitial_title_year_volume_to_issn /media/rafaeljpd/Dados/data/pi/scl/correction-bases/v0.6c/base_year_volume_artifitial_v0.6c.csv \
    --equations /media/rafaeljpd/Dados/data/pi/scl/correction-bases/v0.6c/equations_issn_v0.6c.csv \
    --use_fuzzy \
    --output "$FILE.$JUMP.$STOP.csv" \
    --input "$FILE" \
    --input_format scl24 \
    --ignore_previous_result \
    --jump "$JUMP" \
    --stop "$STOP"
