PELICAN=pelican
PELICANOPTS=

GHP_IMPORT=ghp-import

BASEDIR=$(PWD)/site
INPUTDIR=$(BASEDIR)/source
OUTPUTDIR=$(BASEDIR)/output
CONFFILE=$(BASEDIR)/pelicanconf.py

help:
	@echo 'Makefile for a pelican Web site                                        '
	@echo '                                                                       '
	@echo 'Usage:                                                                 '
	@echo '   make html                        (re)generate the web site          '
	@echo '   make clean                       remove the generated files         '
	@echo '   make publish                     publish to gh-pages                '
	@echo '                                                                       '


html: clean $(OUTPUTDIR)/index.html
	@echo 'Done'

$(OUTPUTDIR)/%.html:
	$(PELICAN) $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

clean:
	if [ -d "$(OUTPUTDIR)" ]; then find $(OUTPUTDIR) -mindepth 1 -delete; fi

regenerate: clean
	$(PELICAN) -r $(INPUTDIR) -o $(OUTPUTDIR) -s $(CONFFILE) $(PELICANOPTS)

serve:
	cd $(OUTPUTDIR) && python -m SimpleHTTPServer

publish: html
	$(GHP_IMPORT) -p -m "Publish to gh-pages." $(OUTPUTDIR)

.PHONY: html help clean regenerate serve publish
