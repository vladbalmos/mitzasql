.PHONY: build

build:
	rm -f dist/* || true
	python3 setup.py sdist bdist_wheel

publish-test-package: build
	twine upload --repository testpypi dist/*

publish: build
	twine upload dist/*

install-test-package:
	pip3 install --upgrade --user --index-url https://test.pypi.org/simple \
		--extra-index-url https://pypi.python.org/simple mitzasql[clipboard]

install-website-deps:
	cd docs && bundle

start-website:
	cd docs && bundle exec jekyll serve

clean:
	rm -f dist/* || true
	docker-compose down --remove-orphans
	docker-compose -f docker-compose-tests.yml down --remove-orphans
