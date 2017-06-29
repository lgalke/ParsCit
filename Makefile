CRFPP_SRC=crfpp-src
CRFPP_BIN=crfpp

all: crfpp

crfpp:
	git submodule update --init
	sed -i '/#include "winmain.h"/d' $(CRFPP_SRC)/crf_test.cpp
	sed -i '/#include "winmain.h"/d' $(CRFPP_SRC)/crf_learn.cpp
	cd $(CRFPP_SRC) && ./configure && make
	mkdir -p crfpp
	cp $(CRFPP_SRC)/crf_test $(CRFPP_BIN)/
	cp $(CRFPP_SRC)/crf_learn $(CRFPP_BIN)/


