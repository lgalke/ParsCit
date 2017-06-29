CRFPP_SOURCE=crfpp

all: crfpp

crfpp:
	git submodule update --init
	sed -i '/#include "winmain.h"/d' $(CRFPP_SOURCE)/crf_test.cpp
	sed -i '/#include "winmain.h"/d' $(CRFPP_SOURCE)/crf_learn.cpp
	cd $(CRFPP_SOURCE) && make

