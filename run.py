import threading, time
from Setting.setting  import Setting

from Tools.log import log_line, log
from Email.EmailManager import EmailManager
from Spiders import amac
from Spiders import amac2
from Spiders import bjjrj
from Spiders import cbrc
from Spiders import cctv
from Spiders import circ
from Spiders import circ2
from Spiders import cnstock
from Spiders import cs
from Spiders import csrc
from Spiders import fangchan
from Spiders import gzjrj
from Spiders import hexun
from Spiders import jingji
from Spiders import mohurd
from Spiders import pbc
from Spiders import shanghai
from Spiders import stcn
from Spiders import szjrj
from Spiders import xinhua
from Spiders import zqrb


if __name__ == '__main__':

    targets = [
        # amac.AmacSpider().run,
        # amac2.Amac2Spider().run,
        # bjjrj.BjjrjSpider().run,
        # cbrc.CbrcSpider().run,
        # cctv.CctvSpider().run,
        # circ.CircSpider().run,
        # circ2.Circ2Spider().run,  # 未完成！！检查！！
        # cnstock.CnstockSpider().run,
        # cs.CsSpider().run,
        # csrc.CsrcSpider().run,
        # fangchan.FangChanSpider().run,
        # gzjrj.GzjrjSpider().run,
        # hexun.HeXunSpider().run,
        # jingji.JingJiSpider().run,
        # mohurd.MoHurdSpider().run,
        # pbc.PbcSpider().run,
        # shanghai.ShangHaiSpider().run,
        # stcn.StcnSpider().run,
        # szjrj.SzJrjSpider().run,
        # xinhua.XinHuaSpider().run,
        # zqrb.ZqrbSpider().run,
    ]

    start = time.time()

    threads = []
    for index, target in enumerate(targets):
        t = threading.Thread(target=target)
        threads.append(t)
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()

    # 发送邮件
    log('准备发送邮件')
    manager = EmailManager(Setting.SERVER_USER, Setting.SERVER_PASSWORD)
    manager.send(manager.get_emails())
    log('邮件发送完成')
    cost= time.time() - start
    log('耗时', cost)


    '''
    邮件内容需要增加：
    新闻所在的网站
    新闻关键词

    '''





