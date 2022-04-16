install:
	pip install .

test:
	tox 

publish:
	sudo python setup.py sdist && twine upload dist/*