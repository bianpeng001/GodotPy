#
# chinese number
#

# 〇零, 选一个吧
_ch_num = ['〇','一','二','三','四','五','六','七','八','九',]
def num_to_chinese(num):
    if num == 0:
        return _ch_num[0]
    
    minus = num < 0
    if minus:
        num = -num
        
    s = []
    while num > 0:
        d = num % 10
        s.append(_ch_num[d])
        num //= 10
    
    if minus:
        s.append('负')
    s.reverse()
    
    return ''.join(s)

_ch_0 = '零'
_ch_num1 = [_ch_0,'一','二','三','四','五','六','七','八','九']
_ch_num2 = [_ch_0,'十','百','千','万','亿','京']
def num_to_chinese2(num):
    index = 0
    s = []
    n = 0
    while num > 0:
        if index % 4 == 0 and index > 0:
            if n == len(s):
                s.pop()
            s.append(_ch_num2[index // 4 + 3])
            n = len(s)
        
        d = num % 10
        if d > 0 and index % 4 > 0:
            s.append(_ch_num2[index % 4])
        
        if d == 0:
            if len(s) > n and s[-1] != _ch_0:
                s.append(_ch_0)
        else:
            s.append(_ch_num1[d])

        num //= 10
        index += 1
        
    s.reverse()
    
    return ''.join(s)

if __name__ == '__main__':
    print(num_to_chinese(1000123))
    print(num_to_chinese2(1000020))
    print(num_to_chinese2(20001000020))
    print(num_to_chinese2(2000000020))
