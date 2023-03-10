import ast
import itertools
from functools import reduce

import argparse
import difflib

# the from_to(a,b+1) variants below exploit this equivalence:
# b    b    a-1
# ⅀ =  ⅀  - ⅀
# a   i=1   i=1

def gauss(n):
    '''
    # n
    # ⅀ i**1 <=> (n*(n+1))//2
    # i=1
    '''
    return (n*(n+1)) // 2
def range_to(n):
    return ((n-1)*n) // 2
def range_from_to(f, t):
    '''equivalent to sum(range(f,t)):
    the range(x,y) upper bound is exclusive), so u-1
    we subtract the sum of the range(0,f),
    where the upper bound is also exclusive, hence f-1:
res = sum(( i*y for i in range(x,z)))
==>
       z-1
 res ⟵  ⅀  i * y
       i=x
==>
 res = ( ((z-1)*(z-1+1)
         ) / 2
       ) * y
    '''
    return range_to(t) - range_to(f)
def square_to(t):
    '''see square_from_to.
    # n
    # ⅀ i**2 <=> (n*(n+1)*(2*n+1))//6
    # 1
    '''
    return ((t-1)*(t-1+1)*(2*(t-1)+1))//6
def square_from_to(f, t):
    '''
https://proofwiki.org/wiki/Sum_of_Sequence_of_Squares/Proof_by_Summation_of_Summations
res = sum(( i*i for i in range(x,z)))
==>
       z-1
 res ⟵  ⅀ i * i
       i=x
==>    z-1    z-1
 res ⟵  ⅀  (  ⅀ j )
       i=x    j=i
==>    z-1    z-1   i-1
 res ⟵  ⅀  (  ⅀ j - ⅀ j )
       i=x    j=1   j=1
==>    z-1
 res ⟵  ⅀  ((z-1)*z/2) - ((i-1)*(i)/2)
       i=x
==>    z-1
 res ⟵  ⅀  (( z*z - z)/2) - (( i*i - i)/2)
       i=x
==>    z-1
 res ⟵  ⅀  (( z*z - z)/2) - (( i*i - i)/2)
       i=x
==> and then a factor of 6 is applied to be able to erase the fraction (see link above)
==> ((z-1)*(z-1+1)*(2*(z-1)+1))//6 - ((x-1)*(x-1+1)*(2*(x-1)+1))//6
    '''
    return square_to(t) - square_to(f)
'''

gauss(z-1) * y
range_from_to(x,z) * y

>>> sum((i for i in range(10,30)))
390
>>> (((29)*(29+1))//2) - ((9)*(9+1))//2
390
>>> range_from_to(10,30)
390
>>> range_from_to(0, x) == gauss(x-1)
'''
def cube_to(t):
    return ((t-1)**2 * (t)**2) // 4
def cube_from_to(f,t):
    '''
    # n                                ( n  )   ( n  )
    # ⅀ i**3 <=> ((n*(n+1))//2)**2 <=> ( ⅀ i) * ( ⅀ i) <=> (n**2*(n+1)**2) / (2**2)
    # i=1                              (i=1 )   (i=1 )
    '''
    return cube_to(t) - cube_to(f)
def power_from_to_4(f,t):
    '''
    # i
    # ⅀ n**4 <=> (i*(i+1))*(2*i+1)*(3*i**2 + 3*i -1)//30
    # n=1
    '''
    return ((t*(t-1))*(2*(t-1)+1)*(3*(t-1)**2 + 3*(t-1) -1)//30
            - (f*(f-1))*(2*f)*(3*(f-1)**2 + 3*(f-1) -1)//30)
def power_from_to_5(f,t):
    '''
    # n
    # ⅀ i**5 <=> (n**2 * (n+1)**2 * (2*n**2 + 2*n -1)) // 12
    # 1
    # note that Faulhaber's formula gives a potentially nicer solution: (4*a**3-a**2)//3 where a is n*(n+1)//2
    '''
    t -= 1
    f = max(f-1, 0)
    return ((t**2 * (t+1)**2 * (2*t**2 + 2*t -1)) // 12
        - (f**2 * (f+1)**2 * (2*f**2 + 2*f -1)) // 12)
def power_from_to_6(f,t):
    '''
    # n          n
    # ⅀ i**6 <=> ⅀ i**5 + (n-1+1)**2 <=> (6*n**7 +21*n**6 + 21*n**5 -7*n**3 + n)//42
    # 1          1
    '''
    t -= 1
    f = max(f-1, 0)
    return (
        (6*t**7 +21*t**6 + 21*t**5 -7*t**3 + t)//42
        - (6*f**7 +21*f**6 + 21*f**5 -7*f**3 + f)//42
    )
def power_from_to_7(f,t):
    '''
    # n
    # ⅀ i**7 <=> (3*n**8 + 12*n**7 + 14*n**6 -7*n**4 +2*n**2)/24
    # 1
    '''
    t -= 1
    f = max(f-1, 0)
    return ((3*t**8 + 12*t**7 + 14*t**6 -7*t**4 +2*t**2)//24
            - (3*f**8 + 12*f**7 + 14*f**6 -7*f**4 +2*f**2)//24)
def power_from_to_8(f,t):
    '''
    # n
    # ⅀ i**8 <=> (10*n**9 + 45*n**8 + 60*n**7  -42*n**5 +20*n**3 -3*n)//90
    # 1
    '''
    t -= 1
    f = max(f-1, 0)
    return ((10*t**9 + 45*t**8 + 60*t**7  -42*t**5 +20*t**3 -3*t)//90
            - (10*f**9 + 45*f**8 + 60*f**7  -42*f**5 +20*f**3 -3*f)//90)
def power_from_to_9(f,t):
    '''
    # n
    # ⅀ i**9 <=> (2*n**10 + 10*n**9 +15*n**8 -14*n**6 +10*n**4 -3*n**2)//20
    # 1
    '''
    t -= 1
    f = max(f-1, 0)
    return ((2*t**10 + 10*t**9 +15*t**8 -14*t**6 +10*t**4 -3*t**2)//20
            - (2*f**10 + 10*f**9 +15*f**8 -14*f**6 +10*f**4 -3*f**2)//20)
def power_from_to_10(f,t):
    '''
    # n
    # ⅀ i**10 <=> (6*n**11 + 33*n**10 +55*n**9 - 66*n**7 +66*n**5 - 33*n**3 +5*n)//66
    # 1
    '''
    t -= 1
    f = max(f-1, 0)
    return ((6*t**11 + 33*t**10 +55*t**9 - 66*t**7 +66*t**5 - 33*t**3 +5*t)//66
            - (6*f**11 + 33*f**10 +55*f**9 - 66*f**7 +66*f**5 - 33*f**3 +5*f)//66)
def power_from_to_11(f,t):
    '''
    # Faulhaber polynomial solution for **11 where a=n*(n+1)//2
    # n
    # ⅀ i**11 <=> (16*a**6-32*a**5 + 34*a**4 -20*a**3 + 5*a**2) // 3
    # 1
    '''
    t -= 1
    f = max(f-1, 0)
    a_t = t*(t+1)//2
    a_f = f*(f+1)//2
    return ((16*a_t**6-32*a_t**5 + 34*a_t**4 -20*a_t**3 + 5*a_t**2) // 3
            - (16*a_f**6-32*a_f**5 + 34*a_f**4 -20*a_f**3 + 5*a_f**2) // 3)

def is_add(n):
    return type(n) == ast.BinOp and type(getattr(n,'op',None)) == ast.Add

def is_int(n):
    return type(n) == ast.Constant and type(n.value) is int

class StateMachine():
    def __init__(self, for_target, for_range, node_iter, replacement_target, accumulating_exprs=[], initial_value=ast.Constant(0)):
        self.initial_value = initial_value
        # the ast node to eventually be replaced (e.g ast.For or sum()):
        self.replacement_target = replacement_target
        # (i) in 'for i in range..':
        self.for_target : ast.Name = for_target
        # the range(..) in 'for i in range(..)'
        self.node_iter = node_iter
        # the dictionary with the parsed information:
        self.for_range = for_range
        # computed optimization to replace the ast.For loop with:
        self.for_replacement : ast.AST = None
        # abort optimizing this For loop:
        self.dont_optimize = False
        # these are the nodes that capture the results of the summation.
        # in a for-loop it could be the += (ast.AugAssign);
        # or ast.ListComp.elt; or ast.GeneratorExpr.elt
        self.accumulating_exprs = accumulating_exprs
        assert isinstance(self.accumulating_exprs, list) # TODO typecheck

def fold_constant_factors(lst):
    '''given a list like
    [[i; 15; 2]; [i; 40]; [i; 80]; 14; [15;2]; [x;5]; [z; 2]; [z;3];]
    we want to group by / partition the addends into partitions for each
    distinct set of identical non-constant factors:
        [i; 15; 2]; [i; 40]; [i; 80];
        [14]; [15;2];
        [x; 5];
        [z; 2]; [z; 3];
    and then we want to fold the constant factors, resulting in a
    single product for each such partition:
        [i; 15*2 + 30 + 40 + 80] == [i; 150]
        [14]; [15;2];       == [44]
        [x; 5]            == [x; 5]
        [z; 2+3]          == [z; 5]
    '''
    partitions = {}
    for product in lst: # maybe get rid of enumerate()
        constants , wo_constants = [], []
        if type(product) != list:
            product = [product]
        for x in product:
            if type(x) != ast.Constant: wo_constants.append(x)
            else: constants.append(x)
            # ordering doesn't matter, but [i;i] and [i] go in
            # separate partitions:
        wo_constants.sort(key=lambda x: x.id)
        name_hash = ','.join(x.id for x in wo_constants)
        # now we do constant folding for each shard, computing the
        # product of (constants) and storing the running sum:
        this_sum = 0
        if constants:
            this_sum = reduce(int.__mul__, (x.value for x in constants), 1)
        elif wo_constants:
            this_sum = 1
        # note that we have to be careful not to add a zero 'sum'
        # by accident. unless a constant above is 0,
        # this_sum will be nonzero because it's initialized with 1.
        # if there are no constants, it will be 1, so we retain the
        # property that [i]+[i] turns into [i;2] and not [i;0]:
        if this_sum:
            partitions[name_hash] = partitions.get(name_hash, {
                'sum': 0, # identity of addition
                'wo_constants': wo_constants
            })
            partitions[name_hash]['sum'] += this_sum
            if not partitions[name_hash]['sum']:
                # [[i, 1], [i, -1]] ("i*1+i*-1" = "i-i" = "0"):
                # these cancel out, so we remove them:
                del partitions[name_hash]
        # and finally we reconstruct the original format:
        ret = []
    for pdict in partitions.values():
        assert pdict['sum'] != 0, pdict
        if pdict['sum'] == 1 and pdict['wo_constants']:
            ret += [[*pdict['wo_constants']]]
        else:
            ret += [[*pdict['wo_constants'], ast.Constant(pdict['sum'])]]
    return ret

def pp(lstlst):
    '''pretty-prints ast nodes, and nested iterables of ast nodes'''
    if isinstance(lstlst, ast.AST):
        return ast.unparse(lstlst)
    if isinstance(lstlst, list) or isinstance(lstlst, tuple):
        if lstlst and isinstance(lstlst[0], ast.AST):
            return '[' + '; '.join((pp(y)
                for y in lstlst)) + ']'
        return '[' + '; '.join(
            pp(x) for x in lstlst
        ) + ']'
    return lstlst


class ProductWalker(ast.NodeTransformer):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.level = 0
        self.node_id = 0
        self.states = [] # stack of state machine states for ast.For loops
        # dict of (potential) accumulator variables. note that this does
        # not get cleaned up, and it doesn't care about scope. TODO:
        self.local_counters = {}
        self.allowed_name_refs = set() # allowed refs to the accumulator
        super().__init__()
    def pl(self, *a):
        '''print with indentation based on current nesting level in the tree'''
        if self.verbose:
            print('  '*self.level, end='')
            for arg in a:
                print('', pp(arg), end='')
            print('')

    def visit_Assign(self, node):
        '''BFS visit of ast.Assign nodes, where we try to identify the
        counter variables used in the for loops. Since we do not track
        the steps between Assign and For, we cannot safely replace *this* node,
        instead we should replace the ast.For node in order to handle cases
        like:
        S = 123              # ast.Assign (this node)
        b = S + 10
        for i in range(10):  # ast.For that we can rewrite
          S += b + i         # ast.AugAssign
        TODO unless we use self.node_id to ensure that's not the case;
        in that case we can eliminate the Assign node...
        but on a second pass over the AST?
        '''
        for target in node.targets:
            if type(target) == ast.Name and \
               is_int(node.value):
                # TODO should try to check that it's a numerical constant?
                # or at least complain if it is clearly not
                self.pl('identified potential counter', target.id)
                self.allowed_name_refs.add(target)
                self.local_counters[target.id] = {
                    'value': node.value
                }
        return node

    def postprocess_expr(self, node):
        '''
        computes the final optimized version of an expression.
        works on e.g. ast.AugAssign.value or ast.ListComp.elt
        '''
        adds = getattr(node, 'adds', [node])
        for lst in adds:
            for x in (type(lst) is list and lst or [lst]):
                if type(x) == ast.Constant: continue
                if type(x) == ast.Name: continue
                self.pl('postprocess: not rewriting because our adds is not Constant/Name:',
                        type(x), x, )
                self.states[-1].dont_optimize = True
                return None
        self.pl(adds)
        adds = fold_constant_factors(adds)
        self.pl(adds)
        # after constant folding, we are left with products containing
        # variable names and constants, or just a single constant.
        # There are two categories:
        # 1) product factors referring to constants and/or external variables
        # 2) addends whose product factors refer to the loop index
        # Each category 1 addend gets the length/span of the loop added as a factor.
        # Category 2 requires special handling. TODO.
        for i, product in enumerate(adds):
            # TODO I guess we should care about scope and not just check for
            # lexicographical equality here.
            powers_of_loop_var = len([x for x in product if type(x) == ast.Name and \
                                      x.id == self.states[-1].for_target.id
                                      ])
            if powers_of_loop_var == 0:
                adds[i].append(ast.Constant(self.states[-1].for_range["len"]))
            elif powers_of_loop_var > 0:
                adds[i] = list(filter(
                    lambda x: getattr(x,'id',None) != self.states[-1].for_target.id,
                    adds[i]))
                const = self.states[-1].for_range.get(powers_of_loop_var, None)
                if const:
                    adds[i] += [ast.Constant(const)]
                else:
                    # category 2 with loopvar^n with n >= 12, this should
                    # be handled in the future.
                    # in the meantime we should abort the postprocessing
                    # and set dont_optimize=True. TODO.
                    self.pl(f'powers of {powers_of_loop_var} not implemented, not optimizing')
                    self.states[-1].dont_optimize = True
                    return None
                pass # category 2
        self.pl(adds)
        #
        # Add the initial value of the counter: the 123 in
        # (S = 123, for ... S += ..):
        #
        if self.states[-1].initial_value:
            adds += [[self.states[-1].initial_value]]
        #
        # Final reduction step:
        #
        adds = fold_constant_factors(adds)
        self.pl(adds)
        #
        # At the end we need to transform our [addends[products]] list into
        # a nested AST node structure:
        def mk_add(a,b):
            # TODO if they are both 0 we should remove it entirely,
            # instead of returning a ast.Constant(0):
            if is_int(a) and a.value == 0: return b
            if is_int(b) and b.value == 0: return a
            return ast.BinOp(left=a, op=ast.Add(), right=b)
        def mk_mult(a,b):
            if is_int(a) and a.value == 0: return ast.Constant(0)
            if is_int(b) and b.value == 0: return ast.Constant(0)
            if is_int(a) and a.value == 1: return b
            elif is_int(b) and b.value == 1: return a
            return ast.BinOp(left=a, op=ast.Mult(), right=b)
        adds = list(map(lambda addend: reduce(mk_mult, addend[:], ast.Constant(1)) , adds))
        self.pl(adds)
        expr = reduce(mk_add, adds, ast.Constant(0))
        return expr

    def postprocess_listcomp(self, node):
        expr = self.postprocess_expr(node.elt)
        self.pl('got a comprehension', node.elt, '===>', expr)
        if not expr:
            return node
        ast.fix_missing_locations(expr)
        self.states[-1].for_replacement = expr
        return node

    def postprocess_augassign(self, node):
        self.pl('postprocess_augassign', node)
        expr = self.postprocess_expr(node.value)
        if not expr:
            # failed to optimize for some reason
            return Node
        self.states[-1].for_replacement = ast.Assign(
            targets=[node.target],
            value=[ expr ],
        )
        ast.fix_missing_locations(self.states[-1].for_replacement)
        self.pl(node)
        self.pl('==>', self.states[-1].for_replacement)
        return node

    def visit_Name(self, node):
        if node.id in self.local_counters:
            if node in self.allowed_name_refs:
                return node
            # this gets triggered when we add the for_replacement to the tree,
            # which is a problem if we want to do nested loops.
            if self.states:
                self.pl('not optimizing because', node.id,
                    'is an accumulator and that is not supported yet.')
                self.states[-1].dont_optimize = True
        return node

    def generic_visit(self, node):
        self.node_id += 1 # our unique ID for this node

        if self.states and node is self.states[-1].node_iter:
            # (relevant for list comprehensions where the range() is inside
            # the expression to be optimized)
            self.pl('skipping our own range', node)
            return node

        if type(node) == ast.For and not node.orelse:
            self.pl('ast.For loop:', ast.unparse(node))
            p_range = optimizable_range(node.iter)
            self.states.append(StateMachine(node.target, p_range,
                                            replacement_target=node,
                                            node_iter=node.iter))
            if not p_range:
                self.states[-1].dont_optimize = True
        elif type(node) == ast.Call and type(node.func) == ast.Name and 'sum'==node.func.id:
            self.pl('ast.Call: sum()')
            if not node.args:
                self.pl('sum() without arguments TODO')
                return node
            initial_value = ast.Constant(0)
            if (len(node.args) == 2 and [] == node.keywords):
                initial_value = node.args[1]
            elif len(node.args) == 1 and len(node.keywords) == 1 and 'start' == node.keywords[0].arg:
                initial_value = node.keywords[0]
            sum_args = node.args[0]
            if type(sum_args) in [ast.ListComp, ast.GeneratorExp]:
                # sum([ ... ]) or sum(( ... ))
                # [a for a in range(2) for b in range(3)] has:
                # len(.generators) == 2
                # [ (for a in range(2)),  (for b in range(3)) ]
                if len(sum_args.generators) != 1:
                    self.pl('TODO handle nested comprehensions')
                    if self.states: self.states[-1].dont_optimize = True
                    return node
                generator = sum_args.generators[0]
                if type(generator) == ast.comprehension:
                    # loop var: generator.target
                    p_range = optimizable_range(generator.iter)
                    loop_body = sum_args.elt
                    self.states.append(StateMachine(
                        generator.target, p_range,
                        node_iter=generator.iter,
                        replacement_target=node,
                        initial_value=initial_value,
                        accumulating_exprs=[loop_body]))
                    if not p_range:
                        self.states[-1].dont_optimize = True
                    self.pl('sum', 'loop var:', generator.target,
                            'range:', p_range,
                            'loop_body:', loop_body,
                            'initial_value:', initial_value)
        elif type(node) == ast.AugAssign:
            if self.states:
                # TODO this is a massive dirty hack; we should capture these
                # during BFS and set initial_value (PLURAL) depending on which
                # ones were referenced. For now, though, we overwrite:
                if self.states[-1].initial_value.value != 0:
                    self.pl("more than one AugAssign seen in this state. not implemented.")
                    self.states[-1].dont_optimize = True
                    return node
                self.states[-1].initial_value = self.local_counters[node.target.id]['value']
            self.allowed_name_refs.add(node.target)

        # TODO still_optimizing is a mess here.
        # we want to test for dont_optimize being set in one of the
        # descendants, but we also want it to be True if there are no
        # states.
        still_optimizing = True
        if still_optimizing and self.states:
            still_optimizing = not self.states[-1].dont_optimize
        if still_optimizing:
            self.level += 1
            node = super().generic_visit(node)
            self.level -= 1
            if self.states:
                still_optimizing = not self.states[-1].dont_optimize

        if self.states and node is self.states[-1].replacement_target:
            # this is where we need to modify (node) to replace the For loop
            if type(node) == ast.For and node.orelse:
                self.pl('what to do about for.orelse?')
                return node
            self.pl('ENDSUM')
            finalstate = self.states.pop()
            if finalstate.for_replacement and not finalstate.dont_optimize:
                ast.fix_missing_locations(finalstate.for_replacement)
                return finalstate.for_replacement
        elif still_optimizing:
            if type(node) == ast.UnaryOp:
                if type(node.op) == ast.USub:
                    # rewrite '-x' as '((-1) * x)', falling through to
                    # the visit_BinOp_dfs(node) below with the rewritten node:
                    self.pl('rewriting USub as BinOp.Mult:', node)
                    node = ast.BinOp(left=ast.Constant(-1),
                                     op=ast.Mult(),
                                     right=node.operand)
                else:
                    self.pl('not optimizing; unhandled UnaryOp:', node)
                    self.states[-1].dont_optimize = True
            if type(node) == ast.BinOp:
                self.pl('postvisit: visit_BinOp_dfs:',node)
                node = self.visit_BinOp_dfs(node)
            elif type(node) == ast.AugAssign and type(node.op) == ast.Add:
                # TODO we could handle repeated
                # S += abc...
                # S += def...
                # and do s_adds.extend(s2.adds) here. room for improvement :-)
                if node.target.id in self.local_counters:
                    node = self.postprocess_augassign(node)
            elif type(node) in [ast.ListComp, ast.GeneratorExp]:
                node = self.postprocess_listcomp(node)
        return node
    def visit_BinOp_dfs(self, node):
        if is_add(node):
            node.adds = []
            left  = getattr(node.left, 'adds', [node.left])
            right = getattr(node.right, 'adds', [node.right])
            node.adds.extend(left)
            node.adds.extend(right)
            node.adds = fold_constant_factors(node.adds)
            self.pl('Add.adds:', node.adds)
            return node
        elif type(node.op) == ast.Sub:
            node.adds = []
            left  = getattr(node.left, 'adds', [node.left])
            right = ([ast.Constant(-1)]+factors
                     for factors in getattr(node.right, 'adds', [[node.right]]))
            node.adds.extend(left)
            node.adds.extend(right)
            node.adds = fold_constant_factors(node.adds)
            self.pl('Sub.adds:', node.adds)
            return node
        elif type(node.op) == ast.Mult:
            left = getattr(node.left, 'adds', [node.left])
            right = getattr(node.right, 'adds', [node.right])
            self.pl('mult', left, right)
            prod = []
            # here we have the factors with nested lists:
            # [5; [3;2]]
            # and we want to flatten them, with the terrible code below:
            for p in itertools.product(right, left):
                prod.append([])
                for t in p:
                    if type(t) is list: prod[-1] += t
                    else: prod[-1] += [t]
            node.adds = fold_constant_factors(prod)
            self.pl('prod', node.adds)
        elif type(node.op) == ast.Pow and is_int(node.right):
            # rewrite [x**y] to [[*([x]*y)]] when y is a constant.
            self.pl("pow left.adds:", getattr(node.left, 'adds', node.left))
            prod = []
            for p in itertools.product(
                    *([getattr(
                        node.left,
                        'adds', [node.left])]*node.right.value)
            ):
                # TODO this ends up creating rather many duplicates.
                prod.append([])
                for t in p:
                    t = fold_constant_factors([t])
                    assert len(t) == 1
                    t = t[0]
                    if type(t) is list: prod[-1] += t
                    else: prod[-1] += [t]
            node.adds = fold_constant_factors(prod)
            if not node.adds:
                node.adds = [ast.Constant(1)] # ^0, identity of multiplication is 1
            self.pl("pow left:", node.left,
                    "right:", node.right, "node.adds:", node.adds)
        else:
            self.pl('better safe than sorry, not optimizing because', type(node.op), node)
            self.states[-1].dont_optimize = True
        return node

def optimizable_range(iterable):
    '''Looks for sequential ranges whose length
    we can compute, and/or their sum.
    Currently only handles constants. TODO.
    '''
    if type(iterable) == ast.Call:
        if type(iterable.func) == ast.Name:
            if iterable.func.id == 'range':
                if len(iterable.args) >= 1:
                    begin = 0
                    end = 0
                    length = 0
                    if is_int(iterable.args[0]):
                        if len(iterable.args) == 1:
                            end = iterable.args[0].value
                            length = iterable.args[0].value
                        else:
                            begin = iterable.args[0].value
                    else:
                        raise Exception("range(x) for non-constant x: "+str(ast.unparse(iterable)))
                    if len(iterable.args) == 2:
                        if is_int(iterable.args[1]):
                            end = iterable.args[1].value
                            length = iterable.args[1].value - iterable.args[0].value
                        else:
                            # TODO really ough to deal with this case
                            raise Exception("range(x,y) for non-constant y: "+str(ast.unparse(iterable)))
                    if len(iterable.args) > 2:
                        return {}
                    return {
                        'len': length,
                        1: range_from_to(begin, end),
                        2: square_from_to(begin, end),
                        3: cube_from_to(begin, end),
                        4: power_from_to_4(begin, end),
                        5: power_from_to_5(begin, end),
                        6: power_from_to_6(begin, end),
                        7: power_from_to_7(begin, end),
                        8: power_from_to_8(begin, end),
                        9: power_from_to_9(begin, end),
                        10: power_from_to_10(begin, end),
                        11: power_from_to_11(begin, end),
                    }
    return {}

### examples of patterns to match to identify relevant ast subtrees:
#
# S=0
# Assign(targets=[Name(id='S', ctx=Store())],
#        value=Constant(value=0))
#
# for i in range(mo):
# For( target=Name(i),
#      iter=Call(
#        func=Name(id='range', ctx=Load()),
#        args=[
#          Name(id='mo', ctx=Load())],
#        keywords=[]),

# for i in [0,1,2,3]:
#For(
#      target=Name(id='i', ctx=Store()),
#      iter=List(
#        elts=[
#          Constant(value=0),
#          Constant(value=1),
#          Constant(value=2),
#          Constant(value=3)],
#        ctx=Load()),

#for i in range(1,10,2):
#For(
#      target=Name(id='i', ctx=Store()),
#      iter=Call(
#        func=Name(id='range', ctx=Load()),
#        args=[
#          Constant(value=1),
#          Constant(value=10),
#          Constant(value=2)],
#        keywords=[]),



def optimize(code, filename='filename.py', verbose=True):
    # verbose defaults to True for tests
    tree = ast.parse(code, filename)
    pw = ProductWalker(verbose=verbose)
    pw.visit(tree)
    return tree

def optimize_file(filename, verbose):
    content = open(filename, 'r').read()
    original = ast.parse(content)
    optimized = optimize(content, filename=filename, verbose=verbose)
    original_str = ast.unparse(original)
    optimized_str = ast.unparse(optimized)
    if original_str != optimized_str:
        uni_diff = difflib.unified_diff(
            original_str.split('\n'),
            optimized_str.split('\n'),
            filename, filename, n=4)
        for uni_line in uni_diff:
            print(uni_line)

if '__main__' == __name__:
    aparser = argparse.ArgumentParser(
        prog='lilsumthing',
        description='Try to rewrite for-loop based summations'
        ' to use closed-form expressions',)
    aparser.add_argument('-v', '--verbose', action='store_true', default=False)
    aparser.add_argument('filenames', metavar='FILE', nargs='+',
                         help='python module files to examine')
    args = aparser.parse_args()
    for filename in args.filenames:
        optimize_file(filename, verbose=args.verbose)
