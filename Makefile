install:
	pip install .

test:
	tox 

publish:
	sudo python setup.py sdist && twine upload dist/*

clean:
	rm -rf build dist *.egg-info .tox
