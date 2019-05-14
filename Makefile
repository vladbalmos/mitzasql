install-website-deps:
	cd docs && bundle

start-website:
	cd docs && bundle exec jekyll serve
