#!/usr/bin/python
#encoding:utf-8
import xlwt
import xlrd
import datetime
import matplotlib.pyplot as plt
import numpy
from multiprocessing.dummy import Pool as ThreadPool
import time

def process(name, buy_rate_a, buy_rate_b, sell_rate_c, sell_rate_d, regular_investment_amount):
#############################################################
#基础设定
# zhiyinzhisunbili = 0.05
# fene = 6

    inputMoney = 50000
    fee = 0.001#交易手续费
    ZRB = 1.1**(1.0/12)-1#真融宝收益比较
    ZRBM = inputMoney
    timesM = 10000.0


    #############################################################
    #读文件
    title = xlrd.open_workbook(name + '.xls')
    table = title.sheet_by_name('Table')
    #写文件

    #读取每一列
    price = table.col_values(1)
    date = table.col_values(0)
    limit = table.col_values(2)
    # price = [0]
    #
    # for i in range(1, len(tmpPrice)):
    #     price.append(tmpPrice[i])
    #
    #
    # for i in range(21, len(price)):
    #     #每20个price组成一个temp数组
    #     tmplist = price[i-20:i]
    #
    #     MA20 = sum(tmplist)/20.0
    #
    #
    #
    # for i in range(201, len(price)):
    #     #每20个price组成一个temp数组
    #     tmplist = price[i-60:i]
    #     #print tmplist
    #     #print tmplist
    #     MA60 = sum(tmplist)/60.0


    #开始投资
    tmpMonth = date[21][5:7]#初始月份

    stockNum = 0
    stockMoney = 0
    restMoney = inputMoney
    savedMoney = 0
    totalMoney = stockMoney + restMoney + savedMoney
    cost = inputMoney

    #无脑投初始状态
    stockNum1 = int(inputMoney/(1+fee) / price[21] / 100) * 100
    stockMoney1 = stockNum1 * price[21]
    restMoney1 = inputMoney - stockMoney1 - stockMoney1 * fee
    totalMoney1 = stockMoney1 + restMoney1

    average_cost = 0
    highest_recent = price[22]

    #开始循环投资
    for i in range(22, len(price)):
        #先算今天的资产情况
        stockMoney = stockNum * price[i]
        stockMoney1 = stockNum1 * price[i]

        if price[i] > highest_recent:
            highest_recent = price[i]

        #计算当前月份
        nowMonth = date[i][5:7]
        if nowMonth != tmpMonth:#月份发生改变,定投
            #二十日线定投
            cost += regular_investment_amount
            savedMoney += regular_investment_amount
            tmpMonth = nowMonth
            #真融宝
            ZRBM = ZRBM * (1+ZRB) + regular_investment_amount

            #无脑定投
            tmpStockNum1 = int((regular_investment_amount + restMoney1)/(1+fee) / price[i] / 100) * 100
            if tmpStockNum1 != 0:#够买一份了，那就买买买
                stockNum1 += tmpStockNum1
                stockMoney1 += (tmpStockNum1 * price[i])
                restMoney1 = restMoney1 + regular_investment_amount - tmpStockNum1 * price[i] - tmpStockNum1 * price[i] * fee

            else:
                restMoney1 += regular_investment_amount

        totalMoney1 = stockMoney1 + restMoney1

    #    if nowMonth != tmpMonth:#月份发生改变,定投
    #        tmpMonth = nowMonth

        # print stockNum
        # print price[i]
        # print pingjunchengben
        # print zongtourujine
        # print '-------------'

        if price[i] < average_cost * (1 - buy_rate_a):
            tmpStockNum = int((savedMoney + restMoney) * buy_rate_b / (1 + fee) / price[i] / 100) * 100
            if tmpStockNum != 0:  # 购买一份了，那就买买买
                total_cost = average_cost * stockNum

                stockNum += tmpStockNum
                stockMoney += (tmpStockNum * price[i])
                restMoney = restMoney + savedMoney - tmpStockNum * price[i] - tmpStockNum * price[i] * fee
                savedMoney = 0  # 存起来的钱清零

                total_cost += tmpStockNum * price[i]
                average_cost = float(total_cost) / float(stockNum)

        elif price[i] < highest_recent * (1 - sell_rate_c) and stockNum > 0:
            tmpStockNum = stockNum * sell_rate_d

            restMoney += (price[i] * tmpStockNum * (1 - fee))
            stockNum = stockNum - tmpStockNum
            stockMoney = price[i] * stockNum

        # print('stockNum %d totalMoney %d restMoney %d' % (stockNum, totalMoney, restMoney))

        totalMoney = stockMoney + restMoney + savedMoney


    daysPast = datetime.datetime.strptime(date[-1][0:10], '%Y-%m-%d') - \
                        datetime.datetime.strptime(date[1][0:10], '%Y-%m-%d')

    AnnualInterestRate = ((totalMoney / float(cost)) ** (1 / (float(daysPast.days) / 365.0)) - 1) * 100

    return AnnualInterestRate

def process_main(regular_investment_amount_tmp):
    buy_rate_a = 0.0
    buy_rate_b = 0.0
    sell_rate_c = 0.0
    sell_rate_d = 0.0
    regular_investment_amount = 100
    annualized_interest_rate = 0.0

    for buy_rate_a_tmp in numpy.arange(0.02, 0.30, 0.01):
        for buy_rate_b_tmp in numpy.arange(0.05, 1, 0.05):
            for sell_rate_c_tmp in numpy.arange(0.02, 0.30, 0.01):
                for sell_rate_d_tmp in numpy.arange(0.05, 1, 0.05):
                        start = time.time()
                        annualized_interest_rate_tmp = process('000001', buy_rate_a_tmp, buy_rate_b_tmp,
                                                               sell_rate_c_tmp, sell_rate_d_tmp,
                                                               regular_investment_amount_tmp)
                        end = time.time()
                        print end - start
                        print annualized_interest_rate_tmp, code, buy_rate_a_tmp, buy_rate_b_tmp, sell_rate_c_tmp, sell_rate_d_tmp, regular_investment_amount_tmp
                        print annualized_interest_rate, code, buy_rate_a, buy_rate_b, sell_rate_c, sell_rate_d, regular_investment_amount

                        if annualized_interest_rate_tmp > annualized_interest_rate:
                            buy_rate_a = buy_rate_a_tmpu
                            buy_rate_b = buy_rate_b_tmp
                            sell_rate_c = sell_rate_c_tmp
                            sell_rate_d = sell_rate_d_tmp
                            regular_investment_amount = regular_investment_amount_tmp
                            annualized_interest_rate = annualized_interest_rate_tmp
                            print anualized_interest_rate_tmp, code, buy_rate_a_tmp, buy_rate_b_tmp, sell_rate_c_tmp, sell_rate_d_tmp, regular_investment_amount_tmp
                        print '--------------'

    return [code, anualized_interest_rate, buy_rate_a, buy_rate_b, sell_rate_c, sell_rate_d, regular_investment_amount]

if __name__ == '__main__':
    codelist = ['000001']

    pool = ThreadPool(4)

    for code in codelist:
        regular_investment_amount_tmp = [i for i in range(200, 2000, 200)]
        result = pool.map(process_main, regular_investment_amount_tmp)

        print '***************'
        print result
        print '***************'
    pool.close()
    pool.join()
    # nianlilvtemp = process('159902', 0.05, 6)
