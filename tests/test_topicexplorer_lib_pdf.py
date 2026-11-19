import unittest

from unittest.mock import Mock, patch, PropertyMock


import os
import shutil
from tempfile import NamedTemporaryFile, mkdtemp
import topicexplorer.lib.pdf
from topicexplorer.lib.util import get_static_resource_path

TEST_PDF = get_static_resource_path('www/papers/aaai15-topic-explorer-demo.pdf')


class TestPdf(unittest.TestCase):
    @patch('topicexplorer.lib.pdf.subprocess.check_output')
    def test_convert_pdfminer(self, not_found_mock):
        not_found_mock.return_value = b''
        out = topicexplorer.lib.pdf.convert(TEST_PDF)
        self.assertGreater(len(out), 0)
    
    def test_convert_pdftotext(self):
        out = topicexplorer.lib.pdf.convert(TEST_PDF)
        self.assertGreater(len(out), 0)

    def test_main(self):
        output_dir = mkdtemp()
        topicexplorer.lib.pdf.main(TEST_PDF,
            output_dir=output_dir)
        self.assertEqual(1, len(os.listdir(output_dir)))
        shutil.rmtree(output_dir)

    def test_convert_and_write(self):
        output_dir = mkdtemp()
        topicexplorer.lib.pdf.convert_and_write(TEST_PDF,
            output_dir=output_dir, overwrite=True, verbose=True)
        self.assertEqual(1, len(os.listdir(output_dir)))
        shutil.rmtree(output_dir)


if __name__ == '__main__':
    #Define and run test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPdf)
    unittest.TextTestRunner(verbosity=2).run(suite)
