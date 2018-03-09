import threading

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
        amac.AmacSpider().run,
        amac2.Amac2Spider().run,
        bjjrj.BjjrjSpider().run,
        cbrc.CbrcSpider().run,
        cctv.CctvSpider().run,
        circ.CircSpider().run,
        circ2.Circ2Spider().run,
        cnstock.CnstockSpider().run,
        cs.CsSpider().run,
        csrc.CsrcSpider().run,
        fangchan.FangChanSpider().run,
        gzjrj.GzjrjSpider().run,
        hexun.HeXunSpider().run,
        jingji.JingJiSpider().run,
        mohurd.MoHurdSpider().run,
        pbc.PbcSpider().run,
        shanghai.ShangHaiSpider().run,
        stcn.StcnSpider().run,
        szjrj.SzJrjSpider().run,
        xinhua.XinHuaSpider().run,
        zqrb.ZqrbSpider().run,
    ]

    threads = []
    for index, target in enumerate(targets):
        t = threading.Thread(target=target)
        threads.append(t)
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()
    print('最后的最后')





