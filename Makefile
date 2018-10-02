APP_NAME	?= subber
IMAGE_NAME	?= subber
IMAGE_TAG	?= local

all: build

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

check:
	tox

clean:
	rm -rf *.egg *.egg-info .tox
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

install:
	pip3 install -r requirements.txt
	pip install .

lint:
	tox -e pep8

run:
	docker run --name $(APP_NAME) \
		   --detach \
		   --publish 8000:8000 \
		   --volume $(shell PWD)/subber.cfg:/subber/subber.cfg \
		   $(IMAGE_NAME):$(IMAGE_TAG) .

stop:
	docker rm -f $(APP_NAME)

test:
	tox -e cover

.PHONY: all build check clean install lint run stop test
