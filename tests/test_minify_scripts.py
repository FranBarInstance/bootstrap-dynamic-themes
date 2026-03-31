import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    module_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


minify = load_module("btdt_minify", "btdt/scripts/minify.py")
minify_all = load_module("btdt_minify_all", "btdt/scripts/minify-all.py")


class MinifyTests(unittest.TestCase):
    def test_iter_targets_skips_minified_and_excluded_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "ok.css").write_text("body {}", encoding="utf-8")
            (root / "skip.min.css").write_text("body{}", encoding="utf-8")
            excluded = root / ".venv"
            excluded.mkdir()
            (excluded / "ghost.css").write_text("body {}", encoding="utf-8")

            targets = list(minify.iter_targets(root, "preset"))

            self.assertEqual(targets, [root / "ok.css"])

    def test_resolve_css_imports_inlines_local_files_and_keeps_external_or_media_imports(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            preset = root / "preset.css"
            imported = root / "partials" / "palette.css"
            imported.parent.mkdir()
            imported.write_text(":root { --x: 1; }", encoding="utf-8")
            preset.write_text(
                '\n'.join(
                    [
                        '@import "./partials/palette.css";',
                        '@import "https://example.com/external.css";',
                        '@import "./print.css" print;',
                        "body { color: red; }",
                    ]
                ),
                encoding="utf-8",
            )

            bundled = minify.resolve_css_imports(preset)

            self.assertIn(":root { --x: 1; }", bundled)
            self.assertIn('@import "https://example.com/external.css";', bundled)
            self.assertIn('@import "./print.css" print;', bundled)

    def test_rewrite_font_urls_and_hoist_imports_to_top(self):
        css = "\n".join(
            [
                "body { color: red; }",
                '@import "https://example.com/a.css";',
                "@font-face { src: url('demo.ttf'); }",
            ]
        )

        rewritten = minify.rewrite_font_urls(
            css,
            Path("project/fonts/demo/demo.css"),
            Path("project/themes/preset/theme.css"),
        )
        hoisted = minify.hoist_imports_to_top(rewritten)

        self.assertIn("url('../../fonts/demo/demo.ttf')", hoisted)
        self.assertTrue(hoisted.startswith('@import "https://example.com/a.css";'))


class MinifyAllTests(unittest.TestCase):
    def test_resolve_python_executable_prefers_posix_venv(self):
        fake_python = Path("scripts/.venv/bin/python")

        with mock.patch.object(minify_all, "VENV_PYTHON_POSIX", fake_python), \
             mock.patch.object(minify_all, "VENV_PYTHON_WINDOWS", Path("scripts/.venv/Scripts/python.exe")):
            with mock.patch.object(Path, "exists", autospec=True) as exists_mock:
                exists_mock.side_effect = lambda path_obj: path_obj == fake_python
                resolved = minify_all.resolve_python_executable()

        self.assertEqual(resolved, fake_python)

    def test_run_minify_invokes_subprocess_with_local_venv_python(self):
        fake_python = Path("scripts/.venv/bin/python")
        fake_target = Path("theme-dir")

        with mock.patch.object(minify_all, "resolve_python_executable", return_value=fake_python), \
             mock.patch.object(minify_all.subprocess, "run") as run_mock:
            minify_all.run_minify("preset", fake_target)

        run_mock.assert_called_once_with(
            [str(fake_python), str(minify_all.MINIFY_PY), "preset", str(fake_target.resolve())],
            cwd=minify_all.SCRIPT_DIR,
            check=True,
        )

    def test_main_runs_normal_directories_before_preset_directories(self):
        calls = []

        with mock.patch.object(minify_all, "run_minify", side_effect=lambda mode, target: calls.append((mode, target))):
            result = minify_all.main()

        self.assertEqual(result, 0)
        expected = [("normal", path) for path in minify_all.NORMAL_DIRS] + [
            ("preset", path) for path in minify_all.PRESET_DIRS
        ]
        self.assertEqual(calls, expected)


if __name__ == "__main__":
    unittest.main()
