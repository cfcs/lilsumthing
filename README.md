# lilsumthing

This repo contains a little experiment with the Python [`ast` module](https://docs.python.org/3/library/ast.html).

I wanted to play with AST rewriting, and based on my previous [notes about Gauss summations](https://github.com/cfcs/misc/blob/master/gauss-sum.md) I thought it would be fun to try to write something that could rewrite simple for-loops that calculated sums, replacing them with their closed-form represenation.

It presently handles multiplications and additions, subtractions, and simple exponentiations (`n^0` through `n^11`), with constant folding, and it tries to refrain from suggesting incorrect patches, but it is probably not foolproof. If you manage to fool it, please open an issue and we'll add a test. :-) In general, any and all suggestions and patches are welcome here.

Modulo/division, and other arithmetic operations would be nice to add.

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

def sum1_gen(n):
    return sum((i * 123 * n for i in range(100)))
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
 
 def sum1_gen(n):
-    return sum((i * 123 * n for i in range(100)))
+    return n * 608850
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

### Example 6

Besides exercising the hardcoded limit of `i**11`, this example demonstrates that I should really fold `n * n * ...` into `n**7` :-)
```diff
 def sum6(n):
     S = 0
-    for i in range(10000000):
-        S += (2 + i * n) ** 9 * (n - i + 3) ** 2
+    S = n * n * 92159907840027647998156799995904000000 + n * n * n * 895999086080281599978879999667200045312000000 + n * n * n * n * 5759993952001921919852159993248000777600000128000000 + n * n * n * n * n * 25199972640008903999375039928600007392000067199989056000000 + n * n * n * n * n * n * 74666582666694186665322666211946708666667823999865599998912000000 + n * n * n * n * n * n * n * 143999832000053400000239998191200141120009259999135999980640001248000000 + n * n * n * n * n * n * n * n * 163636165636418636372636359256363879963677643633303636214636372456363852000000 + n * n * n * n * n * n * n * n * n * 83333228787890954565954539692045514545559278782238787310037905787880434545414000000 + n * n * n * n * n * n * n * n * n * n * -18181802181820848485298484708484852684849524848454848479848484938484856000000 + n * n * n * n * n * n * n * n * n * n * n * 999999500000074999999999999300000000000004999999999999985000000000000 + n * 5759994240001734399909120000000 + 170666487466728960000000
     return S
```

## Math

### Sums of `c` for constant `c`

For constants `c`, that do not depend on the loop variable, it suffices to multiply by the length/cardinality of the range we are iterating over.

<details>

Example:
```python
S = 0
for i in range(4)
  S += 5
```
Here we are adding 5 for each element `i` in`[0,1,2,3]`. We can rewrite that as:
```python
S = 0
S += len(range(4)) * 5 # == len([0,1,2,3]) * 5 # = 4 * 5 = 20
```

</details>

### Sums of `i` for loopvar `i`

Wikipedia has a [neat article about Triangular numbers](https://en.wikipedia.org/wiki/Triangular_number#Formula).

The TL;DR version is that it suffices that for `range(n)` we can substitute `(n-1)*n//2`.
The `//2` division doesn't truncate because either `n` or `n-1` will be an even number (*"congruent to 0 mod 2"*), ie a multiple of two, so we can safely divide by two.

### Sums of `i^c` for constant `c`, loopvar `i`

`i^0` is replaced with `1`.

`i^1` uses the *Triangular number* formula described in the section above.

<details>

For higher values of `c`, most solutions involve computing either [Bernoulli numbers](https://en.wikipedia.org/wiki/Bernoulli_number) or [Stirling partition numbers](https://en.wikipedia.org/wiki/Stirling_numbers_of_the_second_kind), to be plotted into [Faulhaber's formula](https://en.wikipedia.org/wiki/Faulhaber%27s_formula).

This gets pretty complicated, and slow, so for now, we hardcode the formulas for lower values of `c`, and fail to do anything sensible about e.g. `i^100`.

1. https://github.com/Spooghetti420/Faulhaber/blob/main/calculator.py
2. https://gist.github.com/goulu/5bbf24a3e2e25070904b79f49020448f
3. https://stackoverflow.com/questions/22726715/efficient-implementation-fo-faulhabers-formula
4. also of interest, this impl using Stirling numbers instead of Bernoulli numbers: https://rosettacode.org/wiki/Faulhaber%27s_formula#Python
- see David Harvey's algorithm (according to wikipedia used in SageMath): https://arxiv.org/pdf/0807.1347.pdf
5. and lastly this sounds promising https://arxiv.org/abs/1103.1585 but it reads pretty dense
6. https://mathpages.com/home/kmath279/kmath279.htm here are some simple examples too

</details>

### Sums of `c^i` for constant `c`, loopvar `i`

This one is sadly not implemented yet, but it would make a great addition.

[sum of terms in geometric series with common factor `c`:](https://en.wikipedia.org/wiki/Geometric_series#Sum)
<details>

```python
>>> c = 10
>>> n = 4
>>> sum([c**i for i in range(1,n+1)])
11110
# n
# ⅀ c**k  <=> ((c**i)-c**(n+1)) / (1-c)
# k=i
>>> (c**1 - c**(n+1))//(1-c)
11110
```

</details>

Source: https://mathworld.wolfram.com/PowerSum.html
<details>

```
n
⅀ k * c**k = (c-(n+1)* c**(n+1) + n * c**(n+2)) // (c-1)**2
k=0
```

</details>
