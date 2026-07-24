"""
PDF 리포트 생성 유틸리티

백테스트 결과(성능 지표 요약 + 차트들)를 여러 페이지로 구성된 PDF로
내보낸다. matplotlib의 PdfPages를 사용하므로 별도 의존성이 필요 없다.
"""

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
import pandas as pd

from .plotting import (
    plot_cumulative_returns,
    plot_indicators,
    plot_buy_sell_signals,
)


# (지표 키, 표시 라벨, 포맷 함수)
# 라벨은 영문 사용 — matplotlib 기본 폰트(DejaVu Sans)에 한글 글리프가 없어
# PDF에서 한글이 깨지기 때문. 배포 .exe 환경에서도 안전하게 렌더링된다.
_METRIC_ROWS = [
    ('cagr', 'CAGR (Annual Growth)', lambda v: f"{v:.2%}"),
    ('sharpe_ratio', 'Sharpe Ratio', lambda v: f"{v:.2f}"),
    ('max_drawdown', 'Max Drawdown (MDD)', lambda v: f"{v:.2%}"),
    ('calmar_ratio', 'Calmar Ratio', lambda v: f"{v:.2f}"),
    ('win_rate', 'Win Rate', lambda v: f"{v:.2%}"),
    ('profit_loss_ratio', 'Profit/Loss Ratio', lambda v: f"{v:.2f}"),
    ('total_trades', 'Total Trades', lambda v: str(int(v))),
    ('winning_trades', 'Winning Trades', lambda v: str(int(v))),
    ('losing_trades', 'Losing Trades', lambda v: str(int(v))),
    ('avg_holding_period', 'Avg Holding Period (days)', lambda v: f"{v:.1f}"),
]


def _build_summary_figure(metrics: dict, strategy_name: str, params: dict) -> Figure:
    """지표 요약 표를 담은 첫 페이지 Figure 생성.

    한글 폰트가 없는 환경에서도 깨지지 않도록 ASCII 라벨을 함께 표기한다.
    """
    fig = Figure(figsize=(8.27, 11.69))  # A4 세로
    ax = fig.add_subplot(111)
    ax.axis('off')

    ax.text(0.5, 0.97, "QuantInvest Tool - Backtest Report",
            ha='center', va='top', fontsize=18, fontweight='bold',
            transform=ax.transAxes)
    ax.text(0.5, 0.93, f"Strategy: {strategy_name}",
            ha='center', va='top', fontsize=12, transform=ax.transAxes)

    # 파라미터 요약
    if params:
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        ax.text(0.5, 0.90, f"Parameters: {param_str}",
                ha='center', va='top', fontsize=9, transform=ax.transAxes)

    # 지표 표 데이터
    cell_text = []
    for key, label, fmt in _METRIC_ROWS:
        if key in metrics:
            try:
                value = fmt(metrics[key])
            except (TypeError, ValueError):
                value = str(metrics[key])
        else:
            value = "-"
        cell_text.append([label, value])

    table = ax.table(
        cellText=cell_text,
        colLabels=["Metric", "Value"],
        colWidths=[0.6, 0.3],
        cellLoc='left',
        loc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.0, 1.8)

    # 헤더 스타일
    for col in range(2):
        header_cell = table[0, col]
        header_cell.set_facecolor('#0d47a1')
        header_cell.set_text_props(color='white', fontweight='bold')

    return fig


def export_backtest_pdf(result: dict, output_path: str,
                        strategy_name: str = "Strategy") -> str:
    """백테스트 결과를 다중 페이지 PDF로 내보낸다.

    Args:
        result (dict): BacktestEngine.run_strategy 결과
                       ({'data': DataFrame, 'metrics': dict, 'strategy': obj})
        output_path (str): 저장 경로 (.pdf)
        strategy_name (str): 리포트에 표기할 전략 이름

    Returns:
        str: 저장된 파일 경로

    Raises:
        ValueError: result가 유효하지 않을 때
    """
    if not result or 'data' not in result or 'metrics' not in result:
        raise ValueError("유효한 백테스트 결과가 없습니다. 백테스트를 먼저 실행하세요.")

    data: pd.DataFrame = result['data']
    metrics: dict = result['metrics']
    strategy_obj = result.get('strategy')
    params = getattr(strategy_obj, 'params', {}) if strategy_obj else {}

    with PdfPages(output_path) as pdf:
        # 1페이지: 지표 요약
        summary_fig = _build_summary_figure(metrics, strategy_name, params)
        pdf.savefig(summary_fig)

        # 2~4페이지: 차트 (데이터에 해당 열이 있을 때만)
        for plot_fn, title in [
            (plot_cumulative_returns, "Cumulative Returns"),
            (plot_indicators, "Technical Indicators"),
            (plot_buy_sell_signals, "Buy/Sell Signals"),
        ]:
            try:
                fig = plot_fn(data, f"{strategy_name} - {title}")
                pdf.savefig(fig)
            except Exception:
                # 특정 차트 생성 실패 시 해당 페이지만 건너뜀 (리포트는 계속 생성)
                continue

    return output_path
