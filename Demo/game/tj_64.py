#
# 太极八卦, 文王周易
# 六十四卦
# https://zh.wikipedia.org/wiki/%E5%85%AD%E5%8D%81%E5%9B%9B%E5%8D%A6
#


# |¦
class GuaItem:
    def __init__(self, sname, name, digits, detail):
        self.sname = sname
        self.name = name
        self.digits = digits
        self.detail = detail

guaci_list = [ i for i in range(64) ]

guaci_list[0b000000] = GuaItem('坤', '坤为地', '¦¦¦ ¦¦¦',\
'''坤：元亨。利牝马之贞。
君子有攸往，先迷后得，主利。
西南得朋，东北丧朋。安贞，吉。
初六：履霜，坚冰至。
六二：直方大，不习无不利。
六三：含章，可贞。或从王事，无成有终。
六四：括囊，无咎无誉。
六五：黄裳，元吉。
上六：龙战于野，其血玄黄。
用六：利永贞。''')





