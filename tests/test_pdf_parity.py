import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pdf_parity import assert_narrative_parity


class PDFParity(unittest.TestCase):
    def setUp(self):
        self.data = {'chapters':[{'paragraphs':[
            {'id':'first','runs':[{'text':'First μ paragraph.'}]},
            {'id':'last','runs':[{'text':'Final paragraph!'}]}
        ]}]}
        self.fonts = {'fixture':{ord(c):True for c in 'First μ paragraph.Final!'}}

    def test_wrapping_preserves_narrative(self):
        self.assertEqual(assert_narrative_parity('First μ para\ngraph.\nFinal paragraph!',
                                               self.data,self.fonts),2)

    def test_missing_changed_and_reordered_paragraphs_fail(self):
        for text in ['First μ paragraph.', 'First u paragraph. Final paragraph!',
                     'Final paragraph! First μ paragraph.']:
            with self.subTest(text=text), self.assertRaises(AssertionError):
                assert_narrative_parity(text,self.data,self.fonts)

    def test_missing_font_glyph_fails_even_when_pdf_extraction_retains_it(self):
        del self.fonts['fixture'][ord('μ')]
        with self.assertRaisesRegex(AssertionError,'missing.*μ'):
            assert_narrative_parity('First μ paragraph. Final paragraph!',self.data,self.fonts)


if __name__ == '__main__':
    unittest.main()
