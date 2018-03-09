
from Setting.setting  import Setting
import smtplib
from Email.header import Header
from Email.utils import parseaddr, formataddr
from Email.mime.text import MIMEText


class EmailManager(object):

    _server = server = smtplib.SMTP()

    def __init__(self, user, password):
        self._user = user
        self._password = password
        self._sender = self._user
        self._templates = {}



    def get_content(self):
        """获取邮件模版"""
        me = u'淘淘金新闻收集 <%s>' % 'fxxclwk@163.com'
        print(me)
        news_list = [
            {'title': '深交所：推进债市服务实体经济向纵深发展',
             'url': 'http://bond.hexun.com/2018-01-26/192317103.html'
             },
            {'title': '东哥说股：三一重工均线多头，短期上涨走势已成！',
             'url': 'http://stock.hexun.com/2018-01-27/192327892.html'
             },
            {'title': '东哥说股：三一重工均线多头，短期上涨走势已成！',
             'url': 'http://stock.hexun.com/2018-01-27/192327892.html'
             },
        ]
        content = '该邮件共包含%d条新闻\n\n' % len(news_list)
        for index, news in enumerate(news_list):
            content = content + ''.join(['%s、' % str(index + 1), news['title'], '\n', news['url'], '\n'])
        # print(content)
        msg = MIMEText(content, _subtype='plain', _charset='utf-8')
        msg['Subject'] = '淘淘金'
        msg['From'] = self._format_addr(me)
        msg['To'] = ";".join(['253862014@qq.com'])

        return msg

    def send(self, receivers):
        """发送邮件"""
        # try:
        EmailManager._server.connect(Setting.EMAIL_SERVER)
        EmailManager._server.login(self._user, self._password)
        print('2')
        msg = self.get_content()
        EmailManager._server.sendmail(self._sender, [receivers], msg.as_string())
        EmailManager._server.close()
        # return False
        # except:
        #     return True

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))


if __name__ == '__main__':
    manager = EmailManager(Setting.SERVER_USER, Setting.SERVER_PASSWORD)
    res = manager.send(['253862014@qq.com'])
    print(res)

