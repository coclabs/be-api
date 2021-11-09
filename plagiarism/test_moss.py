from moss import Moss
from moss_result import MossResult
from moss_transformer import MossTransformer
from moss_transformer import MossTransform

_id = '731376226'

if __name__ == '__main__':
    def report_callback(file_path, display_name):
        print('file_path:', file_path)
        print('display_name:', display_name)
        # print('*', end='', flush=True)


    base_path = 'bases\\'
    sample_path = 'samples\\'

    with open(base_path + 'base_0.txt') as base_0, \
            open(base_path + 'base_1.txt') as base_1, \
            open(sample_path + 'sample_3.py') as sample_0, \
            open(sample_path + 'sample_0.py') as sample_1:

        _moss = Moss(user_id=_id, language='python')
        _moss.set_comment_string('test commentXYZ')
        _moss.set_ignore_limit()
        _moss.add_base_content(base_0.read())
        _moss.add_base_content(base_1.read())
        _moss.add_content(sample_0.read())
        _moss.add_content(sample_1.read())

        report_url = _moss.send(report_callback)
        print(report_url)

        _moss_result = MossResult(report_url)
        _moss_generated = _moss_result.generate()

        print('*' * 50)
        print('moss generated result:')
        for key, value in _moss_generated.items():
            print(key, value)

        _moss_transformer = MossTransformer(files=_moss_generated)
        _final_result = {
            'index': _moss_transformer.transform(MossTransform.transform_index),
        }
        print(_final_result)

    # Save report file
    # _moss.saveWebPage(report_url, "report.html")
    # _moss.download_report(report_url, "report_w.html", connections=8, log_level=10,
    #                        on_read=lambda url: print('*', end='', flush=True))
