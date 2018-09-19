def repeat(k):
    return detector(lambda : 0)(k)

def detector(f):
    def g(i):
        if ((f() // 10**i) % 10 > 0):
            print(i)
        return detector(lambda : f()//(10**(i+1))*(10**(i+1)) + 10**i + (0 if i==0 else f()%10**i))
    return g
