import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("prompt", Path(__file__).resolve().parents[1] / "scripts/prompt.py")
prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt)


class PromptTests(unittest.TestCase):
    def test_lyrics_are_opt_in_and_required_when_requested(self):
        candidate = {"name": "帰り道", "situation": "퇴근길", "suno_prompt": "Bright pop."}
        result = {"candidates": [candidate]}
        prompt.validate_result(result, 1, "music")
        for value in (None, "", "  ", []):
            candidate["lyrics"] = value
            with self.assertRaises(ValueError):
                prompt.validate_result(result, 1, "music", True)
        candidate["lyrics"] = "[Chorus]\n帰り道"
        prompt.validate_result(result, 1, "music", True)
        with self.assertRaises(ValueError):
            prompt.validate_result(result, 1, "music")

    def test_invalid_options_fail_before_network(self):
        for options in (["--lyrics"], ["--mode", "music", "--lyrics-language", "Japanese"],
                        ["--mode", "music", "--lyrics", "--vocals", "instrumental"]):
            with self.subTest(options=options), patch("sys.argv", ["prompt.py", "--brief", "test", *options]), \
                    patch.object(prompt, "request_json") as request, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    prompt.main()
                self.assertEqual(error.exception.code, 2)
                request.assert_not_called()

    def test_lyrics_saved_separately_and_raw_failure_retained(self):
        for valid in (True, False):
            candidate = {"name": "퇴근길", "situation": "하루의 끝", "suno_prompt": "Japanese vocal pop."}
            if valid:
                candidate["lyrics"] = "[Verse 1]\n街の灯り\n[Chorus]\n明日へ"
            response = {"choices": [{"finish_reason": "stop", "message": {
                "content": json.dumps({"candidates": [candidate]}, ensure_ascii=False)}}]}
            with self.subTest(valid=valid), tempfile.TemporaryDirectory() as directory, \
                    patch.object(prompt, "ROOT", Path(directory)), \
                    patch.dict("os.environ", {"GEMMA_MODEL": "test-model"}), \
                    patch.object(prompt, "request_json", return_value=response) as request, \
                    patch("sys.argv", ["prompt.py", "--mode", "music", "--lyrics", "--lyrics-language",
                                       "Japanese", "--brief", "퇴근길 J-pop", "--count", "1"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                if valid:
                    prompt.main()
                else:
                    with self.assertRaises(ValueError):
                        prompt.main()
                run, = (Path(directory) / "runs").iterdir()
                self.assertEqual(json.loads((run / "response.json").read_text()), response)
                context = json.loads(request.call_args.kwargs["payload"]["messages"][1]["content"])
                self.assertEqual(context["vocals"], "vocals")
                self.assertEqual(context["lyrics_language"], "Japanese")
                if valid:
                    self.assertEqual((run / "lyrics-01.txt").read_text(), candidate["lyrics"] + "\n")
                    self.assertEqual((run / "prompt-01.txt").read_text(), candidate["suno_prompt"] + "\n")
                else:
                    self.assertFalse((run / "candidates.json").exists())


if __name__ == "__main__":
    unittest.main()
