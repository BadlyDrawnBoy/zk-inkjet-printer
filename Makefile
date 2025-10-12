.PHONY: test lint-docaddrs export gh

test:
	python3 -m pytest -q

lint-docaddrs:
	python3 scripts/doc_addr_lint.py

export:
	tools/make_export.sh --with-binaries

gh:
	scripts/gh.sh
