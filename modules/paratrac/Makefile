python_version = $(shell python --version 2>&1 | sed 's/Python \?//' | sed 's/\.[0-9]+\?$$//')
INC_DIR=.
ifeq ($(shell test -f /usr/include/python$(python_version)/Python.h && echo 1), 1)
	#INC_DIR += /usr/include/python$(python_version)
endif

ifeq ($(INC_DIR),.)
	pythonheaders = $(wildcard /usr/include/python*/Python.h)
	pythondirs = $(dir $(pythonheaders))
	INC_DIR += $(pythondirs)
endif

CFLAGS += $(foreach dir,$(INC_DIR), -I$(dir))

#$(warning Trying Python version with $(python_version))
#$(warning Currenty CFLAGS is $(CFLAGS))

CFLAGS += -fPIC -Wall
LDFLAGS += -Wall

all : paratracmodule.so


paratracmodule.so : paratracmodule.o paratrac_part.o
	$(CC) -shared -o $@ $^

paratrac_part.o : paratrac_part.c paratrac_part.h

paratracmodule.o : paratracmodule.c paratrac_part.h

.PHONY : clean

clean :
	-$(RM) *.o *.so *~

