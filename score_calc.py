import math

def calc_scr(x, y, target=[0, 0]):
    score_out=0
    con=2.5
    div=50

    score=1
    score_x=math.log(1366, con+abs(x-target[0])/div)
    score_y=math.log(768, con+abs(y-target[1])/div)
    score+=min([score_x, score_y])*2

    if score<0:
        score=0
    score=((score/10)**1.5)*0.5
    #return round(score, 1)
    score_out=score*9000

    score_out=str(round(score_out))
    while len(score_out)!=5 and False:
        score_out="0"+score_out
    return score_out


def calc_scr_br(rgn):
    t_scores=[[calc_scr(i*1366/rgn, j*768/rgn, [1366/2, 768/2]) for j in range(rgn)] for i in range(rgn)]
    for score in t_scores:
        print(score)


def calc_hard(rgn, hard, const):
    print(hard+const*rgn)
    for i in range(rgn):
        hard+=(const/((hard+0.6)**3))
    return hard


def gen(mx):
    doub=lambda x, i, mx: [x*(i/mx), x*((mx-i)/mx)]

    poses=[]
    x=1366
    y=768
    dig=(2*y**2)**0.5
    for i in range(int(mx/2)):
        i+=1
        line=[]
        line+=doub(x, i, mx)
        line+=doub(y, i, mx)
        line+=doub(dig, i, mx)
        line+=doub(dig, i, mx)
        poses.append(line)

    return poses


def calc_scr2(vals):
    vals.sort()
    print("\n\n\n----Start----")
    print(vals)
    print((sum([(pos**2)*i/5 for pos, i in enumerate(vals[::-1])])/16000)*10000)
    print((sum([(pos**2.5)*i/11.7 for pos, i in enumerate(vals[::-1])])/16000)*10000)
    print((sum([(pos**3)*i/28 for pos, i in enumerate(vals[::-1])])/16000)*10000)
    print((sum([(i**(pos/4))/3.6 for pos, i in enumerate(vals[::-1])])/16000)*10000)
    print((sum([(i**(pos/6)) for pos, i in enumerate(vals[::-1])])/2200)*10000)


def move_hor(ang, cur):
        if ang%180<90:
            ad=45/4
        else:
            ad=-45/4
        cur=(cur+ad)%360
        return cur


def new_score(pos):
    dic=dict(zip([int(360/8)*i for i in range(8)], [1366 for i in range(8)]))
    del dic[0]
    del dic[180]
    for i in [-1, 1]:
        for j in [0, 180]:
            dic[move_hor(i, j)]=pos[(i%3)%2]

    print(dic)

    ret=sum(list(dic.values()))
    mn=0
    for key, val in dic.items():
        if key%180==key:
            opp=key+180
        else:
            opp=key%180

        mn+=abs(val-dic[opp])
    ret-=(mn/2)
    return ret


if __name__=="__main__":
    #calc_scr_br(20)
    #print(calc_hard(15000, 0.1, 0.0001))

    poses=gen(8)
    for pos in poses:
        print(pos)
        #print(calc_scr2(pos))
        print(new_score(pos))
