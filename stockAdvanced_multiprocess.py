#!/usr/bin/python
#encoding:utf-8
import xlwt
import xlrd
import datetime
import matplotlib.pyplot as plt
import numpy
from multiprocessing.dummy import Pool as ThreadPool

def norm(list, gain=1.0):
    #normalize totalMoneyShow
    listMax = max(list)
    listMin = min(list)
    times = float(listMax - listMin)
    listNorm = []
    for i in list:
        listNorm.append(gain * (i - listMin) / times)
    return listNorm

def normWithMaxNMin(list, max, min, gain=1.0):
    #normalize totalMoneyShow
    times = float(max - min)
    listNorm = []
    for i in list:
        listNorm.append(gain * (i - min) / times)
    return listNorm

def zoomPrice(data, timesPrice=1.0):
    ret = []
    for i0 in data:
        ret.append(i0 * timesPrice)
    return ret

def process(name, buy_rate_a, buy_rate_b, sell_rate_c, sell_rate_d, regular_investment_amount):
#############################################################
#基础设定
# zhiyinzhisunbili = 0.05
# fene = 6
    # name = '159902'
    inputMoney = 50000
    fee = 0.001#交易手续费
    ZRB = 1.1**(1.0/12)-1#真融宝收益比较
    ZRBM = inputMoney
    timesM = 10000.0
    timesPrice = 1.0
    gainNorm = 0.8
    myDPI = 120
    length = 40
    width = 20

    #############################################################
    #读文件
    title = xlrd.open_workbook(name + '.xls')
    table = title.sheet_by_name('Table')
    #写文件
    wb = xlwt.Workbook(encoding='utf-8')
    sheet1 = wb.add_sheet('result',cell_overwrite_ok=True)
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
    flag = []
    flag60 = []
    #第一步：判断当天收盘价是否高于20日线
    sheet1.write(20, 0, 'date')
    sheet1.write(20, 1, 'price')
    sheet1.write(20, 2, 'limit')
    sheet1.write(20, 3, 'MA20')
    sheet1.write(20, 4, 'price>MA20?')

    sheet1.write(20, 5, 'stockNum')
    sheet1.write(20, 6, 'stockMoney')
    sheet1.write(20, 7, 'restMoney')
    sheet1.write(20, 8, 'savedMoney')
    sheet1.write(20, 9, 'totalMoney')
    sheet1.write(20, 10, 'ZRBM')
    sheet1.write(20, 11, 'stockNum1')
    sheet1.write(20, 12, 'stockMoney1')
    sheet1.write(20, 13, 'restMoney1')
    sheet1.write(20, 14, 'totalMoney1')

    sheet1.write(20, 15, 'MA60')
    sheet1.write(20, 16, 'price>MA60?')
    sheet1.write(20, 17, '投入金额')

    #初始化flag为-1
    for i in range(0, len(price)):
        flag.append(-1)

    for i in range(0, len(price)):
        flag60.append(-1)

    dateShow = []
    priceShow = []
    buyShow = []
    buyDateShow = []
    sellShow = []
    sellDateShow = []
    MA20Show = []
    MA60Show = []
    totalMoneyShow = []
    costShow = []
    totalMoneyStupidShow = []
    totalMoneyZRBShow = []

    for i in range(21, len(price)):
        #每20个price组成一个temp数组
        tmplist = price[i-20:i]
        #print tmplist
        sheet1.write(i, 0, datetime.datetime.strptime(date[i][0:10], '%Y-%m-%d').strftime('%Y-%m-%d'))
        sheet1.write(i, 1, price[i])
        sheet1.write(i, 2, limit[i])
        dateShow.append(datetime.datetime.strptime(date[i][0:10], '%Y-%m-%d').date())
        priceShow.append(price[i])
        # buyShow.append(0)
        # sellShow.append(0)
        #print tmplist
        MA20 = sum(tmplist)/20.0
        MA20Show.append(MA20)

        if(MA20 < price[i]):
            flag[i] = 0
        else:
            flag[i] = 1
        sheet1.write(i, 3, MA20)
        sheet1.write(i, 4, flag[i])

        sheet1.write(i, 15, 0)
        sheet1.write(i, 16, 0)


    for i in range(201, len(price)):
        #每20个price组成一个temp数组
        tmplist = price[i-60:i]
        #print tmplist
        #print tmplist
        MA60 = sum(tmplist)/60.0
        MA60Show.append(MA60)

        if(MA60 < price[i]):
            flag60[i] = 0
        else:
            flag60[i] = 1
        sheet1.write(i, 15, MA60)
        sheet1.write(i, 16, flag60[i])




    #开始投资
    tmpMonth = date[21][5:7]#初始月份

    stockNum = 0
    stockMoney = 0
    restMoney = inputMoney
    savedMoney = 0
    sellShow.append(priceShow[0])
    sellDateShow.append(dateShow[0])
    totalMoney = stockMoney + restMoney + savedMoney
    cost = inputMoney
    sheet1.write(21, 5, stockNum)
    sheet1.write(21, 6, stockMoney)
    sheet1.write(21, 7, restMoney)
    sheet1.write(21, 8, savedMoney)
    sheet1.write(21, 9, totalMoney)
    costShow.append(cost/timesM)
    totalMoneyShow.append(totalMoney/timesM)


    #无脑投初始状态
    stockNum1 = int(inputMoney/(1+fee) / price[21] / 100) * 100
    stockMoney1 = stockNum1 * price[21]
    restMoney1 = inputMoney - stockMoney1 - stockMoney1 * fee
    totalMoney1 = stockMoney1 + restMoney1
    totalMoneyStupidShow.append(totalMoney1/timesM)

    totalMoneyZRBShow.append(ZRBM/timesM)

    average_cost = 0
    highest_recent = price[22]

    #开始循环投资
    for i in range(22, len(flag)):
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
            sheet1.write(i, 10, ZRBM)
            #无脑定投
            tmpStockNum1 = int((regular_investment_amount + restMoney1)/(1+fee) / price[i] / 100) * 100
            if tmpStockNum1 != 0:#够买一份了，那就买买买
                stockNum1 += tmpStockNum1
                stockMoney1 += (tmpStockNum1 * price[i])
                restMoney1 = restMoney1 + regular_investment_amount - tmpStockNum1 * price[i] - tmpStockNum1 * price[i] * fee
                buyShow.append(price[i])
                buyDateShow.append(datetime.datetime.strptime(date[i][0:10], '%Y-%m-%d').date())
            else:
                restMoney1 += regular_investment_amount
        sheet1.write(i, 11, stockNum1)
        sheet1.write(i, 12, stockMoney1)
        sheet1.write(i, 13, restMoney1)
        totalMoney1 = stockMoney1 + restMoney1
        sheet1.write(i, 14, totalMoney1)
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

                buyShow.append(price[i])
                buyDateShow.append(datetime.datetime.strptime(date[i][0:10], '%Y-%m-%d').date())
        elif price[i] < highest_recent * (1 - sell_rate_c) and stockNum > 0:
            tmpStockNum = stockNum * sell_rate_d

            restMoney += (price[i] * tmpStockNum * (1 - fee))
            stockNum = stockNum - tmpStockNum
            stockMoney = price[i] * stockNum

            sellShow.append(price[i])
            sellDateShow.append(datetime.datetime.strptime(date[i][0:10], '%Y-%m-%d').date())

        # print('stockNum %d totalMoney %d restMoney %d' % (stockNum, totalMoney, restMoney))
        sheet1.write(i, 5, stockNum)
        sheet1.write(i, 6, stockMoney)
        sheet1.write(i, 7, restMoney)
        sheet1.write(i, 8, savedMoney)
        totalMoney = stockMoney + restMoney + savedMoney
        sheet1.write(i, 9, totalMoney)
        costShow.append(cost/timesM)
        totalMoneyShow.append(totalMoney/timesM)
        totalMoneyStupidShow.append(totalMoney1/timesM)
        totalMoneyZRBShow.append(ZRBM/timesM)



    daysPast = datetime.datetime.strptime(date[-1][0:10], '%Y-%m-%d') - \
                        datetime.datetime.strptime(date[1][0:10], '%Y-%m-%d')

    AnnualInterestRate = ((totalMoney / float(cost)) ** (1 / (float(daysPast.days) / 365.0)) - 1) * 100

    # out = "从%s到%s，购买%s的天数为%s天(共%s年)，初始资金%d，每月定投%d，最后总投入为%d。同期定投真融宝(年化收益0.1)得到%d。" \
    #       % (str(date[1][0:10]), str(date[-1][0:10]), name, str(daysPast), str(daysPast.days/365.0), inputMoney, regular_investment_amount, cost, ZRBM)
    # out0 = "20日线定投基金最终得到%d。年化收益率%f" % (totalMoney, AnnualInterestRate) + '%'
    # out1 = "无脑月初定投%d，最终得到%d。" \
    #       % (regular_investment_amount, totalMoney1)
    # out00 = "交易规则：初始资金%d，每月定投%d，每天检查，如果当天价格在二十日线以上，\
    # 再判断剩余的钱是否足够买100股以上，足够的话，买买买。当天价格在二十日线以下就全仓卖掉" % (inputMoney, regular_investment_amount)
    # sheet1.write(0, 0, out)
    # sheet1.write(1, 0, out0)
    # sheet1.write(2, 0, out1)
    # sheet1.write(3, 0, out00)

    # for i in range(1, len(totalMoneyShow)):
    #     tr = totalMoneyShow[i] / totalMoneyShow[i-1]
    #     if tr < 0.95:
    #         print 'Big Fall!'
    #         print dateShow[i], tr

    # print out.decode('utf-8')
    # print out0.decode('utf-8')
    # print out1.decode('utf-8')
    # print '\n\n', dateShow
    # fig = plt.figure(figsize=(length, width), dpi=myDPI)
    # plt.title(name)
    # plt.xlabel('time')
    # plt.ylabel('data')
    # plt.grid(True)
    # upLimit = max([max(priceShow), max(totalMoneyShow), max(costShow)])
    # downLimit = min([min(priceShow), min(totalMoneyShow), min(costShow)])
    # plt.ylim(downLimit, upLimit)
    # plt.plot_date(dateShow, zoomPrice(priceShow, timesPrice), 'b-', label='Daily Closing Price')
    # plt.plot_date(dateShow, zoomPrice(MA20Show, timesPrice), 'k--', label='MA20', linewidth=2)
    # plt.scatter(buyDateShow, zoomPrice(buyShow, timesPrice), s=80, label='Buy', c='red', marker='*')
    # plt.scatter(sellDateShow, zoomPrice(sellShow, timesPrice), s=100, label='Sell', c='yellow', marker='.')
    # plt.plot_date(dateShow, costShow, 'c--', label='Cost(w)', linewidth=1)
    # plt.plot_date(dateShow, totalMoneyShow, 'm-', label='TotalMoney(w)', linewidth=2)
    # plt.plot_date(dateShow, totalMoneyStupidShow, 'g:', label='TotalMoneyStupid(w)', linewidth=2)
    # plt.plot_date(dateShow, totalMoneyZRBShow, 'k--', label='TotalMoneyZRB(w)', linewidth=1)
    # #plt.plot_date(dateShow, buyShow)
    #
    # #plt.plot_date(dateShow, sellShow)
    # plt.legend(numpoints=1, fontsize=18)
    # #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))matplotlib.pyplot.figure
    # plt.legend(loc='upper left')
    # #plt.show()
    # plt.savefig(name + '.png')
    #
    # fig1 = plt.figure(figsize=(length, width), dpi=myDPI)
    # plt.title(name + '(Norm)(price*%.1f)' % round(gainNorm,1))
    # plt.xlabel('time')
    # plt.ylabel('data')
    # plt.grid(True)
    # priceShowNorm = norm(priceShow, gainNorm)
    # MA20ShowNorm = norm(MA20Show, gainNorm)
    # MA60ShowNorm = norm(MA60Show, gainNorm)
    # buyShowNorm = normWithMaxNMin(buyShow, max(priceShow), min(priceShow), gainNorm)
    # sellShowNorm = normWithMaxNMin(sellShow, max(priceShow), min(priceShow), gainNorm)
    # totalMoneyShowNorm = norm(totalMoneyShow)
    # costShowNorm = normWithMaxNMin(costShow, max(totalMoneyShow), min(totalMoneyShow))
    # totalMoneyStupidShowNorm = normWithMaxNMin(totalMoneyStupidShow, max(totalMoneyShow), min(totalMoneyShow))
    # totalMoneyZRBShowNorm = normWithMaxNMin(totalMoneyZRBShow, max(totalMoneyShow), min(totalMoneyShow))
    # # plt.ylim(downLimit, upLimit)
    # plt.plot_date(dateShow, priceShowNorm, 'b-', label='Daily Closing Price')
    # plt.plot_date(dateShow, MA20ShowNorm, 'k--', label='MA20', linewidth=2)
    # plt.scatter(buyDateShow, buyShowNorm, s=80, label='Buy', c='red', marker='*')
    # plt.plot_date(dateShow, costShowNorm, 'c--', label='Cost', linewidth=2)
    # plt.plot_date(dateShow, totalMoneyShowNorm, 'm-', label='TotalMoney', linewidth=1)
    # plt.plot_date(dateShow, totalMoneyStupidShowNorm, 'g:', label='TotalMoneyStupid(w)', linewidth=2)
    # plt.plot_date(dateShow, totalMoneyZRBShowNorm, 'k--', label='TotalMoneyZRB(w)', linewidth=1)
    # plt.scatter(sellDateShow, sellShowNorm, s=100, label='Sell', c='yellow', marker='.')
    # #plt.plot_date(dateShow, sellShow)
    # plt.legend(numpoints=1, fontsize=18)
    # #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.legend(loc='upper left')
    # plt.savefig(name + 'Norm_priceX%.1f.png'%gainNorm)
    #plt.show()
    # wb.save(name + '_' + str(datetime.datetime.now().strftime('%d_%H_evan_dingbuzhiyin')) + '.xls')

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
                        annualized_interest_rate_tmp = process('000001', buy_rate_a_tmp, buy_rate_b_tmp,
                                                               sell_rate_c_tmp, sell_rate_d_tmp,
                                                               regular_investment_amount_tmp)
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

    pool = ThreadPool()

    for code in codelist:
        regular_investment_amount_tmp = [i for i in range(200, 2000, 200)]
        result = pool.map(process_main, regular_investment_amount_tmp)

        print '***************'
        print result
        print '***************'
    pool.close()
    pool.join()
    # nianlilvtemp = process('159902', 0.05, 6)