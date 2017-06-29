CRFPP_SRC=crfpp-src
CRFPP_BIN=crfpp
# On windows, you need to append '.exe'
CRFPP_TEST=$(CRFPP_SRC)/crf_test
CRFPP_LEARN=$(CRFPP_SRC)/crf_learn

all: crfpp install clean
	echo "ParsCit ready."

crfpp:
	git submodule update --init
	sed -i '/#include "winmain.h"/d' $(CRFPP_SRC)/crf_test.cpp
	sed -i '/#include "winmain.h"/d' $(CRFPP_SRC)/crf_learn.cpp
	cd $(CRFPP_SRC) && ./configure && make


install: $(CRFPP_TEST) $(CRFPP_LEARN)
	mkdir -p crfpp
	cp -f $(CRFPP_TEST) $(CRFPP_BIN)/crf_test
	cp -f $(CRFPP_LEARN) $(CRFPP_BIN)/crf_learn


clean:
	cd $(CRFPP_SRC) && make clean && git reset --hard


