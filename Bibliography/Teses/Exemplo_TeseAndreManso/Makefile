# ---------------------------------------------------------
# type "make" command in Unix to create the PDF file 
# ---------------------------------------------------------

# Main filename
FILE=Thesis

# ---------------------------------------------------------

all:
	pdflatex  ${FILE}
	makeindex $(FILE).nlo -s nomencl.ist -o $(FILE).nls
	makeindex $(FILE).glo -s $(FILE).ist -o $(FILE).gls -t $(FILE).glg
	bibtex ${FILE}
	pdflatex  ${FILE}
	pdflatex  ${FILE}

clean:
	(rm -rf *.aux *.bbl *.blg *.glg *.glo *.gls *.ilg *.ist *.lof *.log *.lot *.nlo *.nls *.out *.toc)

veryclean:
	make clean
	rm -f *~ *.*%
	rm -f $(FILE).pdf $(FILE).ps

