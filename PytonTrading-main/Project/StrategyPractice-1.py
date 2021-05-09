
import sys
import pybithumb
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from privateAPI.pybitumbPrivateAPI import pybithumbPrivateAPI

tickers = pybithumb.get_tickers()[:5]
form = uic.loadUiType("../res/week5-1.ui")[0]


class StrategyPractice(QMainWindow, form):
    def __init__(self):
        super(StrategyPractice, self).__init__()
        # ui 파일을 적용
        self.setupUi(self)
        # 테이블 행 사이즈를 지정
        self.twCoins.setRowCount(len(tickers))
        # 자동매매 버튼
        self.pbStartTrade.clicked.connect(self.start_trade)


        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.timeout)

    def get_marget_info(self, ticker):
        # [코인명, 현재가, 5일 이동평균, 상승장 여부, 보유량]
        currentPrice = pybithumb.get_current_price(ticker)  # 코인 현재가
        tickerInfo = pybithumb.get_candlestick(ticker)  # 자정 기준 코인 정보
        tickerClosePrice = tickerInfo['close']  # 종가 컬럼
        tickerMA = tickerClosePrice.rolling(5).mean()[-2]  # 종가 컬럼을 이용한 5일간의 이동평균

        if currentPrice > tickerMA:  # 현재 코인의 가격이 5일 이동평균 이상이라면 상승장이라고 판단한다.
            marketState = "Bull Market"
        else:
            marketState = "Bear Market"

        reserve = pybithumbPrivateAPI.get_balance(ticker)[0]  # 현재 보유중인 코인의 수량
        reserve = format(reserve, ".8f")

        result = [ticker, currentPrice, tickerMA, marketState, reserve]
        return result

    def timeout(self):
        # 반복적으로 테이블 내용을 업데이트 합니다.
        for i, ticker in enumerate(tickers):
            marketInfo = self.get_marget_info(ticker)
            for j in range(len(marketInfo)):
                self.twCoins.setItem(i, j, QTableWidgetItem(str(marketInfo[j])))

    def start_trade(self):
        """추후 로직을 적용"""
        pass


app = QApplication(sys.argv)
window = StrategyPractice()
window.show()
app.exec_()
