from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import unittest2 as unittest

import sys
if sys.version_info.major == 2:
    from mock import Mock, patch, PropertyMock
elif sys.version_info.major == 3:
    from unittest.mock import Mock, patch, PropertyMock


import os
import shutil
from tempfile import NamedTemporaryFile, mkdtemp
import topicexplorer.lib.pdf


class TestPdf(unittest.TestCase):
    @patch('topicexplorer.lib.pdf.subprocess.check_output')
    def test_convert_pdfminer(self, not_found_mock):
        not_found_mock.return_value = b''
        out = topicexplorer.lib.pdf.convert("www/papers/aaai15-topic-explorer-demo.pdf")
        self.assertGreater(len(out), 0)
    
    def test_convert_pdftotext(self):
        out = topicexplorer.lib.pdf.convert("www/papers/aaai15-topic-explorer-demo.pdf")
        self.assertGreater(len(out), 0)

    def test_main(self):
        output_dir = mkdtemp()
        topicexplorer.lib.pdf.main("www/papers/aaai15-topic-explorer-demo.pdf",
            output_dir=output_dir)
        self.assertEqual(1, len(os.listdir(output_dir)))
        shutil.rmtree(output_dir)

    def test_convert_and_write(self):
        output_dir = mkdtemp()
        topicexplorer.lib.pdf.convert_and_write("www/papers/aaai15-topic-explorer-demo.pdf",
            output_dir=output_dir, overwrite=True, verbose=True)
        self.assertEqual(1, len(os.listdir(output_dir)))
        shutil.rmtree(output_dir)


if __name__ == '__main__':
    #Define and run test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPdf)
    unittest.TextTestRunner(verbosity=2).run(suite)
