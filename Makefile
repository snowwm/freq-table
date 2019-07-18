ver = $(shell python setup.py -V)
user = snowwm

format:
	isort -rc .
	autopep8 -r . -i

check:
	isort -rc . --diff
	autopep8 -r . --diff

publish: build tag upload

upload:
	twine upload dist/* -u $(user)

tag:
	git tag "v$(ver)" -m "Version $(ver)"
	git push --tags

build: clean
	python setup.py --quiet sdist bdist_wheel

clean:
	rm -r build dist *.egg-info || true

.PHONY: format check publish
