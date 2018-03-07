import re
import requests
url="http://www.hexun.com/"

file=requests.get(url)
file.encoding = 'gbk'

ss=file.text

# ss=file.text.replace(" ","")
# urls=re.findall(r"<a.*?href=.*?<\/a>",ss,re.I)
urls=re.findall(r"href=\"http://[a-z]{4,10}.hexun.com/\d+-\d+-\d+/\d+.html\"",ss,re.I)

print(len(urls))

for i in urls:
 print(i)
else:
 print('this is over')