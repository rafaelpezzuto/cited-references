#!/usr/bin/bash
source /home/rafaeljpd/.virtualenvs/scielo-cited-references/bin/activate

ENRICH=/home/rafaeljpd/Dropbox/repos/scielo/cited-references/core/matchers/enrich_references.py

i=$1
echo "Processando $i";
python $ENRICH \
    --title_to_issnl /home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_title2issnl_v0.6.csv \
    --issnl_to_all /home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_issnl2all_v0.6.csv \
    --title_year_volume_to_issn /home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_year_volume_v0.6.csv \
    --artifitial_title_year_volume_to_issn /home/rafaeljpd/Data/cimetrias/correction-bases/bases/base_year_volume_artifitial_v0.6.csv \
    --equations /home/rafaeljpd/Data/cimetrias/correction-bases/bases/equations_issn_v0.6.csv \
    --input $i \
    --use_fuzzy \
    --use_proj056 \
    --input_format csv \
    --output $i.enriched
