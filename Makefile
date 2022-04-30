.PHONY: clean
clean:
	rm --force --recursive __pycache__

.PHONY: process
process:
	python3 main.py ~/web/*.pdf

