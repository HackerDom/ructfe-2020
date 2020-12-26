## Vuln 1

### Explanation
First vulnerability is based on default random seed in golang. Every service uses same seed and generate absolutely same sequence of numbers. 
This sequence is used to generate access token for documents. Hence, you can sequentially make up all tokens, using name of document.

### How to fix
This gap can be easily be fixed by explicit setting different random seed in `hashutil.go`

### [Exploit](./spl2/main.go)


## Vuln 2

### Explanation
Second one is based on self made template language for making documents. There is no verification, if user making request about himself or not.
This weakness lets user insert information about any other user in his or her document. 

### Example
There is an example of stealing doc
```python
def create_doc(name):
    return f"""
vars:
  username: {name}
exprs:
  - name: bio
    expr: "get_info('bio')"
---
{{bio}}
'"""
```

### How to fix
FIX

### [Exploit](./main.py)
