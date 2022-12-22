def sum1(n):
    # 608850 * n <=> 4950 * 123 * n
    x = 0
    for i in range(100):
        x += i * 123 * n
    return x

def sum2(n):
    # 328350 * n <=> (((100-1)*(100)*(2*(100-1)+1))//6)* n
    x = 0
    for i in range(100):
        x += i * i * n
    return x

def sum3(n):
    S = 0
    for i in range(1,50000000):
        S += i*(3+i*n+4)*i + (3+n*3*i)*5 + i*(2+n+i)*5
    return S

print(sum1(1))
print(sum2(1))
print(sum3(1))
