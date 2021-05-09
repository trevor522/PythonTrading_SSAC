"""
변동성돌파전략 플로우
a: 변동폭 = 전일 고가 - 전일 저가
b: 매수판단, 목표가(당일 변동폭 * k 이상 상승) 달성시 매수
c: 매도, 익일 자정

"""

import pybithumb
import time
import schedule

from privateAPI.pybitumbPrivateAPI import pybithumbPrivateAPI


class TradeLogic:
    def __init__(self, ticker):
        self.ticker = ticker
        self.target_price = pybithumb.get_current_price(self.ticker)
        self.current_price = pybithumb.get_current_price(self.ticker)

    # 매도 시도
    def sell(self):
        unit = pybithumbPrivateAPI.get_balance(self.ticker)[0]  # 보유중인 비트코인 수량
        pybithumbPrivateAPI.sell_market_order(self.ticker, unit)  # 매도

    # 매수 시도
    # 지속적으로 현가를 업데이트하면서 변동성 돌파전략에 의해 구매 타이밍을 노린다.

    # 매수기준: 당일 변동폭의 k(여기서는 0.5)배 이상 상승하면 해당 가격으로 바로 매수
    # 매도기준: 당일 종가 매도
    def buy(self):
        """
            변동성 돌파전략과 이동평균에 상승장일때만 매수주문을 체결
        """
        if (self.current_price > self.target_price) and (self.is_bull_market()):
            krw = pybithumbPrivateAPI.get_balance(self.ticker)[2]  # 보유중인 원화 조회
            order_book = pybithumb.get_orderbook(self.ticker)  # 코인 호가 정보 조회
            sell_price = order_book['asks'][0]['price']  # 최상단 매도 호가 조회 (가장 저렴하게 매수할 수 있는 가격)
            unit = krw / float(sell_price)  # 현재 잔액으로 매수 가능한 코인 갯수
            pybithumbPrivateAPI.buy_market_order(self.ticker, unit)  # 매수
            print(f"매수주문, 가격: {sell_price}, 수량: {unit}")

    # 목표가 갱신
    def update_target_price(self):
        try:
            yesterday_coinInfo = pybithumb.get_candlestick(self.ticker).iloc[-2]
            today_open = yesterday_coinInfo['close']  # 오늘 시가 = 전날 종가
            yesterday_high = yesterday_coinInfo['high']  # 전날 고가
            yesterday_low = yesterday_coinInfo['low']  # 전날 저가
            target_price = today_open + (yesterday_high - yesterday_low) * 0.5  # 목표가 = 오늘 시가 + (전날 변동폭)* 0.5
            now = time.localtime()
            print(f" {self.ticker}, 목표가 갱신 시각:",
                  "%04d/%02d/%02d %02d:%02d:%02d" % (
                      now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))

        except:
            print("목표가 갱신 실패")

        self.sell()  # 매도 시도, 변동성 돌파전략에 의해, 당일 구매한 코인이 있다면 자정에 매도한다.

    def is_bull_market(self):
        df = pybithumb.get_candlestick(self.ticker)
        close = df['close']
        ma = close.rolling(5).mean()
        return self.current_price > ma[-2]

    def execute(self):
        # 매 자정 목표가 갱신 스케쥴러
        # schedule.every().day.at("00:00").do(self.update_target_price)
        schedule.every(3).seconds.do(self.update_target_price)
        while True:
            try:
                schedule.run_pending()
                self.buy()
            except:
                pass
            time.sleep(1)


a = TradeLogic("BTC")
a.execute()
