"""Keep the historical standalone module shim narrow and force its retirement."""
from pathlib import Path
import hashlib,json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
PATHS={'layouts/_partials/head/custom-icons.html','layouts/_partials/head/theme-styles.html','static/brand/hub.svg'}
class KitCompatibility(unittest.TestCase):
    def test_compatibility_copies_are_exact_and_retire_with_the_old_pin(self):
        pin=re.search(r'github\.com/boulingua/kit(?:/v[0-9]+)?\s+(\S+)',(ROOT/'go.mod').read_text())[1]
        manifest=ROOT/'kit-compatibility.json'
        if manifest.exists():
            data=json.loads(manifest.read_text());self.assertEqual(data['kit_pin'],'v1.22.0')
            self.assertEqual(pin,data['kit_pin'],'Remove the bounded compatibility copies when promoting the kit pin')
            self.assertEqual(set(data['files']),PATHS)
            for relative,digest in data['files'].items():
                self.assertEqual(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(),digest,relative)
        else:
            self.assertNotEqual(pin,'v1.22.0','The historical module needs its declared compatibility copies')
            self.assertFalse(any((ROOT/p).exists() for p in PATHS),'Retired compatibility files must not shadow the new shared kit')
