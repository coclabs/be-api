import bs4

from enum import Enum

_markup_parser = 'lxml'
report_root = 'report_w.html'


class MossTransform(Enum):
    @staticmethod
    def transform_index(self):
        index_html = self.files.get('index.html')
        document = bs4.BeautifulSoup(index_html, _markup_parser)

        for tr in document.table.find_all('tr'):
            if not tr.td:
                continue

            _row = {
                'file1': None,
                'file2': None,
                'source': None,
                'length': None
            }

            for i, td in enumerate(tr.find_all('td'), start=1):
                anchor = td.a
                if anchor:
                    filename, similar_percent = anchor.string.split(maxsplit=1)

                    if not _row['source']:
                        _row['source'] = anchor['href']

                    _row[f'file{i}'] = {
                        'name': filename,
                        'source': f'{_row["source"].split(".", maxsplit=1)[0]}-{i - 1}.html',
                        'percent': similar_percent.strip('()% ')
                    }

                else:
                    _row['length'] = td.string.strip()

            self.records.append(_row)
        self.result['index_records'] = self.records

    @staticmethod
    def transform_records(self):
        for record in self.records:
            with open(f'{report_root}\\{"-top.".join(record["source"].split(".", maxsplit=1))}') as match_file:
                document = bs4.BeautifulSoup(match_file, _markup_parser)
                match_table_rows = document.table.find_all('tr')

                _match = {
                    f'{"-0.".join(record["source"].split(".", maxsplit=1))}': [],
                    f'{"-1.".join(record["source"].split(".", maxsplit=1))}': [],
                }

                for match_table_row in match_table_rows:
                    for match_table_row_td in match_table_row.find_all('td'):
                        anchor = match_table_row_td.a
                        match_line = anchor.string
                        if match_line:
                            _match[anchor['href'].rstrip('#01')].append(match_line)

                for i, file in enumerate((record['file1'], record['file2']), start=1):
                    with open(f'{report_root}\\{file["source"]}') as source_file:
                        document = bs4.BeautifulSoup(source_file, _markup_parser)
                        source_sections = document.body.pre
                        self.result[f'file{i}'] = {
                            **file,
                            'code': '',
                            'match': _match[file['source']]
                        }

                        for source_line in source_sections.stripped_strings:
                            self.result[f'file{i}']['code'] += source_line

            self.result['source'] = record['source']
            self.result['length'] = record['length']


class MossTransformer:

    def __init__(self, files, markup_parser='lxml'):
        self.markup_parser = markup_parser
        self.files = files
        self.records = []
        self.result = {}

    def transform(self, callback=MossTransform.transform_index, *args, **kwargs):
        callback(self, *args, **kwargs)
        return self.result
