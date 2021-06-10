import os
import json

class File:
    @staticmethod
    def save_file(filename, content, rel_path=None):
        filepath = File.get_filepath(rel_path=rel_path)
        if not os.path.isdir(filepath):
            os.mkdir(filepath)

        mode = 'a'
        full_path = File.get_filename(filename, rel_path=rel_path)
        if os.path.isfile(full_path):
            mode = 'w'

        with open(full_path, mode, encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def read_file(filename, rel_path=None, type='txt'):
        txt = File.read_file_txt(filename, rel_path=rel_path)
        if type == 'json':
            return json.loads(txt)
        else:
            return txt

    @staticmethod
    def read_file_txt(filename, rel_path=None):
        filepath = File.get_filename(filename, rel_path=rel_path)
        result = ''
        with open(filepath) as lines:
            for line in lines:
                result += line
        return result

    @staticmethod
    def get_filepath(rel_path=None):
        filepath = os.getcwd()
        if isinstance(rel_path, str):
            filepath = os.path.join(filepath, rel_path)
        return filepath


    @staticmethod
    def get_filename(filename, rel_path=None):
        filepath = File.get_filepath(rel_path=rel_path)
        return os.path.join(filepath, filename)