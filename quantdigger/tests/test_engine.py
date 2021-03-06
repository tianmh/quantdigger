# -*- coding: utf-8 -*-
from quantdigger.engine.qd import *
from quantdigger.engine.series import NumberSeries, DateTimeSeries
import datetime
import unittest
import pandas as pd
import os
import talib
import numpy as np
from logbook import Logger
logger = Logger('test')


class TestSeries(unittest.TestCase):
        
    def test_case(self):
        close, open, dt, high, low, volume = [], [], [], [], [], []
        open3, dt3 = [], []
        ma3, ma2 = [], []
        svar = []
        true_test = []
        on_exit = {
                'dlist': [],
                'series': [],
                'dtseries': [],
                }
        ## @todo 在多合约中测试on_final, on_exit

        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                ctx.ma3 = MA(ctx.close, 3)
                ctx.svar = NumberSeries()
                ctx.series = NumberSeries()
                ctx.dtseries = DateTimeSeries()
                ctx.dlist = []
                return

            def on_bar(self, ctx):
                ## @todo + - * /
                true_test.append(ctx.open-0 == ctx.open[0])
                true_test.append(ctx.close-0 == ctx.close[0])
                true_test.append(ctx.high-0 == ctx.high[0])
                true_test.append(ctx.low-0 == ctx.low[0])
                true_test.append(ctx.volume-0 == ctx.volume[0])

                ctx.dlist.append(ctx.curbar)
                if ctx.curbar >= 100 and ctx.curbar < 300:
                    ctx.series.update(100) 
                    ctx.dtseries.update(datetime.datetime(1000,1,1))
                elif ctx.curbar >= 300:
                    ctx.dtseries.update(datetime.datetime(3000,1,1))
                    ctx.series.update(300) 

                open.append(ctx.open[0])
                close.append(ctx.close[0])
                high.append(ctx.high[0])
                low.append(ctx.low[0])
                volume.append(int(ctx.volume[0]))
                dt.append(ctx.datetime[0])
                open3.append(ctx.open[3])
                dt3.append(ctx.datetime[3])
                svar.append(ctx.svar[0])

            def on_final(self, ctx):
                return

            def on_exit(self, ctx):
                on_exit['dlist'] = ctx.dlist
                on_exit['series'] = ctx.series.data
                on_exit['dtseries'] = ctx.dtseries.data
                assert(ctx.curbar == len(close))
                return

        ## @todo 滚动的时候无法通过测试
        set_symbols(['BB.SHFE-1.Minute'], 0)
        add_strategy([DemoStrategy('A1')])
        run()
        self.assertTrue(all(true_test), "系统序列变量转化错误!")
        logger.info('----------------- 系统序列变量转化测试成功 -------------------')

        for i in xrange(0, len(on_exit['dlist'])):
            self.assertTrue(i+1 == on_exit['dlist'][i])
        logger.info('----------------- 用户普通变量测试成功 -------------------')
        logger.info('----------------- curbar测试成功 -------------------')

        series = on_exit['series']
        dtseries = on_exit['dtseries']
        dt1980 = datetime.datetime(1980,1,1)
        dt1000 = datetime.datetime(1000,1,1)
        dt3000 = datetime.datetime(3000,1,1)
        for i in xrange(0, len(series)):
            if i < 99:
                self.assertTrue(series[i] == 0.0) 
                self.assertTrue(dtseries[i] == dt1980) 
            elif i >= 99 and i < 299:
                self.assertTrue(series[i] == 100) 
                self.assertTrue(dtseries[i] == dt1000) 
            elif i >= 299:
                self.assertTrue(series[i] == 300) 
                self.assertTrue(dtseries[i] == dt3000) 
        logger.info('----------------- 用户序列变量测试成功 -------------------')

        # 值测试
        target = pd.DataFrame({
            'open': open,
            'close': close,
            'high': high,
            'low': low,
            'volume': volume,
            })
        target = target.ix[:, ['open', 'close', 'high', 'low', 'volume']]
        target.index = dt
        fname = os.path.join(os.getcwd(), 'data', 'BB.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertTrue(source.equals(target), "系统时间序列变量正测试出错")
        fname = os.path.join(os.getcwd(), 'data', 'CC.SHFE-1.Minute.csv')
        source = pd.read_csv(fname, parse_dates=True, index_col=0)
        self.assertFalse(source.equals(target), "系统时间序列变量反测试出错")
        # 保证非常量，从而保证回溯有效。
        conopen = [open[0] for i in xrange(0, len(open))]
        condt = [dt[0] for i in xrange(0, len(open))]
        self.assertFalse(open == conopen)
        self.assertFalse(dt == condt)
        logger.info('----------------- 系统序列变量值的正确测试成功 -------------------')

        # 回溯测试
        for i in xrange(0, len(open)):
            if i-3 >= 0:
                self.assertTrue(open3[i] == open[i-3], "系统序列变量回溯测试失败！" )
                self.assertTrue(dt3[i] == dt[i-3], "系统序列变量回溯测试失败！" )
            else:
                self.assertTrue(open3[i] == NumberSeries.DEFAULT_VALUE,
                                            "系统序列变量回溯测试失败！")
                self.assertTrue(dt3[i] == DateTimeSeries.DEFAULT_VALUE,
                                                "系统序列时间变量回溯测试失败！")
            self.assertTrue(svar[i] == NumberSeries.DEFAULT_VALUE)
        logger.info('----------------- 系统序列变量回溯测试成功 -------------------')

        self.assertTrue(NumberSeries.DEFAULT_VALUE == 0.0)
        self.assertTrue(DateTimeSeries.DEFAULT_VALUE == datetime.datetime(1980,1,1))
        logger.info('----------------- 系统序列类型默认值测试成功 -------------------')



class TestIndicator(unittest.TestCase):
        
    def test_case(self):
        close, open, ma2 = [], [], []
        pre_ma2 = []
        true_test = []
        boll = {
                'upper': [],
                'middler': [],
                'lower': []
                }

        boll3 = {
                'upper': [],
                'middler': [],
                'lower': []
                }

        class DemoStrategy(Strategy):
            def on_init(self, ctx):
                """初始化数据""" 
                ctx.ma2 = MA(ctx.close, 2)
                ctx.boll = BOLL(ctx.close, 2)

            def on_bar(self, ctx):
                if ctx.curbar>=2:
                    ## @todo + - * /
                    true_test.append(ctx.ma2-0 == ctx.ma2[0])
                    
                pre_ma2.append(ctx.ma2[3])
                ma2.append(ctx.ma2[0])
                close.append(ctx.close[0])
                open.append(ctx.open[0])
                boll['upper'].append(ctx.boll['upper'][0])
                boll['middler'].append(ctx.boll['middler'][0])
                boll['lower'].append(ctx.boll['lower'][0])
                boll3['upper'].append(ctx.boll['upper'][3])
                boll3['middler'].append(ctx.boll['middler'][3])
                boll3['lower'].append(ctx.boll['lower'][3])


            def on_final(self, ctx):
                return

            def on_exit(self, ctx):
                return

        ## @todo 滚动的时候无法通过测试
        set_symbols(['BB.SHFE-1.Minute'], 0)
        add_strategy([DemoStrategy('A1')])
        run()
        self.assertTrue(all(true_test), "指标转化错误!")
        logger.info('----------------- 指标转化测试成功 -------------------')

        # 分别测试单值和多值指标函数。
        source_ma2 = talib.SMA(np.asarray(close), 2)
        true_test, false_test = [], []
        for i in xrange(0, len(close)):
            if i >=  1:
                true_test.append(ma2[i] == source_ma2[i])
            else:
                false_test.append(ma2[i] == ma2[i])
        self.assertFalse(any(false_test), "单值指标正例测试失败!")
        self.assertTrue(all(true_test), "单值指标正例测试失败!")
        source_ma2 = talib.SMA(np.asarray(open), 2)
        true_test, false_test = [], []
        for i in xrange(0, len(open)):
            if i >=  1:
                true_test.append(ma2[i] == source_ma2[i])
            else:
                false_test.append(ma2[i] == ma2[i])
        self.assertFalse(any(false_test), "单值指标反例测试失败!")
        self.assertFalse(all(true_test), "单值指标反例测试失败!")
        logger.info('----------------- 单值指标测试成功 -------------------')

        true_test, false_test = [], []
        source_ma2 = talib.SMA(np.asarray(close), 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(pre_ma2[i] == source_ma2[i-3])
            else:
                # 指标序列变量的默认值为nan
                false_test.append(pre_ma2[i] == pre_ma2[i])
        self.assertTrue(all(true_test), "单值指标回溯正例测试成功")
        self.assertFalse(any(false_test), "单值指标回溯正例测试成功")
        true_test, false_test = [], []
        source_ma2 = talib.SMA(np.asarray(open), 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(pre_ma2[i] == source_ma2[i-3])
            else:
                # 指标序列变量的默认值为nan
                false_test.append(pre_ma2[i] == pre_ma2[i])
        self.assertFalse(all(true_test), "单值指标回溯反例测试成功")
        self.assertFalse(any(false_test), "单值指标回溯反例测试成功")
        logger.info('----------------- 单值指标回溯测试成功 -------------------')

        #
        u, m, l = talib.BBANDS(np.asarray(close), 2, 2, 2)
        true_test, false_test = [], []
        for i in xrange(0, len(close)):
            if i >=  1:
                true_test.append(boll['upper'][i] == u[i])
                true_test.append(boll['middler'][i] == m[i])
                true_test.append(boll['lower'][i] == l[i])
            else:
                false_test.append(boll['upper'][i] == boll['upper'][i])
                false_test.append(boll['middler'][i] == boll['middler'][i])
                false_test.append(boll['lower'][i] == boll['lower'][i])
        self.assertFalse(any(false_test), "多值指标正例测试失败!")
        self.assertTrue(all(true_test), "多值指标正例测试失败!")
        u, m, l = talib.BBANDS(np.asarray(open), 2, 2, 2)
        true_test, false_test = [], []
        for i in xrange(0, len(close)):
            if i >=  1:
                true_test.append(boll['upper'][i] == u[i])
                true_test.append(boll['middler'][i] == m[i])
                true_test.append(boll['lower'][i] == l[i])
            else:
                false_test.append(boll['upper'][i] == boll['upper'][i])
                false_test.append(boll['middler'][i] == boll['middler'][i])
                false_test.append(boll['lower'][i] == boll['lower'][i])
        self.assertFalse(any(false_test), "多值指标反例测试失败!")
        self.assertFalse(all(true_test), "多值指标反例测试失败!")
        logger.info('----------------- 多值指标测试成功 -------------------')


        true_test, false_test = [], []
        u, m, l = talib.BBANDS(np.asarray(close), 2, 2, 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(boll3['upper'][i] == u[i-3])
            else:
                false_test.append(boll3['upper'][i] == boll3['upper'][i])
        self.assertTrue(all(true_test), "多值指标回溯正例测试成功")
        self.assertFalse(any(false_test), "多值指标回溯正例测试成功")
        true_test, false_test = [], []
        u, m, l = talib.BBANDS(np.asarray(open), 2, 2, 2)
        for i in xrange(0, len(close)):
            if i >= 4:
                true_test.append(boll3['upper'][i] == u[i-3])
            else:
                false_test.append(boll3['upper'][i] == boll3['upper'][i])
        self.assertFalse(all(true_test), "多值指标回溯反例测试成功")
        self.assertFalse(any(false_test), "多值指标回溯反例测试成功")
        logger.info('----------------- 多值指标回溯测试成功 -------------------')


class TestMultipleCombination(unittest.TestCase):
    """ 多组合策略测试 """
        
    def test_case(self):
        on_exit = {
                'strategy': [],
                }

        on_final = {
                'strategy': [],
                }
        on_bar = {
                'combination': set(),
                'count': 0
                }

        class DemoStrategy(Strategy):
            
            def on_init(self, ctx):
                """初始化数据""" 
                return

            def on_bar(self, ctx):
                #print ctx.strategy, ctx.pcontract
                on_bar['combination'].add((str(ctx.pcontract), ctx.strategy))
                on_bar['count'] += 1
                pass

            def on_final(self, ctx):
                on_final['strategy'].append(ctx.strategy)

            def on_exit(self, ctx):
                on_exit['strategy'].append(ctx.strategy)
                return

        simulator = set_symbols(['BB.SHFE-1.Minute', 'AA.SHFE-1.Minute'], 0)
        add_strategy([DemoStrategy('A1'), DemoStrategy('A2')])
        add_strategy([DemoStrategy('B1'), DemoStrategy('B2')])
        run()

        fname = os.path.join(os.getcwd(), 'data', 'BB.SHFE-1.Minute.csv')
        blen = len(pd.read_csv(fname))
        fname = os.path.join(os.getcwd(), 'data', 'AA.SHFE-1.Minute.csv')
        alen = len(pd.read_csv(fname))
        sample = set([
                ('BB.SHFE-1.Minute', 'A1'),
                ('BB.SHFE-1.Minute', 'A2'),
                ('AA.SHFE-1.Minute', 'A1'),
                ('AA.SHFE-1.Minute', 'A2'),
                ('BB.SHFE-1.Minute', 'B1'),
                ('BB.SHFE-1.Minute', 'B2'),
                ('AA.SHFE-1.Minute', 'B1'),
                ('AA.SHFE-1.Minute', 'B2')
        ])
        self.assertTrue(on_bar['combination'] == sample)
        sample.pop()
        self.assertFalse(on_bar['combination'] == sample)
        self.assertTrue(on_bar['count'] == alen*4 + blen*4)
        self.assertFalse(on_bar['count'] == alen*3 + blen*4)
        self.assertTrue(['A1', 'A2', 'B1', 'B2']*max(blen, alen) == on_final['strategy'],
                        'on_final测试失败！')
        self.assertFalse(['C1', 'A2', 'B1', 'B2']*max(blen, alen) == on_final['strategy'],
                        'on_final测试失败！')
        self.assertTrue(['A1', 'A2', 'B1', 'B2'] == on_exit['strategy'], 'on_exit测试失败！')
        self.assertFalse(['C1', 'A2', 'B1', 'B2'] == on_exit['strategy'], 'on_exit测试失败！')
        logger.info('----------------- 多组合策略测试成功！ -------------------')

        # Context单元测试
        context = simulator.context
        data_contexts = []
        strategies = [['A1', 'A2'], ['B1', 'B2']]
        for pcon,  dctx in context._data_contexts.iteritems():
            self.assertTrue(pcon == dctx.pcontract, "Context数据上下文出错")
            data_contexts.append(str(dctx.pcontract))
        for i, sctx in enumerate(context._strategy_contexts):
            self.assertTrue(strategies[i] == [s.name for s in sctx], "Context策略上下文出错")
        ## @todo 资金配比测试 


class TestSimulator(unittest.TestCase):
    """ 多组合策略测试 """
        
    def test_case(self):
        ## @todo profile
            # all_holdings 长度一样
            # signals 盈利

        ## @todo 回测案例
        # 隔天第一根买卖，很容易计算结果。

        ## @TODO deals DemoStrategy2
        pass

if __name__ == '__main__':
    unittest.main()
