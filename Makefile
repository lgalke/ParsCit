CRFPP_DIR=crfpp

all: build_crfpp
	echo "ParsCit ready."

build_crfpp:
	echo "Compile crfpp source".
	git submodule update --init
	sed -i '/#include "winmain.h"/d' $(CRFPP_DIR)/crf_test.cpp
	sed -i '/#include "winmain.h"/d' $(CRFPP_DIR)/crf_learn.cpp
	cd $(CRFPP_DIR) && ./configure && make && make install
