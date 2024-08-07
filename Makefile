# Makefile for cleaning Python cache files

.PHONY: pylint
pylint:
	PIPENV_IGNORE_VIRTUALENVS=1 \
	pipenv run pylint --rcfile=pylintrc .
	pipenv run black . 
	pipenv run isort --overwrite-in-place .

.PHONY: flake8
flake8:
	PIPENV_IGNORE_VIRTUALENVS=1 \
	@find . -type d -name '${VENV_DIR}' \
	-prune -o -type d -name '.git' \
	-prune -o -name '*.py' \
	-print -exec flake8 --jobs=0 {} +

.PHONY: lint
lint: pylint flake8


.PHONY: test-unit
test-unit:
	export PYTHONPATH=$(PWD) && \
	pipenv run pytest -v --cov=dags --cov-report=term-missing tests/unit 

.PHONY: clean
clean:
	rm -rf cov-report
	rm -rf .pytest_cache
	rm -rf tests/.pytest_cache
	rm -rf .coverage*
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf