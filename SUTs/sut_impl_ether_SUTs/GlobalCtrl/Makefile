
CFLAGS  = -g3 -ggdb3 -Wall -std=gnu99
#CFLAGS += -Wvariadic-macros
INCLUDE = -I.

#LDPATH  =
#LDFLAGS = -lpthread

PATH := c:\opt\gcc-4.9-win64\bin:$(PATH)
export PATH

CC=gcc

all:	clean libuav_swarm_globalctrl.a

libuav_swarm_globalctrl.a: uav_swarm_globalctrl.o time1.o trace.o 
	ar cru $(@) $(^) 
	ranlib $(@)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDE) -c -o $@ $<

clean:		
	rm -f *~ *.o *.a 
