"""
Matplotlib 플로팅 유틸리티
"""

from matplotlib.figure import Figure
import pandas as pd
import numpy as np


def plot_cumulative_returns(data: pd.DataFrame, title: str = "Strategy Performance") -> Figure:
    """
    누적 수익률 차트 생성

    Args:
        data (pd.DataFrame): 백테스트 결과 데이터
        title (str): 차트 제목

    Returns:
        Figure: matplotlib Figure 객체
    """
    figure = Figure(figsize=(12, 6))
    ax = figure.add_subplot(111)

    if 'Cumulative_Return' in data.columns:
        cumulative_return = data['Cumulative_Return']

        ax.plot(cumulative_return.index, cumulative_return.values, linewidth=2, label='Strategy')
        ax.fill_between(cumulative_return.index, cumulative_return.values, alpha=0.3)

        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Return')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        figure.autofmt_xdate()

    figure.tight_layout()
    return figure


def plot_indicators(data: pd.DataFrame, title: str = "Technical Indicators") -> Figure:
    """
    기술 지표 차트 생성

    Args:
        data (pd.DataFrame): 지표가 포함된 데이터
        title (str): 차트 제목

    Returns:
        Figure: matplotlib Figure 객체
    """
    figure = Figure(figsize=(12, 8))

    # 주가 차트
    ax1 = figure.add_subplot(3, 1, 1)
    if 'Close' in data.columns:
        ax1.plot(data.index, data['Close'], linewidth=2, label='Close Price')
        ax1.set_ylabel('Price')
        ax1.set_title(f'{title} - Close Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

    # EMA 차트
    ax2 = figure.add_subplot(3, 1, 2)
    if 'Short_EMA' in data.columns:
        ax2.plot(data.index, data['Short_EMA'], linewidth=1, label='Short EMA')
        ax2.plot(data.index, data['Long_EMA'], linewidth=1, label='Long EMA')
        ax2.set_ylabel('EMA')
        ax2.set_title('Exponential Moving Averages')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    # 거래량 차트
    ax3 = figure.add_subplot(3, 1, 3)
    if 'Volume' in data.columns:
        ax3.bar(data.index, data['Volume'], alpha=0.5, label='Volume')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Volume')
        ax3.set_title('Trading Volume')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

    figure.autofmt_xdate()
    figure.tight_layout()
    return figure


def plot_buy_sell_signals(data: pd.DataFrame, title: str = "Buy/Sell Signals") -> Figure:
    """
    매매 신호 차트 생성

    Args:
        data (pd.DataFrame): 신호가 포함된 데이터
        title (str): 차트 제목

    Returns:
        Figure: matplotlib Figure 객체
    """
    figure = Figure(figsize=(12, 6))
    ax = figure.add_subplot(111)

    if 'Close' in data.columns:
        # 주가 그리기
        ax.plot(data.index, data['Close'], linewidth=2, label='Close Price', color='black')

        # 매수 신호
        if 'Signal' in data.columns:
            buy_signals = data[data['Signal'] == 1]
            if len(buy_signals) > 0:
                ax.scatter(buy_signals.index, buy_signals['Close'],
                          color='green', marker='^', s=100, label='Buy Signal')

            # 매도 신호
            sell_signals = data[data['Signal'] == -1]
            if len(sell_signals) > 0:
                ax.scatter(sell_signals.index, sell_signals['Close'],
                          color='red', marker='v', s=100, label='Sell Signal')

        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        figure.autofmt_xdate()

    figure.tight_layout()
    return figure


def embed_plot_in_qt(figure: Figure):
    """
    matplotlib Figure를 PySide6에 임베드하기 위한 헬퍼 함수

    Args:
        figure (Figure): matplotlib Figure 객체

    Returns:
        FigureCanvas: PySide6 호환 Canvas
    """
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    return FigureCanvas(figure)
