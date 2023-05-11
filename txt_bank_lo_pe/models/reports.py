import base64
import os
import tempfile
import zipfile


class BankReportTxt(object):

    def __init__(self, filename, code, data):
        self.data = data
        self.code = code
        self.filename = self.set_filename(filename)

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        if self.code == '09':
            return '{} - Scotiabank.zip'.format(filename)
        elif self.code == '02':
            return '{} - BCP.txt'.format(filename)
        elif self.code == '03':
            return '{} - Interbank.txt'.format(filename)
        elif self.code == '11':
            return '{} - BBVA.txt'.format(filename)
        else:
            return '{}.txt'.format(filename)

    def get_content(self):
        template = '{}\r\n'
        raw = template.format(self.data['row1']) if self.data.get('row1') else ''
        for value in self.data['row2']:
            raw += template.format(value)
        if self.code == '09':
            tmp_dir = self.generate_tmp_dir(raw)
            zip_dir = self.generate_zip(tmp_dir)
            f = open(zip_dir, "rb").read()
            return base64.encodebytes(f)
        else:
            return base64.encodebytes(raw.encode('cp1252'))

    @staticmethod
    def generate_tmp_dir(xmlstr):
        tmp_dir = tempfile.mkdtemp()
        with open(os.path.join(tmp_dir, 'Reporte.txt'), 'w') as f:
            f.write(xmlstr)
        return tmp_dir

    def generate_zip(self, tmp_dir):
        zip_filename = os.path.join(tmp_dir, self.filename)
        with zipfile.ZipFile(zip_filename, 'w') as docx:
            docx.write(os.path.join(tmp_dir, 'Reporte.txt'), 'Reporte.txt')
        return zip_filename
