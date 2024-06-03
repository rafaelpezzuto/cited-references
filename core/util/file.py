import csv
import datetime
import json
import logging
import os
import sys

from scielo_scholarly_data import standardizer


csv.field_size_limit(sys.maxsize)


def check_dir(path):
    if os.path.exists(path):
        raise Exception

    os.makedirs(path)


def generate_folder_name(path):
    return os.path.join(
        path,
        str(round(datetime.datetime.utcnow().timestamp()*1000))
    )


def open_files(path: str) -> dict:
    files_names = [
        'pre-existing-issn',
        'doiset',
        'insufficient-data',
        'exact-match',
        'exact-match-homonymous-fixed',
        'exact-match-homonymous-insufficient-data',
        'exact-match-homonymous-not-fixed',
        'exact-match-homonymous-fixed-volume-inferred',
        'fuzzy-match-insufficient-data',
        'fuzzy-match-validated',
        'fuzzy-match-not-validated',
        'fuzzy-match-validated-volume-inferred',
        'fuzzy-todo',
        'unmatch',
    ]

    dict_files = {}

    for fn in files_names:
        try:
            dict_files[fn] = open(os.path.join(path, fn + '.csv'), 'w')
        except:
            ...

    return dict_files


def close_files(dict_files):
    for v in dict_files.values():
        try:
            v.close()
        except:
            ...


def load_title_to_gissn(issn_to_issnl, issn_to_titles):
    title_to_gissn = {}

    for issn in issn_to_titles:
        gissn = issn_to_issnl[issn]
        for t in issn_to_titles[issn]:
            if t not in title_to_gissn:
                title_to_gissn[t] = set()
            title_to_gissn[t].add(gissn)

        if gissn is None or len(gissn) != 9:
            print(f'ISSN com problema {issn}')

    for t in title_to_gissn:
        title_to_gissn[t] = '#'.join([v for v in title_to_gissn[t] if v is not None])
    return title_to_gissn


def load_issnl_to_all(path: str, sep1='|', sep2='#'):
    with open(path) as fin:
        fin.readline()
        issn_to_issnl = {}
        issn_to_titles = {}

        for line in fin:
            els = line.split(sep1)

            issns = els[1].split(sep2)
            issnl = els[0]
            titles = els[5].split(sep2)

            for i in issns:
                if i not in issn_to_issnl:
                    issn_to_issnl[i] = issnl
                    issn_to_titles[i] = titles
                else:
                    if issn_to_issnl[i] != issnl:
                        logging.error(f'{issnl} != {issn_to_issnl[i]} para chave {i}')

    return issn_to_issnl, issn_to_titles


def load_year_volume(path: str, data: dict, sep='|'):
    with open(path) as fin:
        title_year_volume_to_issn = {}

        for line in fin:
            els = line.split(sep)

            issn = standardizer.journal_issn(els[0])
            main_issn = data.get(issn, '') or issn

            title = els[1].strip()
            year = els[2].strip()
            volume = els[3].strip()

            mkey = '-'.join([
                title,
                year,
                volume
            ])

            if mkey not in title_year_volume_to_issn:
                title_year_volume_to_issn[mkey] = {main_issn}
            else:
                title_year_volume_to_issn[mkey].add(main_issn)

    return title_year_volume_to_issn


def load_equations(path: str, sep='|'):
    key_to_equation_params = {}

    if path:
        with open(path) as fin:
            csv_reader = csv.DictReader(fin, delimiter=sep)

            for row in csv_reader:
                if row['ISSN'] not in key_to_equation_params:
                    key_to_equation_params[row['ISSN']] = (float(row['a']), float(row['b']))

    return key_to_equation_params


def load_refs_from_csv(path: str, delimiter: str):
    with open(path) as fin:
        counter = 0
        csv_reader = csv.DictReader(fin, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL, quotechar='"', escapechar='\\')
        for i in csv_reader:
            counter += 1
            if counter % 10000 == 0:
                print('Linha %d' % counter)
            yield i


def load_crossref_results_dois(path: str):
    dois = set()

    with open(path) as fin:
        for row in fin:
            data = json.loads(row)

            doi = data['url_searched'].replace('https://api.crossref.org/works/', '')
            if doi:
                dois.add(doi.lower())

    return dois
