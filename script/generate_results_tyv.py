import argparse
import csv
import json
import pickle

from scielo_scholarly_data import standardizer


FIELDNAMES = [
	'id',
	'our_issnl_set',
	'our_issnl_set_method',
	'our_title_year_volume_key',
	'cited_year',
	'cited_vol',
	'cited_journal',
	'cited_doiset',
	'citation_count',
	'gold_issnl_set',
	'gold_stz_issnl_set',
	'gold_issnl_set_method',
]
METHOD_ISSNL_FROM_DOI = 1
METHOD_ISSNL_FROM_OUR = 2
METHOD_ISSNL_UNDEFINED = -1


def _get_program_args():
	parser = argparse.ArgumentParser()

	parser.add_argument(
		'--input',
		required=True,
		help='Arquivo a ser tratado'
	)

	parser.add_argument(
		'--doi_to_issnl',
		required=True,
		help='Mapa de DOI para ISSN-L'
	)

	parser.add_argument(
		'--output',
		default='output.csv',
		help='Arquivo de saída'
	)

	parser.add_argument(
		'--issn_to_issnl',
		required=True,
		help='Arquivo que contém mapeamento de ISSN para ISSN-L'
	)

	return parser.parse_args()


def _read_doi_issnl_map(path):
	with open(path, 'rb') as fin:
		d = pickle.load(fin)
		print(f'Há {len(d.keys())} chaves')
		return d


def _read_issn_issnl_map(path):
	issn_to_issnl = {}

	with open(path) as fin:
		# ISSNL|MAIN_TITLE|MAIN_ABBREV_TITLE|ISSNs|OTHER_TITLEs|PORTAL_ISSN|DOAJ|LATINDEX|NLM|SCIELO|SCIMAGO_JR|SCOPUS|ULRICH|WOS|WOS_JCR|COUNTRIES|YEARS
		for line in fin:
			els = line.strip().split('|')
			issnl = els[0]
			issns = els[3].split('#')

			for i in issns:
				issn_to_issnl[i] = issnl
	print(f'Há {len(issn_to_issnl.keys())} chaves')
	return issn_to_issnl


def _read_line(path):
	with open(path) as fin:
		for i in fin:
			yield json.loads(i)


def _start_output(path, fieldnames, delimiter='|'):
	fout = open(path, 'w')
	csvw = csv.DictWriter(fout, fieldnames=fieldnames, delimiter=delimiter, quoting=csv.QUOTE_NONE, escapechar='\"', extrasaction='ignore')
	csvw.writeheader()
	return csvw


def _write_line(ref, output):
	# id
	# our_issnl_set
	# our_issnl_set_method
	# our_title_year_volume_key
	# cited_year
	# cited_vol
	# cited_journal
	# cited_doiset
	# citation_count
	# gold_issnl_set
	# gold_stz_issnl_set
	# gold_issnl_set_method
	for k, v in ref.items():
		if isinstance(v, str):
			ref[k] = v.replace('|', ';')
	output.writerow(ref)


def _extract_issnl_from_doi(ref, doi2issnl):
	issnls = set()

	if ref['cited_doiset'] is None:
		ref['cited_doiset'] = ''

	ref['cited_doiset'] = ref['cited_doiset'].lower()

	for d in ref['cited_doiset'].split(' '):
		dstz = standardizer.document_doi(d, return_mode='path')
		if isinstance(dstz, str):
			if dstz in doi2issnl:			
				issnls = issnls.union(doi2issnl[dstz])

	return '#'.join(issnls)


def _extract_issnl_from_our(ref):
	ref['our_issnl_set_method'] = ref['result_code']
	ref['our_title_year_volume_key'] = ref['title_year_volume_key']

	if ref['result_code'] in {0, 1, 2, 3, 4, 11, 12, 13, 14}:
		ref['our_issnl_set'] = ref['cited_issnl']
	else:
		ref['our_issnl_set'] = ''	

	return ref['our_issnl_set']


def _set_gold_issnl_set(ref, doi2issnl):
	_issnl_fd = _extract_issnl_from_doi(ref, doi2issnl)
	if len(_issnl_fd) > 0:
		ref['gold_issnl_set'] = _issnl_fd
		ref['gold_issnl_set_method'] = METHOD_ISSNL_FROM_DOI
		return

	_issnl_fo = _extract_issnl_from_our(ref)
	if len(_issnl_fo) >= 9:
		ref['gold_issnl_set'] = _issnl_fo
		ref['gold_issnl_set_method'] = METHOD_ISSNL_FROM_OUR
		return

	ref['gold_issnl_set'] = ''
	ref['gold_issnl_set_method'] = METHOD_ISSNL_UNDEFINED


def _set_gold_stz_issnl_set(ref, issn2issnl):
	issnls = set()

	for i in ref['gold_issnl_set'].split('#'):
		issnls.add(issn2issnl.get(i, i))

	ref['gold_stz_issnl_set'] = '#'.join(issnls)


def main():
	args = _get_program_args()

	print(f'Lendo mapa de DOI para ISSN a partir de {args.doi_to_issnl}')
	doi2issnl = _read_doi_issnl_map(args.doi_to_issnl)

	print(f'Lendo mapa de ISSN para ISSN-L a partir de {args.issn_to_issnl}')
	issn2issnl = _read_issn_issnl_map(args.issn_to_issnl)

	print(f'Iniciando arquivo de resultados em {args.output}')	
	output = _start_output(args.output, FIELDNAMES)
	line_number = 1

	print(f'Processando {args.input}')
	for ref in _read_line(args.input):
		_set_gold_issnl_set(ref, doi2issnl)
		_set_gold_stz_issnl_set(ref, issn2issnl)
		_write_line(ref, output)

		if line_number % 10000 == 0:
			print(f'Foram processadas {line_number} linhas')

		line_number += 1

if __name__ == '__main__':
	main()
