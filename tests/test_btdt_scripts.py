import importlib.util
import io
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


sync_configs = load_module("sync_configs", "btdt/scripts/sync-configs.py")
export_runtime = load_module("export_runtime", "btdt/scripts/export-runtime.py")


class SyncConfigsTests(unittest.TestCase):
    def test_humanize_slug_preserves_known_acronyms(self):
        self.assertEqual(sync_configs.humanize_slug("dm-sans"), "DM Sans")
        self.assertEqual(sync_configs.humanize_slug("pt-sans"), "PT Sans")
        self.assertEqual(sync_configs.humanize_slug("space-grotesk"), "Space Grotesk")

    def test_categorize_preset_import_maps_accent_variants(self):
        self.assertEqual(
            sync_configs.categorize_preset_import("../styles/accent-left.css"),
            ("accent", "left"),
        )
        self.assertEqual(
            sync_configs.categorize_preset_import("../styles/accent-4.css"),
            ("accentSize", "4"),
        )
        self.assertEqual(
            sync_configs.categorize_preset_import("../styles/accent-secondary.css"),
            ("accentColor", "secondary"),
        )
        self.assertIsNone(
            sync_configs.categorize_preset_import("../styles/accent-unknown.css")
        )

    def test_collect_preset_import_values_warns_on_duplicates_and_unsupported_paths(self):
        warnings = sync_configs.WarningCollector()
        seen, values = sync_configs.collect_preset_import_values(
            "demo",
            [
                "../fonts/inter.css",
                "../styles/accent-left.css",
                "../styles/accent-right.css",
                "../outside/odd.css",
            ],
            warnings,
        )

        self.assertEqual(seen, ["fonts", "accent", "accent"])
        self.assertEqual(values["fonts"], "inter")
        self.assertEqual(values["accent"], "right")
        self.assertIn("[preset:demo] Duplicate import category: accent", warnings.items)
        self.assertIn("[preset:demo] Unsupported import path: ../outside/odd.css", warnings.items)

    def test_validate_preset_metadata_allows_missing_accent_fields_when_accent_is_none(self):
        warnings = sync_configs.WarningCollector()

        sync_configs.validate_preset_metadata(
            "demo",
            {
                "colors": "ocean",
                "fonts": "inter",
                "background": "none",
                "borders": "default",
                "rounding": "default",
                "shadows": "default",
                "spacing": "default",
                "gradients": "default",
                "accent": "none",
            },
            {"accent": "none"},
            warnings,
        )

        self.assertEqual(warnings.items, [])

    def test_write_config_writes_window_assignment_with_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "generated-config.js"

            with mock.patch.object(sync_configs, "ROOT", Path(tmpdir)):
                sync_configs.write_config(output_path, "BTDT_TEST", {"demo": "Demo"})

            content = output_path.read_text(encoding="utf-8")
            self.assertEqual(
                content,
                "// generated-config.js\nwindow.BTDT_TEST = {\n  demo: 'Demo',\n};\n",
            )

    def test_main_check_mode_does_not_write_and_reports_status(self):
        captured = io.StringIO()

        with mock.patch("sys.stdout", new=captured):
            result = sync_configs.main(["--check"])

        output = captured.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("Check mode: no files written.", output)
        self.assertTrue("No warnings." in output or "Warnings:" in output)


class ExportRuntimeTests(unittest.TestCase):
    def test_extract_fonts_from_preset_detects_imports_font_face_and_existing_family_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            preset = tmp_path / "demo.css"
            preset.write_text(
                '\n'.join(
                    [
                        '@import "../fonts/inter.css";',
                        "@font-face {",
                        "  src: url(../fonts/nunito/nunito-400-normal.ttf);",
                        "}",
                        ":root {",
                        "  --bs-body-font-family: 'Work Sans', sans-serif;",
                        "}",
                    ]
                ),
                encoding="utf-8",
            )

            font_dir = export_runtime.BTDT_DIR / "fonts" / "work-sans"
            self.assertTrue(font_dir.exists(), "Expected repo font directory work-sans to exist")

            fonts = export_runtime.extract_fonts_from_preset(preset)

            self.assertEqual(fonts, {"inter", "nunito", "work-sans"})

    def test_validate_source_files_reports_missing_requested_preset(self):
        files = [
            export_runtime.BTDT_DIR / "css" / "bootstrap.min.css",
            export_runtime.BTDT_DIR / "themes" / "preset" / "default.min.css",
        ]

        errors = export_runtime.validate_source_files(files, ["default", "missing-theme"])

        self.assertIn(
            "Requested preset 'missing-theme' was not found in btdt/themes/preset/",
            errors,
        )

    def test_copy_files_creates_export_tree_and_copies_readme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            destination = Path(tmpdir)
            files = [
                export_runtime.BTDT_DIR / "css" / "bootstrap.min.css",
                export_runtime.BTDT_DIR / "js" / "btdt.min.js",
            ]

            with mock.patch("sys.stdout", new=io.StringIO()):
                copied_count = export_runtime.copy_files(destination, files, dry_run=False)

            self.assertEqual(copied_count, 3)
            self.assertTrue((destination / "btdt/css/bootstrap.min.css").is_file())
            self.assertTrue((destination / "btdt/js/btdt.min.js").is_file())
            self.assertTrue((destination / "btdt/README.md").is_file())

    def test_main_returns_zero_for_dry_run_with_selected_presets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            argv = [
                "export-runtime.py",
                tmpdir,
                "--presets",
                "default",
                "--dry-run",
            ]

            with mock.patch.object(sys, "argv", argv):
                with mock.patch("sys.stdout", new=io.StringIO()):
                    result = export_runtime.main()

            self.assertEqual(result, 0)
            self.assertFalse((Path(tmpdir) / "btdt").exists())


if __name__ == "__main__":
    unittest.main()
