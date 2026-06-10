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

# input and output vars should be passed via CLI using INPUT, OUTPUT
.PHONY: build run clean

build:
	docker build -t $(IMAGE) .
# OCR Pipeline [-h] [-i INPUT] [-o OUTPUT] [-r] [-ascii] [--ext EXT] [--dispatch DISPATCH] [-p PRECISION] [-w WORKERS]
run:
	docker run --rm \
	         -v $(shell pwd)/$(INPUT):/app/data/input \
		     -v $(shell pwd)/$(OUTPUT):/app/data/output \
		     -v $(shell pwd)/$(DISPATCH):/app/data/dispatch \
			 $(IMAGE):$(TAG) -i /app/data/input $(ARGS)

clean:
	-docker rmi $(IMAGE):$(TAG)
