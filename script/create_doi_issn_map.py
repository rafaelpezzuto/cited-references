import argparse
import json
import pickle
import os


def _get_program_args():
	parser = argparse.ArgumentParser()

	parser.add_argument(
		'--input',
		required=True,
		help='Arquivo a ser tratado'
	)

	parser.add_argument(
		'--doi_to_issn',
		default='',
		help='Arquivo de mapeamento de DOI para ISSN pré-existente'
	)

	return parser.parse_args()


def _read_doi_issn_map(path):
	if os.path.exists(path):
		with open(path, 'rb') as fin:
			return pickle.load(fin)
	return {}


def _write_doi_issn_map(path, data):
	with open(path, 'wb') as fin:
		return pickle.dump(data, fin)


def _read_line(path):
	with open(path) as fin:
		for line in fin:
			yield json.loads(line)


def _extract_mapping(json_line):
	if 'crossref' in json_line:
		root_key = 'crossref'
	elif 'metadata' in json_line:
		root_key = 'metadata'
	elif 'message' in json_line:
		root_key = 'message'
	else:
		print('INVESTIGAR ROOTKEY -----', json_line)

	try:
		doi = json_line[root_key]['DOI']
	except KeyError:
		try:
			doi = json_line['doi']
		except KeyError:
			try:
				doi = json_line['url_searched'].split("https://api.crossref.org/works/")[-1]
			except KeyError:
				doi = ''
				print('INVESTIGAR DOI -----', json_line)
	except TypeError:
		doi = ''
		print('INVESTIGAR ROOTKEY -----', json_line)

	try:
		issn = json_line[root_key]['ISSN']
	except KeyError:
		issn = set()
		print('INVESTIGAR ISSN -----', json_line)
	except TypeError:
		issn = set()
		print('INVESTIGAR ROOTKEY -----', json_line)

	return doi.lower(), set([i.upper() for i in issn])


def main():
	args = _get_program_args()

	doi2issn = _read_doi_issn_map(args.doi_to_issn)

	counter = 0

	for ref in _read_line(args.input):
		counter += 1
		doi, issn = _extract_mapping(ref)

		if doi != '':
			if doi not in doi2issn:
				doi2issn[doi] = set()
			doi2issn[doi] = doi2issn[doi].union(issn)

		if counter % 10000 == 0:
			print('CONTADOR DE LINHAS ----', counter)

	_write_doi_issn_map('newdict.data', doi2issn)


if __name__ == '__main__':
	main()
