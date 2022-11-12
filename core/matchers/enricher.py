from scielo_scholarly_data import standardizer

from core.matchers import result_code
from core.matchers import exceptions

import re


class Enricher:
    def __init__(self, min_word_length=2, min_title_length=6, min_words_number=2, min_comparable_words_number=2):
        self.correction_bases = {}
        self.min_word_length = min_word_length
        self.min_title_length = min_title_length
        self.min_words_number = min_words_number
        self.min_comparable_words_number = min_comparable_words_number


    def load_linear_regressions(self, path_linear_regressions):
        self.correction_bases['issn_to_linear_regression'] = ...


    def load_primary_correction_base(self, path_primary_correction_base):
        self.correction_bases['issnl_to_metadata'] = ...
        self.correction_bases['title_to_issnl'] = ...


    def load_secondary_correction_base(self, path_secondary_correction_base):
        self.correction_bases['journal_year_volume_to_issnl'] = ...


    def load_terciary_correction_base(self, path_terciary_correction_base):
        self.correction_bases['journal_year_volume_to_issnl_artifitial'] = ...


    def extract_basic_citation_data(self, citation):
        try:
            journal_title = standardizer.journal_title_for_deduplication(citation.cited_journal).upper()
        except AttributeError:
            ...

        if not journal_title:
            try:
                journal_title = standardizer.journal_title_for_deduplication(citation.cited_source).upper()
            except AttributeError:
                raise exceptions.EmptyCitedJournalTitleError('Título citado padronizado está vazio')
        
        try:
            year = standardizer.document_publication_date(citation.cited_year, only_year=True)
        except Exception:
            raise exceptions.EmptyCitedYearError('Ano citado está vazio')

        try:
            volume = standardizer.issue_volume(citation.cited_vol)
        except Exception:
            raise exceptions.InvalidCitedVolumeError('Volume citado não é numérico ou está vazio')

        return {
            'cited_journal': journal_title,
            'cited_year': year,
            'cited_volume': volume,
        }


    def infer_volume(self, issn, year):
        try:
            a, b = self.correction_bases['issn_to_linear_regression'][issn]
        except KeyError:
            raise exceptions.LinearRegressionDoesNotExistError(f'Não existe regressão linear para ISSN {issn}')
        
        volume = round(a + (b * year))
        if volume == 0: 
            volume += 1

        return {
            'cited_volume': volume,
            'inferred_volume': True,
        }


    def do_exact_match(self, citation):
        citation_data = self.extract_basic_citation_data(citation)
        try:
            cited_issnls = self.correction_bases['title_to_issnl'][citation_data['cited_journal']].split('#')
        except KeyError:
            raise exceptions.ExactMatchTitleNotInCorrectionBaseError('Não foi possível encontrar o título {cited_journal} na base de correção primária')

        cited_issnls = [standardizer.journal_issn(i) for i in cited_issnls]
        citation_data['cited_issnl_len'] = len(cited_issnls)

        if len(cited_issnls) == 1:
            citation_data['cited_issnl'] = list(cited_issnls)[0]
            citation_data['result_code'] = result_code.SUCCESS_EXACT_MATCH
            return citation_data
        else:
            return self.do_gold_validation(cited_issnls, citation_data, 'exact')


    def generate_year_volume_key(self, cited_journal, cited_year, cited_volume, delimiter='-'):
        return delimiter.join([
            cited_journal,
            cited_year,
            cited_volume,
        ])

    
    def do_gold_validation(self, issnl_list, citation_data, mode):
        if not citation_data['cited_year'].isdigit():
            raise exceptions.ValidationIssnYearIsNotDigitError(f'Ano não é digito {citation_data}')

        if not citation_data['cited_volume']:
            raise exceptions.VolumeIsUnknowError(f'Volume é desconhecido: {citation_data}')

        journal_year_volume_key = self.generate_year_volume_key(citation_data)

        try:
            cited_issnls_via_jyv_key = self.correction_bases['journal_year_volume_to_issnl'][journal_year_volume_key]
        except KeyError:
            raise exceptions.GoldValidationFailureKeyDoesNotExistError('Chave f{journal_year_volume_key} não existe na base de correção secundária')

        cited_issnls_via_jyv_key = [standardizer.journal_issn(i) for i in cited_issnls_via_jyv_key]

        if len(cited_issnls_via_jyv_key) == 1:
            cited_issnl = list(cited_issnls_via_jyv_key)[0]

            if cited_issnl in issnl_list:
                citation_data['cited_issnl'] = list(cited_issnls_via_jyv_key)[0]
                citation_data['result_code'] = result_code.SUCCESS_EXACT_MATCH_YEAR_VOL if mode == 'exact' else result_code.SUCCESS_FUZZY_MATCH_YEAR_VOL
                return citation_data
            
            raise exceptions.GoldValidationFaileureIssnOutOfListError('Chave f{journal_year_volume_key} aponta para um ISSN que não está em {issn_list}')
        else:
            return self.do_silver_validation(issnl_list, citation_data, mode)       


    def do_silver_validation(self, issnl_list, citation_data, mode):
        title_year_volume_inferred = set()

        for issnl in issnl_list:
            try:
                issnl_volume_inferred = self.infer_volume(issnl, citation_data['cited_year'])
            except exceptions.LinearRegressionDoesNotExistError:
                continue

            for vol in [vol for vol in range(issnl_volume_inferred - 1, issnl_volume_inferred + 2)]:
                title_year_volume_inferred.add(self.generate_year_volume_key(
                    citation_data['cited_journal',
                    citation_data['cited_year'],
                    vol, 
                ]))

                citation_data['cited_volume_inferred'].append(vol)

        inferred_yvk_issns = set()
        for key in title_year_volume_inferred:
            try:
                inferred_yvk_issns = inferred_yvk_issns.union(self.correction_bases['journal_year_volume_to_issnl'][key])
            except KeyError:
                ...

        inferred_yvk_issns = [standardizer.journal_issn(i) for i in inferred_yvk_issns]

        if len(inferred_yvk_issns) == 1:
            citation_data['cited_issnl'] = list(inferred_yvk_issns)[0]
            citation_data['result_code'] = result_code.SUCCESS_EXACT_MATCH_YEAR_VOL_INF if mode == 'exact' else result_code.SUCCESS_FUZZY_MATCH_YEAR_VOL_INF
            return citation_data
        else:
            return self.do_bronze_validation(issnl_list, citation_data, mode)


    def do_bronze_validation(self, issnl_list, citation_data, mode):
        journal_year_volume_key = self.generate_year_volume_key(citation_data)

        try:
            cited_issnls_via_jyv_key = self.correction_bases['journal_year_volume_to_issnl_artifitial'][journal_year_volume_key]
        except KeyError:
            raise exceptions.BronzeValidationFailureKeyDoesNotExistError('Chave f{journal_year_volume_key} não existe na base de correção terciária')

        cited_issnls_via_jyv_key = [standardizer.journal_issn(i) for i in cited_issnls_via_jyv_key]

        if len(cited_issnls_via_jyv_key) == 1:
            cited_issnl = list(cited_issnls_via_jyv_key)[0]

            if cited_issnl in issnl_list:
                citation_data['cited_issnl'] = list(cited_issnls_via_jyv_key)[0]
                citation_data['result_code'] = result_code.SUCCESS_EXACT_MATCH_YEAR_VOL if mode == 'exact' else result_code.SUCCESS_FUZZY_MATCH_YEAR_VOL
                return citation_data
            
            raise exceptions.BronzeValidationFaileureIssnOutOfListError('Chave f{journal_year_volume_key} aponta para um ISSN que não está em {issn_list}')
        else:
            raise exceptions.BronzeValidationFailureUndecidebleError('Não foi possível decidir qual é o ISSN-L correto para {citation_data}')


    def is_valid_for_fuzzy_matching(self, citation_data, words):        
        if len(citation_data['cited_journal']) >= self.min_title_length:
            if len(words) >= self.min_words_number:
                valid_words = [w for w in words if len(w) >= self.min_word_length]
                return len(valid_words) >= self.min_comparable_words_number

        return False


    def do_fuzzy_match(self, citation):
        citation_data = self.extract_basic_citation_data(citation)

        if not citation_data['cited_year'].isdigit():
            citation_data['result_code'] = result_code.ERROR_FUZZY_MATCH_INVALID_YEAR
            raise exceptions.ValidationIssnYearIsNotDigitError(f'Ano não é digito {citation_data}')

        words = citation_data['cited_journal'].split(' ')

        fuzzy_matches = []

        if self.is_valid_for_fuzzy_matching(citation_data, words):
            pattern = r'[\w|\s]*'.join([word for word in words]) + '[\w|\s]*'

            title_pattern = re.compile(pattern, re.UNICODE)

            for oficial_title in [ot for ot in self.correction_bases['title_to_issnl'].keys() if ot.startswith(words[0])]:
                match = title_pattern.fullmatch(oficial_title)

                if match:
                    fuzzy_matches.extend(self.correction_bases['title_to_issnl'][oficial_title].split('#'))
        
        cited_issnls = set([standardizer.journal_issn(f) for f in fuzzy_matches])

        if len(cited_issnls) == 0:
            raise exceptions.FuzzyMatchTitleNotInCorrectionBaseError('Não foi possível encontrar o título {cited_journal} na base de correção primária')

        citation_data['cited_issnl_len'] = len(cited_issnls)

        return self.do_gold_validation(cited_issnls, citation_data, 'fuzzy')
