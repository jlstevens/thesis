
all: thesis clean


thesis:
	/Library/TeX/texbin/pdflatex thesis.tex &> /dev/null
	/Library/TeX/texbin/bibtex thesis
	/Library/TeX/texbin/pdflatex thesis.tex &> /dev/null

clean:
	rm thesis.aux
	rm thesis.bbl
	rm thesis.blg
	rm thesis.log
	rm thesis.out
	rm thesis.toc

