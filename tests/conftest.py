import os

def pytest_ignore_collect(path, config):
    name = os.path.basename(str(path))
    if name in {"test_uiqvga_decoder.py", "test_uiqvga_hypersearch.py"}:
        # Nur einsammeln, wenn explizit gewünscht.
        return not os.getenv("RUN_UIQVGATests")
