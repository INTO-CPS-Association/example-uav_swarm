
CFLAGS  = -g3 -ggdb3 -Wall -std=gnu99
#CFLAGS += -Wvariadic-macros
INCLUDE = -I.

#LDPATH  =
#LDFLAGS = -lpthread

PATH := c:\opt\gcc-4.9-win64\bin:$(PATH)
export PATH

CC=gcc

TOPTARGETS := all clean

SUBDIRS := $(wildcard */.)

$(TOPTARGETS): $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS)

.PHONY: $(TOPTARGETS) $(SUBDIRS)
