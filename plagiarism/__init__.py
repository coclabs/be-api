import pathlib
import mosspy

_id = '731376226'


class Moss(mosspy.Moss):

    def __init__(self, *args, base_path='bases', sample_path='samples', **kwargs):
        self.base_path = pathlib.Path(base_path)
        self.sample_path = pathlib.Path(sample_path)
        super().__init__(*args, **kwargs)

    def addBaseFile(self, file_path, display_name=None):
        file_path = str(self.base_path / pathlib.Path(file_path))
        super().addBaseFile(file_path, display_name)

    def addFile(self, file_path, display_name=None):
        file_path = str(self.sample_path / pathlib.Path(file_path))
        super().addFile(file_path, display_name)

    def addFilesByWildcard(self, wildcard):
        file_path = str(self.sample_path / pathlib.Path(wildcard))
        super().addFilesByWildcard(file_path)


if __name__ == '__main__':
    def report_callback(file_path, display_name):
        print('file_path:', file_path)
        print('display_name:', display_name)
        # print('*', end='', flush=True)


    _moss = Moss(user_id=_id, language='python')
    _moss.addBaseFile('base_0.txt')
    _moss.addBaseFile('base_1.txt')
    _moss.addFilesByWildcard('sample_*.py')

    # report_url = _moss.send(report_callback)
    # print(report_url)

    # Save report file
    report_url = 'http://moss.stanford.edu/results/0/8627166986438/'
    _moss.saveWebPage(report_url, "report.html")
    mosspy.download_report(report_url, "report_w.html", connections=16, log_level=10,
                           on_read=lambda url: print('*', end='', flush=True))
