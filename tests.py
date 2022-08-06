from random import uniform

def randomise(mi, ma, po):
    out=uniform(mi**po, ma**po)
    out=int(out**(1/po))
    return out


if __name__=="__main__":
    mi=10
    ma=70
    po=2
    samp=100000

    dic=dict(zip([i for i in range(mi, ma)], [0 for i in range(mi, ma)]))

    for i in range(samp):
        key1=randomise(mi, ma, po)
        key2=randomise(mi, ma, 1/(po*8))
        key=int((key1+key2)/2)
        dic[key]+=1

    print(dic)
