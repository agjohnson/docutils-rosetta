import unittest

from docutils_rosetta.transforms.pod import PODTransform
from docutils import nodes


class Test(unittest.TestCase):

    def setUp(self):
        self.t = PODTransform()

    def assertParse(self, source, expected, field='document'):
        obj = getattr(self.t.parse(source), field)
        self.assertEqual(obj().asdom().toxml(), expected)

    def test_begin(self):
        self.assertParse(
            'This is a paragraph',
            ('<?xml version="1.0" ?>'
             '<document source="&lt;string&gt;">'
             '<paragraph>This is a paragraph</paragraph>'
             '</document>')
        )
