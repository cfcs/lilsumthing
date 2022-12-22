import ast
import itertools
from functools import reduce

import argparse
import difflib

# TODO instead of defining functions for square, cube etc for powers it would be
# nice to just generalize by adding nested sum loops.

def gauss(n):
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
    '''see square_from_to'''
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
    return cube_to(t) - cube_to(f)

def is_add(n):
    return type(n) == ast.BinOp and type(getattr(n,'op',None)) == ast.Add

class StateMachine():
    def __init__(self, for_target, for_range):
        self.for_target : ast.Name = for_target # (i) in 'for i in range..'
        self.for_range = for_range
        # computed optimization to replace the ast.For loop with:
        self.for_replacement : ast.AST = None
        # abort optimizing this For loop:
        self.dont_optimize = False

class ProductWalker(ast.NodeTransformer):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.level = 0
        self.node_id = 0
        self.states = [] # stack of state machine states for ast.For loops
        self.local_counters = {}
        self.allowed_name_refs = set()
        super().__init__()
    def pl(self, *a):
        if self.verbose:
            print('  '*self.level, *a)
        pass
    def pp(self, lst):
        return self.ppl(lst)
    def ppl(self, lstlst):
        if isinstance(lstlst, ast.AST):
            return ast.unparse(lstlst)
        if isinstance(lstlst[0], ast.AST):
            return '[' + '; '.join((self.ppl(y)
                                    for y in lstlst)) + ']'
        return '[' + '; '.join(
            self.ppl(x) for x in lstlst
        ) + ']'

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
               type(node.value) == ast.Constant:
                # TODO should try to check that it's a numerical constant?
                # or at least complain if it is clearly not
                self.pl('identified potential counter', target.id)
                self.allowed_name_refs.add(target)
                self.local_counters[target.id] = {
                    'value': node.value
                }
        return node

    def postprocess_augassign(self, node):
        self.pl('postprocess_augassign', self.ppl(node))
        adds = getattr(node.value, 'adds', [node.value])
        self.pl(self.ppl(adds))
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
                this_sum = reduce(int.__mul__, (x.value for x in constants), 1)
                # note that we have to be careful not to add a zero 'sum'
                # by accident. unless a constant above is 0,
                # this_sum will be nonzero because it's initialized with 1.
                # if there are no constants, it will be 1, so we retain the
                # property that [i]+[i] turns into [i;2] and not [i;0]:
                partitions[name_hash] = partitions.get(name_hash, {
                    'sum': 0,
                    'wo_constants': wo_constants
                })
                partitions[name_hash]['sum'] += this_sum
            # and finally we reconstruct the original format:
            ret = []
            for pdict in partitions.values():
                ret += [[*pdict['wo_constants'], ast.Constant(pdict['sum'])]]
            return ret
        adds = fold_constant_factors(adds)
        self.pl(self.pp(adds))

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
                if 1 == powers_of_loop_var:
                    adds[i] += [ast.Constant(self.states[-1].for_range['sum'])]
                elif 2 == powers_of_loop_var:
                    adds[i] += [ast.Constant(self.states[-1].for_range['square'])]
                elif 3 == powers_of_loop_var:
                    adds[i] += [ast.Constant(self.states[-1].for_range['cube'])]
                else:
                    # category 2 with loopvar^n with n >= 4, this should
                    # be handled in the future.
                    # in the meantime we should abort the postprocessing
                    # and set dont_optimize=True. TODO.
                    raise NotImplemented
                pass # category 2
        self.pl(self.ppl(adds))
        #
        # Add the initial value of the counter: the 123 in
        # (S = 123, for ... S += ..):
        #
        adds += [self.local_counters[node.target.id]['value']]
        #
        # Final reduction step:
        #
        adds = fold_constant_factors(adds)
        self.pl(self.ppl(adds))
        #
        # At the end we need to transform our [addends[products]] list into
        # a nested AST node structure:
        def mk_add(a,b):
            # TODO if they are both 0 we should remove it entirely,
            # instead of returning a ast.Constant(0):
            if type(a) == ast.Constant and a.value == 0: return b
            if type(b) == ast.Constant and b.value == 0: return a
            return ast.BinOp(left=a, op=ast.Add(), right=b)
        def mk_mult(a,b):
            if type(a) == ast.Constant and a.value == 0: return ast.Constant(0)
            if type(b) == ast.Constant and b.value == 0: return ast.Constant(0)
            if type(a) == ast.Constant and a.value == 1: return b
            elif type(b) == ast.Constant and b.value == 1: return a
            return ast.BinOp(left=a, op=ast.Mult(), right=b)
        adds = list(map(lambda addend: reduce(mk_mult, addend[:], ast.Constant(1)) , adds))
        self.pl(self.ppl(adds))
        expr = reduce(mk_add, adds, ast.Constant(0))
        self.states[-1].for_replacement = ast.Assign(
            targets=[node.target],
            value=[ expr ],
        )
        ast.fix_missing_locations(self.states[-1].for_replacement)
        self.pl(self.pp(node))
        self.pl('==>', self.pp(self.states[-1].for_replacement))
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

        if type(node) == ast.For and not node.orelse:
            self.pl('ast.For loop:', ast.unparse(node))
            p_range = optimizable_range(node.iter)
            self.states.append(StateMachine(node.target, p_range))
        elif type(node) == ast.AugAssign:
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

        if type(node) == ast.For and not node.orelse:
            # this is where we need to modify (node) to replace the For loop
            self.pl('ENDFOR')
            finalstate = self.states.pop()
            if finalstate.for_replacement and not finalstate.dont_optimize:
                ast.fix_missing_locations(finalstate.for_replacement)
                return finalstate.for_replacement
        elif still_optimizing:
            if type(node) == ast.BinOp:
                node = self.visit_BinOp_dfs(node)
            elif type(node) == ast.AugAssign and type(node.op) == ast.Add:
                # TODO we could handle repeated
                # S += abc...
                # S += def...
                # and do s_adds.extend(s2.adds) here. room for improvement :-)
                if node.target.id in self.local_counters:
                    node = self.postprocess_augassign(node)
        return node
    def visit_BinOp_dfs(self, node):
        pl, pp, ppl = self.pl, self.pp, self.ppl
        if is_add(node):
            node.adds = []
            left  = getattr(node.left, 'adds', [node.left])
            right = getattr(node.right, 'adds', [node.right])
            node.adds.extend(left)
            node.adds.extend(right)
            self.pl('Add.adds:', self.ppl(node.adds))
            return node
        elif type(node.op) == ast.Mult:
            left = getattr(node.left, 'adds', [node.left])
            right = getattr(node.right, 'adds', [node.right])
            self.pl('mult', ppl(left), ppl(right))
            prod = []
            # here we have the factors with nested lists:
            # [5; [3;2]]
            # and we want to flatten them, with the terrible code below:
            for p in itertools.product(right, left):
                prod.append([])
                for t in p:
                    if type(t) is list: prod[-1] += t
                    else: prod[-1] += [t]
            node.adds = prod
            self.pl('prod', ppl(prod))
        else:
            self.pl('better safe than sorry, not optimizing because', self.pp(node))
            self.states[-1].dont_optimize = True
        return node

def optimizable_range(iterable):
    '''Looks for sequential ranges whose length
    we can compute, and/or their sum.
    Currently only handles constants, and assumes they are integer. TODO.
    '''
    if type(iterable) == ast.Call:
        if type(iterable.func) == ast.Name:
            if iterable.func.id == 'range':
                if len(iterable.args) >= 1 and \
                   type(iterable.args[0]) == ast.Constant:
                    if len(iterable.args) == 1:
                        return {'len': iterable.args[0].value,
                                'square': square_to(iterable.args[0].value),
                                'cube': cube_to(iterable.args[0].value),
                                'sum': range_to(iterable.args[0].value)}
                    elif len(iterable.args) == 2 and \
                         type(iterable.args[1]) == ast.Constant:
                        return {'len':
                                iterable.args[1].value - iterable.args[0].value,
                                'square': square_from_to(
                                    iterable.args[0].value,
                                    iterable.args[1].value),
                                'cube': cube_from_to(
                                    iterable.args[0].value,
                                    iterable.args[1].value),
                                'sum': range_from_to(iterable.args[0].value,
                                                     iterable.args[1].value)
                                }
    return {}

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
