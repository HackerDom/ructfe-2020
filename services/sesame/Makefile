baz: baz_0.s baz.c num.c vm.c storage.c baz.vm compilevm.py index.*
	cat baz.vm | python3 compilevm.py > baz.vm.h
	python3 embed_face.py > face.html.h
	gcc-7 baz_0.s baz.c num.c vm.c storage.c -nostdlib -fno-builtin -m64 -mno-sse -O2 -o baz