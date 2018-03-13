class A:
    def __init__(self):
        self.url = 'www'
        self.con = '你好'


class B(A):
    def __init__(self):
        self.url = 'uuu'
        self.con = '再见'
        self.start_urls = ['一样一样']

        A.__init__(self)



b = B()
print(b.url, b.start_urls)