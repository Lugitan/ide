black_exclude = --exclude='__metadata__.py|boilerplate|definition.py|layout.py'

black-check:
	black --check --diff ${black_exclude} --target-version=py38 .

black-reformat:
	black ${black_exclude} --target-version=py38 .

flake_exclude = --exclude=__metadata__.py,boilerplate
flake_ignore = --ignore=E203,E266,E501,W503
flake_options = --isolated --max-line-length=88

flake8:
	flake8 ${flake_exclude} ${flake_ignore} ${flake_options}

isort-check:
	isort \
	--case-sensitive \
	--check-only \
	--diff \
	--line-width=88 \
	--multi-line=3 \
	--project=abjad \
	--project=abjadext \
	--project=baca \
	--recursive \
	--thirdparty=ply \
	--thirdparty=roman \
	--thirdparty=uqbar \
	--trailing-comma \
	--use-parentheses \
	.

isort-reformat:
	isort \
	--apply \
	--case-sensitive \
	--check-only \
	--diff \
	--line-width=88 \
	--multi-line=3 \
	--project=abjad \
	--project=abjadext \
	--project=baca \
	--recursive \
	--thirdparty=ply \
	--thirdparty=roman \
	--thirdparty=uqbar \
	--trailing-comma \
	--use-parentheses \
	.

mypy:
	mypy .

project = ide

pytest:
	rm -Rf htmlcov
	pytest \
	--cov-config=.coveragerc \
	--cov-report=html \
	--cov=${project} \
	.

pytest-x:
	rm -Rf htmlcov
	pytest \
	-x \
	--cov-config=.coveragerc \
	--cov-report=html \
	--cov=${project} \
	.

reformat:
	make black-reformat
	make isort-reformat

check:
	make black-check
	make flake8
	make isort-check
	make mypy

test:
	make black-check
	make flake8
	make isort-check
	make mypy
	make pytest
