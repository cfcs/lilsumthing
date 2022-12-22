import lilsumthing
import ast

def test_linear0():
    '''independent of i, only depending on the length of the sequence:'''
    o = lilsumthing.optimize('''
S = 0
for i in range(2,10):
  S += 5
''')
    assert ast.unparse(o) == 'S = 0\nS = 40'

def test_xx():
    #o = lilsumthing.optimize('''
#S = 0 + 8 * 2
#''')
    #print(ast.dump(o, indent=2))
    #print()
    #for l in o.body:
    #    print(ast.unparse([l]))
    pass


def test_linear2():
    '''4205'''
    o = lilsumthing.optimize('''
S = 5
for i in range(400,1000):
  S += 7
''')
    assert ast.unparse(o) in [
        'S = 5 + 600 * 7',
        'S = 5\nS = 4205'
        ]

def test_linear3():
    '''4805'''
    o = lilsumthing.optimize('''
S = 5
for i in range(400,1000):
  S += 7 + 1
''')
    unparsed = ast.unparse(o)
    assert unparsed in [
        'S = 5\nS = 4805',
        'S = 5 + 600 * (7 + 1)',
        'S = 5 + (600 * 7 + 600 * 1)',
        'S = 5 + (600 * 7 + 600)',
        ]

def test_linear4():
    '''12605'''
    o = lilsumthing.optimize('''
S = 5
for i in range(400,1000):
  S += 7 + 1 + (4 + (1 + 8))
''')
    unparsed = ast.unparse(o)
    assert ast.unparse(o) in [
        'S = 5\nS = 12605',
        'S = 5 + 600 * (7 + 1 + (4 + (1 + 8)))',
        'S = 5 + 600 * (7 + 1) + 600 * (4 + (1 + 8))',
        'S = 5 + (600 * (7 + 1) + 600 * (4 + (1 + 8)))',
        'S = 5 + (600 * 7 + 600 * 1 + (600 * 4 + (600 * 1 + 600 * 8)))',
        'S = 5 + (1 * (600 * 7 + 600 * 1) + 1 * (600 * 4 + 1 * (600 * 1 + 600 * 8)))',
        'S = 5 + (600 * 7 + 600 + (600 * 4 + (600 + 600 * 8)))',
        ], unparsed

def test_linear5():
    o = lilsumthing.optimize('''
S = 5
for i in range(400,1000):
  S += 10*20
''')
    unparsed = ast.unparse(o)
    assert ast.unparse(o) in [
        'S = 5\nS = 120005',
        'S = 5 + 600 * (10 * 20)',
        'S = 5 + 600 * 10 * 20',
        ], unparsed

def test_gauss0():
    o0_10 = lilsumthing.optimize('''
S = 5
for i in range(0,10):
  S += i
''')
    unparsed = ast.unparse(o0_10)
    assert ast.unparse(o0_10) == 'S = 5\nS = 50', unparsed
    o1_10 = lilsumthing.optimize('''
S = 5
for i in range(1,10):
  S += i
''')
    assert ast.unparse(o0_10) == ast.unparse(o1_10), \
        'sum of 0,1,2..9 == sum of 1,2..9 because 0+1 == 1'

def test_gauss1():
    '''51'''
    o = lilsumthing.optimize('''
S = 6
for i in range(0,10):
  S += i
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert ast.unparse(o) in [
        'S = 6 + 45',
        'S = 6\nS = 51'
    ], unparsed

def test_gauss2():
    '''
    6 + sum((i+4 for i in range(0,10)))
    91
    '''
    o = lilsumthing.optimize('''
S = 6
for i in range(0,10):
  S += i + 4
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert ast.unparse(o) in [
        'S = 6 + (45 + 10 * 4)',
        'S = 6\nS = 91',
    ], \
        (unparsed, 'S = 6 + (45 + 10 * 4)')

def test_gauss20():
    '''
    0 + sum(( 3 + (2+i) + 4 for i in range(0,10)))
    135
    '''
    o = lilsumthing.optimize('''
S = 0
for i in range(0,10):
  S += 3 + (2+i) + 4
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert ast.unparse(o) in [
        'S = 0 + (10 * 3 + (10 * 2 + 45) + 10 * 4)',
        'S = 0\nS = 135',
    ], unparsed

def test_gauss21():
    '''
    0 + sum(( 3 + (2+i+5) + 4 for i in range(0,10)))
    185
    '''
    o = lilsumthing.optimize('''
S = 0
for i in range(0,10):
  S += 3 + (2+i+5) + 4
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert ast.unparse(o) in [
        'S = 0 + (10 * 3 + (10 * 2 + 45 + 10 * 5) + 10 * 4)',
        'S = 0\nS = 185',
        ], unparsed


def test_gauss14():
    '''
    7+sum((i*2 + 4 for i in range(1,5)))
    == 43
    '''
    o = lilsumthing.optimize('''
S = 7
for i in range(1,5):
  S += i*2 + 4
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert ast.unparse(o) in [
        'S = 7\nS = 43',
        'S = 7 + (10 * 2 + 4 * 4)',
        'S = 7 + 10 * (1 * 2) + 4 * 4',
        'S = 7 + (10 * (1 * 2) + 4 * 4)',
        'S = 7 + (1 * 10 * 2 + 4 * 4)',
        'S = 7 + (1 * (10 * (1 * 2)) + 4 * 4)',
        ], unparsed

def test_gauss3():
    '''
    >>> sum(((i+1)*2+4 for i in range(0,1000)))
    1005000
    1005000 + 7 = 1005007
    '''
    o = lilsumthing.optimize('''
S = 7
for i in range(0,1000):
  S += (i+1)*2 + 4
''')
    unparsed = ast.unparse(o)
    #print(ast.dump(o, indent=2))
    # 7 + (499500*2 + 2*1000) + 1000*4
    # 7 + (999000 + 2000) + 4000
    # 7 + 1001000 + 4000
    # 7 + 1005000
    # 1005007
    print('UNP', unparsed)
    assert unparsed in [
        'S = 7\nS = 1005007',
        'S = 7 + ((499500 + 1000 * 1) * 2 + 1000 * 4)',
        'S = 7 + (500500 * 2 + 1000 * 4)',
        'S = 7 + ((499500 * 1 + 1000 * 1) * 2 + 1000 * 4)',
        'S = 7 + (1 * (1 * ((499500 * 1 + 1000 * 1) * 2)) + 1000 * 4)',
        'S = 7 + ((499500 + 1000) * 2 + 1000 * 4)',
        ], unparsed.replace('\n', ';')

def test_gauss4():
    '''1005008'''
    o = lilsumthing.optimize('''
S = 8
for i in range(0,1000):
  S += 4 + 2*(1+i)
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert unparsed in [
        'S = 8\nS = 1005008',
        'S = 8 + (1000 * 4 + (2 * (1000 * 1 + 499500 * 1)))',
        'S = 8 + (1000 * 4 + 2 * (1000 + 499500))',
    ], unparsed

def test_gauss5():
    '''
    91
    '''
    o = lilsumthing.optimize('''
S = 6
for i in range(0,10):
  S += 4 + i
''')
    unparsed = ast.unparse(o)
    #print(ast.dump(o, indent=2))
    print('UNP', unparsed)
    assert ast.unparse(o) in [
        'S = 6\nS = 91',
        'S = 6 + (10 * 4 + 45)',
        ], unparsed

def test_gauss6():
    '''
    100*99/2 * 123 * n = 608850 * n
    '''
    o = lilsumthing.optimize('''
S = 0
for i in range(100):
  S += i * 123 * n
''')
    assert ast.unparse(o) in [
        'S = 0\nS = n * 608850',
        'S = 608850 * n',
        'S = 4950 * 123 * n',
        'S = 0 + 4950 * 123 * n',
        'S = 0 + 1 * 4950 * 123 * n',
    ]

def test_gauss7():
    '''
    we should abort on this for now, because it references the running sum S,
    which is not something we currently support.
    '''
    orig_src ='''
S = 0
for i in range(100):
  S += S * i * 123 * n
'''
    o = lilsumthing.optimize(orig_src)
    assert ast.unparse(o) == ast.unparse(ast.parse(orig_src))

def test_archimedes1():
    '''
    https://proofwiki.org/wiki/Sum_of_Sequence_of_Squares , yo:Archimedes
    we can also solve this recursively:
    https://proofwiki.org/wiki/Sum_of_Sequence_of_Squares/Proof_by_Summation_of_Summations
    # top*(top+1)*(2*(rlen+1)-1)//6 == 285
    # (9*(9+1)*(2*(spanlen+1)-1))//6 == 285
    '''
    o = lilsumthing.optimize('''
S = 0
for i in range(1,10):
  S += i*i
''')
    # (9*(9+1)*(2*(9+1)-1))//6 == 285
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert unparsed in [
        'S = 0\nS = 285',
        'S = 285',
        'S = 0 + 285',
    ], unparsed
    o0_10 = lilsumthing.optimize('''
S = 0
for i in range(0,10):
  S += i*i
''')
    assert unparsed == ast.unparse(o0_10), \
        'this should be the same, again because sum of 0,1 is 1'

def test_archimedes2():
    # >>> sum((i**3 for i in range(1,10)))
    # 2025
    o = lilsumthing.optimize('''
S = 0
for i in range(1,10):
  S += i*i*i
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert unparsed in [
        'S = 0 + 2025',
        'S = 0\nS = 2025',
        'S = 2025',
    ], unparsed

def test_cube2():
    # >>> sum((i*(i+7)*i for i in range(1,10)))
    # 4020
    o = lilsumthing.optimize('''
S = 0
for i in range(1,10):
  S += i*(i+7)*i
''')
    unparsed = ast.unparse(o)
    print(ast.dump(o, indent=2))
    assert unparsed in [
        'S = 4020',
        'S = 0\nS = 4020',
        'S = 4020',
        'S = 0 + 4020',
        'S = 0 + 2025 + 285*7' # expanded from (i**3 + i*i*7)
        ], unparsed

def test_factors():
    pw = lilsumthing.ProductWalker()
    tree = ast.parse(
'''
S = 0
for i in range(1,50000000):
  S += i*(3+i*n+4)*i + (3+n*3*i)*5 + i*(2+n+i)*5
# 151 * 4 = 604
''')
    pw.visit(tree)
    unparsed = ast.unparse(tree)
    assert unparsed in [
        'S = 0\nS = 499999997500000599999985 + n * 1562499937500025624999500000000',
        'S = 499999997500000599999985 + n * 1562499937500025624999500000000',
        ], unparsed.replace('\n', ';')

def test_minus0():
    orig_src='''
S = 0
for i in range(10):
  S += i + 1 - 1
'''
    o = lilsumthing.optimize(orig_src)
    unparsed = ast.unparse(o)
    assert unparsed == ast.unparse(ast.parse(orig_src))

def test_range_equiv():
    '''∀x, x>=0: range_from(x) == range_from_to(0, x)'''
    pass
