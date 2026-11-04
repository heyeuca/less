"""Behavioral checks for protocol-v2 transport handling and provenance."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import measure
import protocol

class Followups(unittest.TestCase):
    def test_transport_does_not_hide_meaningful_whitespace(self):
        normalize = protocol.presentation
        source = 'def f():\n    return 1\n'
        self.assertEqual(normalize(source,source), normalize(source,'```python\n'+source+'```\n'))
        self.assertEqual(normalize(source,source), normalize(source,source[:-1]))
        for changed in ['def f():\n return 1\n', source+'\n', source.rstrip()+'  \n']:
            self.assertNotEqual(normalize(source,source),normalize(source,changed))
        self.assertNotEqual(normalize('line  \nnext','line  \nnext'),normalize('line  \nnext','line\nnext'))
        self.assertIsNone(normalize(source,None))

    def test_execution_model_changes_and_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            protocol.save(out/'freeze.json',json.dumps({'inputs':protocol.inputs(),'execution':measure.execution()}))
            with patch.object(measure,'call',return_value=('answer','model-a')),patch.object(measure,'version',return_value='cli-1'):
                measure.recorded_call(out,'claude','x','prompt')
            measure.validate_reply(out,'x','answer','prompt')
            with self.assertRaises(RuntimeError):measure.validate_reply(out,'x','edited','prompt')
            with patch.object(measure,'call',return_value=('other','model-b')),patch.object(measure,'version',return_value='cli-1'):
                with self.assertRaises(RuntimeError):measure.recorded_call(out,'claude','y','prompt')
            frozen=json.loads(protocol.load(out/'freeze.json'))
            self.assertEqual(frozen['models']['claude'],'model-a')
            self.assertFalse(frozen['calls']['y'][-1]['accepted'])
            self.assertEqual(frozen['calls']['x'][0]['cli'],'cli-1')
            with patch.object(measure,'call',return_value=('unknown',None)),patch.object(measure,'version',return_value='cli-1'):
                with self.assertRaises(RuntimeError):measure.recorded_call(out,'claude','z','prompt')
            with patch.object(measure,'GRADER_PROMPT','different'):
                with self.assertRaises(RuntimeError):measure.validate_execution(out)
            with patch.dict(measure.CONFIG,timeout_seconds=321):
                with self.assertRaises(RuntimeError):measure.validate_execution(out)

if __name__=='__main__':unittest.main()
