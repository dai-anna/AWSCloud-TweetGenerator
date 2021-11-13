install:
	pip install --upgrade pip
	pip install -r requirements.txt
	git clone --depth=1 https://github.com/twintproject/twint.git
	cd twint
	pip3 install . -r requirements.txt
