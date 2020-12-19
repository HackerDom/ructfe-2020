baz: baz.c vm.c storage.c baz.vm compilevm.py index.*
	cat baz.vm | python3 compilevm.py > baz.vm.h
	python3 embed_face.py > face.html.h
	gcc-7 baz.c vm.c storage.c -m64 -O2 -o baz