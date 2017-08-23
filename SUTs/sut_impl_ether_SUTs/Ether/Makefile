
CFLAGS  = -g3 -ggdb3 -Wall -std=gnu99
#CFLAGS += -Wvariadic-macros
INCLUDE = -I.

#LDPATH  =
#LDFLAGS = -lpthread

PATH := c:\opt\gcc-4.9-win64\bin:$(PATH)
export PATH

CC=gcc

all:	clean libuav_swarm_ether.a main

libuav_swarm_ether.a: uav_swarm_ether.o time1.o trace.o 
	ar cru $(@) $(^) 
	ranlib $(@)

main: main.o
	$(CC) $(CFLAGS) -L. -l:libuav_swarm_ether.a -o main main.c uav_swarm_ether.c time1.c trace.c 

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDE) -c -o $@ $<

clean:		
	rm -f *~ *.o *.a 
