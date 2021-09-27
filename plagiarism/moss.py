import socket
import glob

from contextlib import closing

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


class Moss:
    languages = (
        'c',
        'cc',
        'java',
        'ml',
        'pascal',
        'ada',
        'lisp',
        'scheme',
        'haskell',
        'fortran',
        'ascii',
        'vhdl',
        'verilog',
        'perl',
        'matlab',
        'python',
        'mips',
        'prolog',
        'spice',
        'vb',
        'csharp',
        'modula2',
        'a8086',
        'javascript',
        'plsql')
    server = 'moss.stanford.edu'
    port = 7690

    def __init__(self, user_id, language='c', encode='utf-8'):
        self.user_id = user_id
        self.encode = encode
        self.options = {
            'language': 'c',
            'matches': 10,
            'directory': 0,
            'experimental': 0,
            'comment': '',
            'matching_files': 250
        }
        self.base_contents = []
        self.contents = []
        self.report_url = None

        if language in self.languages:
            self.options['language'] = language

    def set_ignore_limit(self, limit):
        self.options['matches'] = limit

    def set_comment_string(self, comment):
        self.options['comment'] = comment

    def set_number_of_matching_files(self, n):
        if n > 1:
            self.options['matching_files'] = n

    def set_directory_mode(self, mode):
        self.options['directory'] = mode

    def set_experimental_server(self, opt):
        self.options['experimental'] = opt

    def add_base_content(self, content, display_name=None):
        if not display_name:
            display_name = f'base_file-{len(self.base_contents)}'
        self.base_contents.append((content, display_name))

    def add_base_contents(self, contents):
        for content in contents:
            self.add_base_content(content.get('content'), content.get('name'))

    def add_content(self, content, display_name=None):
        if not display_name:
            display_name = f'file-{len(self.contents)}'
        self.contents.append((content, display_name))

    def add_contents(self, contents):
        for content in contents:
            self.add_content(content.get('content'), content.get('name'))

    def get_languages(self):
        return self.languages

    def upload_file(self, s, content, display_name, file_id, on_send):
        display_name = display_name.replace(' ', '_').replace('\\', '/')

        content_encoded = content.encode('utf-8')
        content_size = len(content_encoded)
        message = f'file {file_id} {self.options["language"]} {content_size} {display_name}\n'
        s.send(message.encode())
        s.send(content_encoded)

    def send(self, on_send=lambda file_path, display_name: None):
        with closing(socket.socket()) as session:
            session.connect((self.server, self.port))

            session.send(f'moss {self.user_id}\n'.encode())
            session.send(f'directory {self.options["directory"]}\n'.encode())
            session.send(f'X {self.options["experimental"]}\n'.encode())
            session.send(f'maxmatches {self.options["matches"]}\n'.encode())
            session.send(f'show {self.options["matching_files"]}\n'.encode())

            session.send(f'language {self.options["language"]}\n'.encode())
            recv = session.recv(1024)
            if recv == 'no':
                session.send(b'end\n')
                raise Exception('send() => Language not accepted by server')

            for base_content, display_name in self.base_contents:
                self.upload_file(session, base_content, display_name, 0, on_send)

            for index, (content, display_name) in enumerate(self.contents, start=1):
                self.upload_file(session, content, display_name, index, on_send)

            session.send(f'query 0 {self.options["comment"]}\n'.encode())

            response = session.recv(1024)

            session.send(b'end\n')
        report_url = response.decode().replace('\n', '')
        self.report_url = report_url
        return report_url

    def clean(self):
        self.base_contents = []
        self.contents = []
        self.report_url = None

    def saveWebPage(self, url, path):
        if len(url) == 0:
            raise Exception("Empty url supplied")

        response = urlopen(url)
        charset = response.headers.get_content_charset()
        content = response.read().decode(charset)

        f = open(path, 'w', encoding='utf-8')
        f.write(content)
        f.close()
