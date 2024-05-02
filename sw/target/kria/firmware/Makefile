# Path to board specific firmwares to build.
BOARDS := boards/

default: all

all: build

build: $(BOARDS)
	make -C $(BOARDS)

clean:
	make -C $(BOARDS) clean

install:
	make -C $(BOARDS) install DESTDIR=$(DESTDIR)

.PHONY: default all build clean install
