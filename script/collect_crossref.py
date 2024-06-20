import argparse
import asyncio
import html
import json
import logging
import os
import pickle
import textwrap
import time

from aiohttp import ClientSession
from scielo_scholarly_data import standardizer


DIR_DATA = os.environ.get('DIR_DATA', '.')
CROSSREF_URL_WORKS = os.environ.get('CROSSREF_URL_WORKS', 'https://api.crossref.org/works/{}')
CROSSREF_SEMAPHORE_LIMIT = int(os.environ.get('CROSSREF_SEMAPHORE_LIMIT', '20'))


def load_doi_to_issn(path, only_doi=True):
    with open(path, 'rb') as fin:
        doi_to_issn = pickle.load(fin)

        if only_doi:
            return set(list(doi_to_issn.keys()))

        return doi_to_issn


def load_previous_results(dir):
    files = [os.path.join(dir, f) for f in os.listdir(dir) if f.startswith('crossref') and f.endswith('.json')]

    codes = set()

    for f in files:
        with open(f) as fin:
            for line in fin:
                jline = json.loads(line)
                codes.add(jline['_id'])

    return codes


class CrossrefAsyncCollector:
    logging.basicConfig(level=logging.INFO)

    def __init__(self, email, path, dir_results):
        self.email = email
        self.path = path
        self.path_results = os.path.join(dir_results, f'crossref.{time.time()}.json')
        self.codes = self.load_codes(self.path)

    def load_codes(self, path):
        with open(path) as fin:
            for line in fin:
                doi_path = standardizer.document_doi(line, return_mode='path')
                doi_uri = CROSSREF_URL_WORKS.format(doi_path)
                
                if isinstance(doi_path, str):
                    yield {'path': doi_path.lower(), 'uri': doi_uri}

    def parse_result(self, raw):
        raw_status = raw.get('status', '')
        if raw_status == 'ok':
            metadata = raw.get('message')

            if metadata:
                if 'reference' in metadata:
                    metadata.__delitem__('reference')

                return metadata

    def save_result(self, doi_path_to_metadata):
        with open(self.path_results, 'a') as f:
            json.dump(doi_path_to_metadata, f)
            f.write('\n')

    async def run(self, existings_codes):
        sem = asyncio.Semaphore(CROSSREF_SEMAPHORE_LIMIT)
        tasks = []

        async with ClientSession(headers={'mailto:': self.email}) as session:
            for i in self.codes:
                if i['path'] in existings_codes:
                    logging.info(f'{i} ignored')
                else:
                    task = asyncio.ensure_future(self.bound_fetch(i['path'], i['uri'], sem, session))
                    tasks.append(task)

            responses = asyncio.gather(*tasks)
            await responses

    async def bound_fetch(self, path, uri, semaphore, session):
        async with semaphore:
            await self.fetch(path, uri, session)

    async def fetch(self, path, uri, session):
        async with session.get(uri) as response:
            logging.debug('collecting metadata for %s' % path)

            try:
                raw = await response.json(content_type=None)
            except json.decoder.JSONDecodeError:
                logging.debug(f'it was not possible to collect {uri}')
            else:
                metadata = self.parse_result(raw)

                if metadata:
                    logging.info(f'{path} has been collected.')
                    self.save_result({'_id': path, 'crossref': metadata})


def main():
    usage = "collect metadata from the Crossref Service"

    parser = argparse.ArgumentParser(textwrap.dedent(usage))
    parser.add_argument(
        '-e', '--email',
        required=True,
        default=None,
        dest='email',
        help='an e-mail registered in the CrossRef service'
    )
    parser.add_argument(
        '-p', '--path',
        required=True,
        help='a file with DOI codes to be collected from CrossRef'
    )
    parser.add_argument(
        '-d', '--doi_to_issn',
        help='a file in pickle format containing a DOI to ISSN dict'
    )
    parser.add_argument(
        '-r', '--dir_results',
        default=DIR_DATA,
    )

    args = parser.parse_args()

    doi_to_issn = load_doi_to_issn(args.doi_to_issn, only_doi=True)
    print(f'there are {len(doi_to_issn)} codes into DOI to ISSN dict')

    codes_collected = load_previous_results(args.dir_results)
    print(f'{len(codes_collected)} codes has been collected previously')

    codes_to_ignore = doi_to_issn.union(codes_collected)
    try:
        cac = CrossrefAsyncCollector(email=args.email, path=args.path, dir_results=args.dir_results)

        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(cac.run(codes_to_ignore))
        loop.run_until_complete(future)

    except KeyboardInterrupt:
        print("Interrupt by user")


if __name__ == '__main__':
    main()
