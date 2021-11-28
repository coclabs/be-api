from os import environ

from moss import Moss
from moss_result import MossResult
from moss_transformer import MossTransformer
from moss_transformer import MossTransform

_id = environ.get('MOSS_ID')

if __name__ == '__main__':
    def report_callback(file_path, display_name):
        print('file_path:', file_path)
        print('display_name:', display_name)
        # print('*', end='', flush=True)


    base_path = 'bases\\'
    sample_path = 'samples\\'

    with open(base_path + 'base_0.txt') as base_0, \
            open(base_path + 'base_1.txt') as base_1, \
            open(sample_path + 'sample_0.py') as sample_0, \
            open(sample_path + 'sample_1.py') as sample_1, \
            open(sample_path + 'sample_4.py') as sample_2, \
            open(sample_path + 'sample_5.py') as sample_3:

        _moss = Moss(user_id=_id, language='python')
        _moss.set_comment_string('test commentXYZ')
        _moss.set_ignore_limit(1000000)
        # _moss.set_experimental_server(1)
        _moss.add_base_content(base_0.read())
        _moss.add_base_content(base_1.read())
        _moss.add_content(sample_0.read())
        _moss.add_content(sample_1.read())
        _moss.add_content(sample_2.read())
        _moss.add_content(sample_3.read())

        # Standford Moss is currently not stable, tcp message will not be send
        report_url = _moss.send(report_callback)
        # report_url = 'http://moss.stanford.edu/results/6/3900184024564/'
        print('report:', report_url)

        _moss_result = MossResult(report_url)
        # Stanford Moss is currently not stable, previous result will be used for demo instead
        # _moss_result = MossResult('http://moss.stanford.edu/results/0/8627166986438/')
        _moss_generated = _moss_result.generate()

        print('*' * 50)
        print('moss generated result:')
        for key, value in _moss_generated.items():
            print(key, value)

        _moss_transformer = MossTransformer(files=_moss_generated)
        transformed_index = _moss_transformer.transform(('index.html',))
        if transformed_index:
            transformed_records = []
            for record in transformed_index:
                transformed_records.append(
                    _moss_transformer.transform(
                        files=(
                            ('-top.'.join(record['source'].split('.', maxsplit=1))),
                            record['file1']['source'],
                            record['file2']['source']
                        ),
                        transformer=MossTransform.transform_record,
                        match_meta=record,
                    )
                )

            import json
            with open('output.log', 'wt') as file:
                file.write('=====Parsed index=====\n')
                file.write(json.dumps(transformed_index, indent=4)+'\n'*2)
                file.write('=====Parsed record=====\n')
                file.write(json.dumps(transformed_records, indent=4))
                print('wrote output to output.log')
                # print(transformed_index)
                # print(transformed_record_0)

    # Save report file
    # _moss.saveWebPage(report_url, "report.html")
    # _moss.download_report(report_url, "report_w.html", connections=8, log_level=10,
    #                        on_read=lambda url: print('*', end='', flush=True))
