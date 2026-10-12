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
    def test_image_validation(self):
        candidate = {"name": "골목", "image_prompt": "A neon alley.",
                     "animation_notes": "간판 깜박임", "reference_ids": []}
        prompt.validate_result({"candidates": [candidate]}, 1)
        for field, value in (("image_prompt", " "), ("animation_notes", None),
                             ("reference_ids", "ref"), ("reference_ids", [1])):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                prompt.validate_result({"candidates": [{**candidate, field: value}]}, 1)
        with self.assertRaises(ValueError):
            prompt.validate_result({"candidates": [candidate]}, 2)

    def test_removed_music_options_fail_before_network(self):
        for options in (["--mode", "music"], ["--genre", "pop"], ["--vocals", "vocals"],
                        ["--lyrics"], ["--lyrics-language", "Japanese"]):
            with self.subTest(options=options), patch("sys.argv", ["prompt.py", "--brief", "test", *options]), \
                    patch.object(prompt, "request_json") as request, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    prompt.main()
                self.assertEqual(error.exception.code, 2)
                request.assert_not_called()

    def test_image_saved_and_raw_failure_retained(self):
        for valid in (True, False):
            candidate = {"name": "골목", "image_prompt": "A neon alley.",
                         "animation_notes": "간판 깜박임", "reference_ids": []}
            if not valid:
                del candidate["image_prompt"]
            response = {"choices": [{"finish_reason": "stop", "message": {
                "content": json.dumps({"candidates": [candidate]}, ensure_ascii=False)}}]}
            with self.subTest(valid=valid), tempfile.TemporaryDirectory() as directory, \
                    patch.object(prompt, "ROOT", Path(directory)), \
                    patch.dict("os.environ", {"GEMMA_MODEL": "test-model"}), \
                    patch.object(prompt, "request_json", return_value=response) as request, \
                    patch("sys.argv", ["prompt.py", "--brief", "네온 골목", "--count", "1"]), \
                    contextlib.redirect_stdout(io.StringIO()):
                for name, data in (("config/style.json", {}), ("references/catalog.json", [])):
                    path = Path(directory) / name
                    path.parent.mkdir(parents=True)
                    path.write_text(json.dumps(data))
                if valid:
                    prompt.main()
                else:
                    with self.assertRaises(ValueError):
                        prompt.main()
                run, = (Path(directory) / "runs").iterdir()
                self.assertEqual(json.loads((run / "response.json").read_text()), response)
                context = json.loads(request.call_args.kwargs["payload"]["messages"][1]["content"])
                self.assertEqual(context["brief"], "네온 골목")
                if valid:
                    self.assertEqual((run / "prompt-01.txt").read_text(), candidate["image_prompt"] + "\n")
                else:
                    self.assertFalse((run / "candidates.json").exists())

    def test_dry_run_needs_no_service_or_run_directory(self):
        output = io.StringIO()
        with patch("sys.argv", ["prompt.py", "--brief", "비행선 항구", "--dry-run"]), \
                patch.object(prompt, "request_json") as request, contextlib.redirect_stdout(output):
            prompt.main()
        request.assert_not_called()
        messages = json.loads(output.getvalue())
        self.assertEqual(json.loads(messages[1]["content"])["brief"], "비행선 항구")


if __name__ == "__main__":
    unittest.main()
