import re


con_list = ['dsads我们的', '   呵呵oo']

contents = [re.sub(r'[a-z]+|\s+', '', cc) for cc in con_list]



print(contents)


