.PHONY: clean
clean:
	rm --force --recursive __pycache__
	rm --force --recursive .venv

.venv:
	python3 -m venv .venv
	bash -c "source .venv/bin/activate && python3 -m pip install pdfminer.six"

.PHONY: run
run: .venv
	bash -c "source .venv/bin/activate && python3 main.py data/*.pdf"

