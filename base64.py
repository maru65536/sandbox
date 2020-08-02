def base64_encording(s):
    t=''
    #二進数に変換
    for c in s:
        t+=bin(ord(c))[2:].zfill(8)
    #bit長が6の倍数でない場合は後端を0で埋める
    t+='0'*(6-len(t)%6 if len(s)%3!=0 else 0)
    #変換表
    def transrate_e(st):
        n=0
        for j in range(6):
            if st[-1-j]=='1':
                n+=2**j
        if n<=25:
            return chr(n+65)
        elif n<=51:
            return chr(n+71)
        elif n<=61:
            return str(n-52)
        elif n==62:
            return '+'
        else:
            return '/'
    tex=''
    #6文字ずつ変換を行う
    for i in range(len(t)//6):
        a=t[i*6:(i+1)*6]
        tex+=transrate_e(a)
    #文字数が4の倍数でない場合は後端を'='で埋める
    tex+='='*(4-len(tex)%4 if len(tex)%4!=0 else 0)
    return tex

def base64_decording(s):
    s.replace('=','')
    def transrate_d(st):
        if st.islower():
            bit=ord(st)-65
        elif st.isupper():
            bit=ord(st)-71
        elif st.isdecimal():
            bit=int(st)+52
        elif st=='+':
            bit=62
        else:
            bit=63
        return bin(bit)[2:].zfill(6)
    transrate_d(1)
    #0埋めで発生した0かもともとある0かの判定がつかない　あきらめた