.PHONY: run test

run:
	python3 -m src

test:
	python3 -m unittest discover -s tests -t .
