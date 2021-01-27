from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp
from vnpy.gateway.futu import FutuGateway
from vnpy.gateway.alpaca import AlpacaGateway
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_backtester import CtaBacktesterApp

from vnpy.app.algo_trading import AlgoTradingApp, AlgoEngine, AlgoTemplate

from vnpy.app.chart_wizard import ChartWizardApp
from vnpy.app.data_manager import DataManagerApp
from vnpy.app.data_recorder import DataRecorderApp
from vnpy.app.excel_rtd import ExcelRtdApp
from vnpy.app.market_radar import MarketRadarApp

from vnpy.app.option_master import OptionMasterApp
from vnpy.app.option_master import OptionEngine

from vnpy.app.paper_account import PaperAccountApp
from vnpy.app.portfolio_manager import PortfolioManagerApp
from vnpy.app.risk_manager import RiskManagerApp
from vnpy.app.portfolio_strategy import PortfolioStrategyApp
from vnpy.app.rpc_service import RpcServiceApp
from vnpy.app.script_trader import ScriptTraderApp
from vnpy.app.spread_trading import SpreadTradingApp

def main():
    """Start VN Trader"""
    qapp = create_qapp()

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    # main_engine.add_gateway(AlpacaGateway)
    main_engine.add_gateway(FutuGateway)

    algoEngine = AlgoEngine(main_engine, event_engine)

    applist = [AlgoTradingApp, ChartWizardApp, DataManagerApp, DataRecorderApp, ExcelRtdApp, MarketRadarApp,
               OptionMasterApp, PaperAccountApp, PortfolioManagerApp, RiskManagerApp, PortfolioStrategyApp,
               RiskManagerApp, RpcServiceApp, ScriptTraderApp, SpreadTradingApp, CtaStrategyApp, CtaBacktesterApp]
    for i in applist:
        main_engine.add_app(i)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()

if __name__ == "__main__":
    main()