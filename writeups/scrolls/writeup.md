## Vuln 1

### Explanation
First vulnerability is based on default random seed in golang. Every service uses same seed and generate absolutely same sequence of numbers. 
This sequence is used to generate access token for documents. Hence, you can sequentially make up all tokens, using name of document.

### How to fix
This gap can be easily be fixed by explicit setting different random seed in `hashutil.go`

### [Exploit](../../sploits/scrolls/spl2/main.go)


## Vuln 2

### Explanation
Second one is based on self made template language for making documents. 
