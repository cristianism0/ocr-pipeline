IMAGE :=ocr-pipeline
TAG	  :=latest

DISPATCH ?=data/dispatch
INPUT ?=data/input
OUTPUT?=data/output

RECURSIVE ?=
ASCII ?=
EXTENSION ?=
PRECISION ?=
WORKERS ?=

ARGS :=
ifneq ($(RECURSIVE),)
	ARGS += -r
endif
ifneq ($(ASCII),)
	ARGS += -ascii
endif
ifneq ($(EXTENSION),)
	ARGS += --ext $(EXTENSION)
endif
ifneq ($(PRECISION),)
	ARGS += -p $(PRECISION)
endif
ifneq ($(WORKERS),)
	ARGS += -w $(WORKERS)
endif

.DEFAULT_GOAL := help

# input and output vars should be passed via CLI using INPUT, OUTPUT
.PHONY: help build build-api run run-api clean 

help:
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build:				## Build CLI Docker Image
	docker build --target cli  -t $(IMAGE):$(TAG) .

build-api:				## Build API Docker Image
	docker build --target api -t $(IMAGE):$(TAG) .

run:				## Run CLI Docker Image (use INPUT=, OUTPUT=, DISPATCH=, RECURSIVE=1, ASCII=1, EXTENSION=, PRECISION=, WORKERS=)
	docker run --rm \
	docker run --rm \
	         -v $(shell pwd)/$(INPUT):/app/data/input \
		     -v $(shell pwd)/$(OUTPUT):/app/data/output \
		     -v $(shell pwd)/$(DISPATCH):/app/data/dispatch \
			 $(IMAGE):$(TAG) -i /app/data/input $(ARGS)
run-api:				## Run API container on port 8000
	docker run --rm -p 8000:8000 $(IMAGE):$(TAG)

clean:				## Remove Docker Image
	-docker rmi $(IMAGE):$(TAG)
