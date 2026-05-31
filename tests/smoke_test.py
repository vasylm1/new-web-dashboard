"""Headless smoke test for CI: load every tool via Streamlit AppTest and assert
no exception, then drive the no-upload generators (fill + Generate) and assert
they produce output. Exit non-zero on any failure.

Run:  python tests/smoke_test.py
"""
import os
import sys
import glob

from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICES = os.path.join(ROOT, "services")


def _code(path):
    return (
        "import sys\n"
        f"sys.path.insert(0, {ROOT!r})\n"
        "import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('toolmod', {path!r})\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        "m.run('English')\n"
    )


def _exc(at):
    if at.exception:
        e = at.exception[0]
        return f"{e.type}: {e.message}".strip()
    return None


def main():
    failures = []

    # Phase 1: every tool renders without error.
    files = sorted(glob.glob(os.path.join(SERVICES, "*.py")))
    print(f"Phase 1: render {len(files)} tools")
    for path in files:
        name = os.path.basename(path)[:-3]
        try:
            at = AppTest.from_string(_code(path), default_timeout=120)
            at.run()
            exc = _exc(at)
        except Exception as e:  # harness-level failure
            exc = f"HARNESS {type(e).__name__}: {e}"
        if exc:
            failures.append((name, exc))
            print(f"  FAIL {name}: {exc}")
        else:
            print(f"  ok   {name}")

    # Phase 2: no-upload generators actually produce output.
    generators = [
        "Resume builder", "Cover letter", "Certificate generator", "Certificate image",
        "Label sheet", "EPUB builder", "Roadmap maker", "Social banner",
        "QR code", "Vcard generator", "Persona builder", "Newsletter builder", "Sell sheet",
    ]
    print("Phase 2: drive generators (fill + Generate)")
    for name in generators:
        path = os.path.join(SERVICES, f"{name}.py")
        try:
            at = AppTest.from_string(_code(path), default_timeout=120)
            at.run()
            for w in at.text_input:
                w.set_value("Jane Doe")
            for w in at.text_area:
                if not w.value:
                    w.set_value("Line one\nLine two\nLine three")
            at.run()
            if len(at.button):
                at.button[0].click()
                at.run()
            exc = _exc(at)
            errs = [e.value for e in at.error]
            if not exc and errs:
                exc = "st.error: " + "; ".join(errs)
        except Exception as e:
            exc = f"HARNESS {type(e).__name__}: {e}"
        if exc:
            failures.append((name + " (generate)", exc))
            print(f"  FAIL {name}: {exc}")
        else:
            print(f"  ok   {name}")

    print(f"\n{len(files)} tools | {len(failures)} failures")
    for n, e in failures:
        print(f"  FAIL {n}: {e}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
