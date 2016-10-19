
thesis:
	/Library/TeX/texbin/pdflatex thesis.tex &> /dev/null
	/Library/TeX/texbin/bibtex thesis
	/Library/TeX/texbin/pdflatex thesis.tex &> /dev/null
