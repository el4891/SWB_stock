#!/usr/bin/python
#encoding:utf-8
import xlwt
import xlrd
import datetime
# import matplotlib.pyplot as plt
import numpy
from multiprocessing.dummy import Pool as ThreadPool
import time

def process(name, buy_rate_a, buy_rate_b, sell_rate_c, sell_rate_d, total_rate_e, regular_investment_amount):

    inputMoney = 50000
    fee = 0.001#交易手续费

    #读文件
    title = xlrd.open_workbook(name + '.xls')

    try:
        table = title.sheet_by_name('Table')
    except Exception as err:
        table = title.sheet_by_name(name)

    #读取每一列
    tmpPrice = table.col_values(1)
    date = table.col_values(0)
    limit = table.col_values(2)

    price = [0]
    if tmpPrice[1] > 10:#股价太高，说明是指数，降低1000倍
        for i in range(1, len(tmpPrice)):
            price.append(tmpPrice[i]/1000.0)
    else:
        for i in range(1, len(tmpPrice)):
            price.append(tmpPrice[i])

    #开始投资
    tmpMonth = date[21][5:7]#初始月份

    stockNum = 0
    stockMoney = 0
    restMoney = inputMoney
    savedMoney = 0
    totalMoney = stockMoney + restMoney + savedMoney
    cost = inputMoney

    average_cost = price[22]
    highest_recent = price[22]

    #开始循环投资
    for i in range(22, len(price)):
        #先算今天的资产情况
        stockMoney = stockNum * price[i]


        if price[i] > highest_recent:
            highest_recent = price[i]

        #计算当前月份
        nowMonth = date[i][5:7]
        if nowMonth != tmpMonth:#月份发生改变,定投
            #二十日线定投
            cost += regular_investment_amount
            savedMoney += regular_investment_amount
            tmpMonth = nowMonth

        if price[i] < average_cost * (1 - buy_rate_a):
            tmpStockNum = int((savedMoney + restMoney) * (totalMoney / (savedMoney + restMoney)) * buy_rate_b / (1 + fee) / price[i] / 100) * 100

            if tmpStockNum > int((savedMoney + restMoney) / (1 + fee) / price[i] / 100) * 100:
                tmpStockNum = int((savedMoney + restMoney) / (1 + fee) / price[i] / 100) * 100

            if tmpStockNum != 0:

                total_cost = average_cost * stockNum

                stockNum += tmpStockNum
                stockMoney += (tmpStockNum * price[i])
                restMoney = restMoney + savedMoney - tmpStockNum * price[i] - tmpStockNum * price[i] * fee
                savedMoney = 0  # 存起来的钱清零

                total_cost += tmpStockNum * price[i]
                average_cost = float(total_cost) / float(stockNum)
                highest_recent = price[i]

        elif price[i] < highest_recent * (1 - sell_rate_c) and stockNum > 0:
            tmpStockNum = int(stockNum * sell_rate_d / 100) * 100

            if tmpStockNum != 0:
                restMoney += (price[i] * tmpStockNum * (1 - fee))
                stockNum = stockNum - tmpStockNum
                stockMoney = price[i] * stockNum
                highest_recent = price[i]
                average_cost = price[i]

        # print('%s price %.3f limit %.3f stockNum %d totalMoney %d restMoney %d average_cost %.3f' % (date[i], price[i], limit[i], stockNum, totalMoney, restMoney, average_cost))

        totalMoney = stockMoney + restMoney + savedMoney

        if price[i] * stockNum < totalMoney * total_rate_e and stockNum != 0:
            average_cost = price[i]


    daysPast = datetime.datetime.strptime(date[-1][0:10], '%Y-%m-%d') - \
                        datetime.datetime.strptime(date[1][0:10], '%Y-%m-%d')

    AnnualInterestRate = ((totalMoney / float(cost)) ** (1 / (float(daysPast.days) / 365.0)) - 1) * 100

    return AnnualInterestRate

def process_main(regular_investment_amount_tmp):
    buy_rate_a = 0.0
    buy_rate_b = 0.0
    sell_rate_c = 0.0
    sell_rate_d = 0.0
    total_rate_e = 0.0
    regular_investment_amount = 100
    annualized_interest_rate = 0.0

    for buy_rate_a_tmp in numpy.arange(0.02, 0.22, 0.02):
        for buy_rate_b_tmp in numpy.arange(0.1, 0.52, 0.1):
            for sell_rate_c_tmp in numpy.arange(0.02, 0.22, 0.02):
                for sell_rate_d_tmp in numpy.arange(0.1, 0.52, 0.1):
                    for total_rate_e_tmp in numpy.arange(0.05, 0.22, 0.05):
                        start = time.time()
                        annualized_interest_rate_tmp = process(codenow, buy_rate_a_tmp, buy_rate_b_tmp,
                                                               sell_rate_c_tmp, sell_rate_d_tmp, total_rate_e_tmp,
                                                               regular_investment_amount_tmp)
                        end = time.time()
                        print end - start
                        print annualized_interest_rate_tmp, code, buy_rate_a_tmp, buy_rate_b_tmp, sell_rate_c_tmp, sell_rate_d_tmp, total_rate_e_tmp, regular_investment_amount_tmp
                        print annualized_interest_rate, code, buy_rate_a, buy_rate_b, sell_rate_c, sell_rate_d, total_rate_e, regular_investment_amount

                        if annualized_interest_rate_tmp > annualized_interest_rate:
                            buy_rate_a = buy_rate_a_tmp
                            buy_rate_b = buy_rate_b_tmp
                            sell_rate_c = sell_rate_c_tmp
                            sell_rate_d = sell_rate_d_tmp
                            total_rate_e = total_rate_e_tmp
                            regular_investment_amount = regular_investment_amount_tmp
                            annualized_interest_rate = annualized_interest_rate_tmp
                            print annualized_interest_rate_tmp, code, buy_rate_a_tmp, buy_rate_b_tmp, sell_rate_c_tmp, sell_rate_d_tmp, total_rate_e_tmp, regular_investment_amount_tmp
                        print '--------------'

    return [code, annualized_interest_rate, buy_rate_a, buy_rate_b, sell_rate_c, sell_rate_d, total_rate_e, regular_investment_amount]

codenow = '000001'

if __name__ == '__main__':
    codelist = ['159949']

    pool = ThreadPool(4)

    for code in codelist:
        codenow = code
        regular_investment_amount_tmp = [i for i in range(800, 1300, 200)]
        result = pool.map(process_main, regular_investment_amount_tmp)

        print '***************'
        print result
        print '***************'
    pool.close()
    pool.join()

    # annualized_interest_rate_tmp = process('510050', 0.02,  0.2,  0.16, 0.30000000000000004, 0.05, 800)
    # print annualized_interest_rate_tmp, "510050 0.02 0.2 0.16 0.30000000000000004 0.05 800"

    # annualized_interest_rate_tmp = process('159949', 0.04, 0.5, 0.02, 0.5, 0.05, 800)
    # print annualized_interest_rate_tmp, "'159949', 0.04, 0.5, 0.02, 0.5, 0.05, 800"
