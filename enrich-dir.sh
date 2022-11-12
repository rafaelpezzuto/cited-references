#!/usr/bin/bash
source /home/rafaeljpd/.virtualenvs/scielo-cited-references/bin/activate

ENRICH=/home/rafaeljpd/Dropbox/repos/scielo/cited-references/core/matchers/enrich_references.py
INPUT_DIR_DATA=$1

TITLE2ISSNL=/home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_title2issnl_v0.6.csv
ISSN2ALL=/home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_issnl2all_v0.6.csv
TITLEYEARVOLUME2ISSN=/home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_year_volume_v0.6.csv
ARTIFITIALTITLEYEARVOLUME2ISSN=/home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_year_volume_artifitial_v0.6.csv
EQUATIONS=/home/rafaeljpd/Data/cimetrias/correction-bases/bases/equations_issn_v0.6.csv

echo "Enriquecendo dados de diretório $INPUT_DIR_DATA..."
python $ENRICH \
    --title_to_issnl $TITLE2ISSNL \
    --issnl_to_all $ISSN2ALL \
    --title_year_volume_to_issn $TITLEYEARVOLUME2ISSN \
    --artifitial_title_year_volume_to_issn $ARTIFITIALTITLEYEARVOLUME2ISSN \
    --equations $EQUATIONS \
    --use_fuzzy \
    --input_dir $INPUT_DIR_DATA \
    --input_format csv \
    --ignore_previous_result 
