# lilsumthing

This repo contains a little experiment with the Python [`ast` module](https://docs.python.org/3/library/ast.html).

I wanted to play with AST rewriting, and based on my previous [notes about Gauss summations](https://github.com/cfcs/misc/blob/master/gauss-sum.md) I thought it would be fun to try to write something that could rewrite simple for-loops that calculated sums, replacing them with their closed-form represenation.

It presently handles multiplications and additions, subtractions, and simple exponentiations, with constant folding, and it tries to refrain from suggesting incorrect patches, but it is probably not foolproof. If you manage to fool it, please open an issue and we'll add a test. :-) In general, any and all suggestions and patches are welcome here.

Modulo/division, and other arithmetic operations would be nice to add.

It would also be great to extend the "opportunity to optimize here" matching to cover list comprehensions and generator expressions in addition to `for i in range(..):`.

## Examples

### Usage
```
usage: lilsumthing [-h] [-v] FILE [FILE ...]

Try to rewrite for-loop based summations to use closed-form expressions

positional arguments:
  FILE           python module files to examine

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose
```

### Example 1

```python
def sum1(n):
    # 608850 * n <=> 4950 * 123 * n
    x = 0
    for i in range(100):
        x += i * 123 * n
    return x
```
```bash
$ python3 lilsumthing.py example1.py
```
```diff
 def sum1(n):
     x = 0
-    for i in range(100):
-        x += i * 123 * n
+    x = n * 608850
     return x
```

The first example also highlights a glaring problem, namely that since we are using the `ast` module we are operating on an abstract syntax tree devoid of original comments, whitespace, etc, so we cannot produce a faithful, guaranteed-to-apply patch. Maybe in the future we could use [`libcst`](https://github.com/Instagram/LibCST) instead of the built-in `ast` module.

### Example 2

```python
def sum2(n):
    x = 0
    for i in range(100):
        x += i * i * n
    return x
```
```bash
$ python lilsumthing.py -v example2.py
# note -v for debug output:
```
```diff
     identified potential counter x
     ast.For loop: for i in range(100):
    x += i * i * n
           mult [i] [i]
           prod [[i; i]]
         mult [[i; i]] [n]
         prod [[n; i; i]]
       postprocess_augassign x += i * i * n
       [[n; i; i]]
       [[i; i; n; 1]]
       [[n; 1; 328350]]
       [[n; 328350]; [0]]
       [n * 328350; 0]
       x += i * i * n
       ==> x = n * 328350
     ENDFOR

 def sum2(n):
     x = 0
-    for i in range(100):
-        x += i * i * n
+    x = n * 328350
     return x
```

### Example 3
```python
def sum3(n):
    S = 0
    for i in range(1,50000000):
        S += i*(3+i*n+4)*i + (3+n*3*i)*5 + i*(2+n+i)*5
    return S
```
```bash
$ python3 lilsumthing.py example3.py
```
```diff
 def sum3(n):
     S = 0
-    for i in range(1, 50000000):
-        S += i * (3 + i * n + 4) * i + (3 + n * 3 * i) * 5 + i * (2 + n + i) * 5
+    S = 499999997500000599999985 + n * 1562499937500025624999500000000
     return S
```

### Example 4
```diff
 def sum4(n):
     S = 0
-    for i in range(1000000):
-        S += ((-i)**2) * -2 * -3 *(-i-2)
+    S = -1500000999995500002000000
     return S
```
### Example 5
```diff
 def sum5(n):
     S = 0
-    for i in range(1000):
-        S += n * (n*5 - 2 * i * n) ** 3 - n * (i * 7 * n - 10*n) ** 2
+    S = n * n * n * n * -1976106790000 + n * n * n * -16239011500
     return S
```
