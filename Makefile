install:
	@poetry install

build: clear
	@poetry build

publish: build
	@poetry publish --repository testpypi

run:
	@poetry run page-loader

clear:
	if [ -d "dist" ]; then rm -r dist; fi

lint:
	@poetry run flake8 page_loader

test:
	pytest

check: lint test

coverage:
	pytest --cov=page_loader/ tests/

coverage-xml:
	pytest --cov=page_loader/ tests/ --cov-report xml