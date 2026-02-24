# Enriquecimento de Referências Citadas (cited-references)

Este repositório contém ferramentas para processar referências citadas, com foco em:
1.  **Criação de bases de correção**: Consolidação de dados de periódicos (ISSN, títulos, volume/ano).
2.  **Enriquecimento de citações**: Identificação do ISSN de uma citação com base no título do periódico, ano e volume.

## Instalação

Recomenda-se o uso de um ambiente virtual Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

Ou, caso prefira instalar apenas as dependências:

```bash
pip install -r requirements.txt
```

## Como usar o script de enriquecimento

O script principal para realizar o enriquecimento é o `core/matchers/enrich_references.py`. Ele utiliza bases de correção pré-geradas para validar e completar os dados das citações.

### Exemplo básico de uso

```bash
python core/matchers/enrich_references.py \
    --issnl_to_all base_issnl.csv \
    --title_year_volume_to_issn base_tyv.csv \
    --artifitial_title_year_volume_to_issn base_artificial_tyv.csv \
    --input referencias_entrada.jsonl \
    --output resultados_enriquecidos.jsonl
```

### Parâmetros principais

| Parâmetro | Descrição | Obrigatório |
| :--- | :--- | :---: |
| `--issnl_to_all` | Base de correção GISSN -> DADOS (CSV). | Sim |
| `--title_year_volume_to_issn` | Base de correção Título, Ano, Volume -> ISSN (CSV). | Sim |
| `--artifitial_title_year_volume_to_issn` | Base de correção artificial Título, Ano, Volume -> ISSN (CSV). | Sim |
| `--input` | Arquivo de entrada com as referências a serem enriquecidas. | Não* |
| `--input_dir` | Diretório contendo arquivos de referências. | Não* |
| `--output` | Caminho para o arquivo de saída (padrão: `results.jsonl`). | Não |
| `--input_format` | Formato da entrada: `json` (padrão), `csv`, `elsevier`, `tyv`, `scl24`. | Não |
| `--use_fuzzy` | Ativa a busca aproximada (fuzzy match) para títulos de periódicos. | Não |
| `--equations` | Base de correção de regressão linear (ISSN -> Regressão). | Não |
| `--ignore_previous_result` | Ignora o campo `cited_issnl` se ele já existir na entrada. | Não |

*\*É necessário informar ou `--input` ou `--input_dir`.*

## Formatos de Entrada

O script suporta diferentes formatos de arquivos de entrada através do parâmetro `--input_format`:

-   **json**: Arquivo JSON Lines (padrão).
-   **csv**: Arquivo CSV com delimitador vírgula.
-   **tyv**: Formato específico de Título, Ano, Volume.
-   **elsevier**: Formato de dados provenientes da Elsevier.
-   **scl24**: Formato específico SciELO 24.

## Scripts para geração de bases de correção

Os scripts utilizados para criar as bases de correção exigidas pelo `enrich_references.py` encontram-se no diretório `script/`.
