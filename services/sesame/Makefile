sesame: sesame.* storage.* http.* *.html
	python3 embed_face.py > face.html.h
	gcc-7 sesame.c storage.c http.c -m64 -O2 -luuid -Wl,--strip-all -o sesame