import io
import json

import cv2
import pdfplumber
import pytest
from aspose.pdf import Document
from aspose.pdf.devices import Resolution, JpegDevice
from pyzbar import pyzbar


class TestTask:
    correct_pdf = 'test_task.pdf'
    incorrect_pdf = 'test_task_broken.pdf'

    @pytest.mark.xfail(reason='File already exist.')
    def test_format_pdf_to_jpg(self, path="page_pdf"):
        document = Document("test_task.pdf")
        resolution = Resolution(300)
        device = JpegDevice(resolution)
        for i in document.pages:
            image = io.FileIO(path + ".jpg", "x")
            device.process(i, image)
            image.close()

    def test_get_barcode_data(self, path="page_pdf.jpg"):
        img = cv2.imread(path)
        for bar in pyzbar.decode(img, symbols=[pyzbar.ZBarSymbol.CODE128]):
            print(bar)

    @staticmethod
    def pdf_to_json(file_path=None):
        # noinspection PyTypeChecker
        with pdfplumber.PDF(open(file=file_path, mode='br')) as pdf:
            data = {}
            start_list = []
            for string in pdf.pages:
                start_list.append(string.extract_text().replace(': ', ':').replace(' :', ':').split('\n'))
            data.setdefault('title', start_list[0][0])
            start_list[0].pop(0)
            for text in start_list[0]:
                if len(text.split(':')) != 3:
                    try:
                        data.setdefault(text.split(':')[0])
                        data.setdefault(text.split(':')[2])
                    except IndexError:
                        pass

                if len(text.split(':')) == 3:
                    data.setdefault(text.split(':')[0])
                    try:
                        data.setdefault(text.split(':')[1].split(' ')[1])
                    except IndexError:
                        pass
                        data.setdefault(text.split(':')[0])
                        data.setdefault(text.split(':')[1])

            data_2 = {}
            start_list_2 = []
            for string in pdf.pages:
                start_list_2.append(string.extract_text().replace(': ', ':').replace(' :', ':').split('\n'))
            data_2.setdefault('title', start_list_2[0][0])
            start_list_2[0].pop(0)
            for text in start_list_2[0]:
                if len(text.split(':')) != 3:
                    try:
                        if text.split(':')[0] in data.keys() and Exception != IndexError:
                            data_2.setdefault(text.split(':')[0], text.split(':')[1])
                    except IndexError:
                        pass

                if len(text.split(':')) == 3:
                    if text.split(':')[0] in data.keys() and text.split(':')[1].split(' ')[0] not in data.keys():
                        data_2.setdefault(text.split(':')[0], text.split(':')[1].split(' ')[0])
                        data_2.setdefault(text.split(':')[1].split(' ')[1], text.split(':')[2].split(' ')[0])

                    elif text.split(':')[0] in data.keys() and text.split(':')[1].split(' ')[0] in data.keys():
                        data_2.setdefault(text.split(':')[0])

            print(json.dumps(data_2))

            return json.dumps(data_2)

    def test_compare_with_standard(self):
        data = self.pdf_to_json(self.correct_pdf)
        data_2 = self.pdf_to_json(self.correct_pdf)

        for i in range(len(json.loads(data))):
            assert list(json.loads(data).keys())[i] == list(json.loads(data_2).keys())[i], 'Does not meet the standard.'

    @pytest.mark.xfail(reason='Expected fail test')
    def test_compare_with_incorrect_data(self):
        data = self.pdf_to_json(self.correct_pdf)
        data_2 = self.pdf_to_json(self.incorrect_pdf)

        for i in range(len(json.loads(data))):
            assert list(json.loads(data).keys())[i] == list(json.loads(data_2).keys())[i], 'Does not meet the standard.'
