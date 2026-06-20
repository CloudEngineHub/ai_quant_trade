# -*- coding: utf-8 -*-
"""生成 Excel 看盘模板（使用 openpyxl）

运行: python -m excel_monitor.utils.template_generator
或通过 main.py 自动调用
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from excel_monitor.config_loader import AppConfig


def _style_header(cell):
    """设置表头样式"""
    cell.font = Font(bold=True, size=11, color="FFFFFF")
    cell.fill = PatternFill(start_color="4472C4", end_color="4472C4",
                            fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")
    thin = Side(border_style="thin", color="CCCCCC")
    cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)


def create_template(output_path: str = None, config: AppConfig = None):
    """生成 Excel 模板

    Args:
        output_path: 输出路径，默认使用 config.excel_template
        config: 配置对象，默认使用 AppConfig()
    """
    cfg = config or AppConfig()
    path = output_path or os.path.join(os.getcwd(), cfg.excel_template)

    wb = Workbook()

    # === Sheet 1: 大盘 ===
    ws1 = wb.active
    ws1.title = cfg.sheets["market_overview"]
    ws1["A1"] = "=== 大盘总览（自动刷新）==="
    ws1["A1"].font = Font(bold=True, size=14)

    # === Sheet 2: 详细行情 ===
    ws2 = wb.create_sheet(cfg.sheets["detailed_quotes"])
    ws2["A1"] = "代码"
    ws2["B1"] = "名称"
    _style_header(ws2["A1"])
    _style_header(ws2["B1"])
    # 示例自选股
    ws2["A2"] = "中国平安"
    ws2["B2"] = "中国平安"
    ws2["A3"] = "贵州茅台"
    ws2["B3"] = "贵州茅台"

    # === Sheet 3: 新闻 ===
    ws3 = wb.create_sheet(cfg.sheets["news"])
    ws3["A1"] = "=== 财经新闻（自动刷新）==="
    ws3["A1"].font = Font(bold=True, size=14)

    # === Sheet 4: 个性定制看盘 ===
    ws4 = wb.create_sheet(cfg.sheets["custom_watch"])
    # 写入数据列表头
    headers = cfg.custom_watch_columns
    for col_idx, header in enumerate(headers, 1):
        cell = ws4.cell(row=1, column=col_idx, value=header)
        _style_header(cell)
    # 写入预警条件列表头（紧挨数据列右侧，用橙色区分）
    alert_headers = cfg.alert_columns
    alert_start_col = len(headers) + 1
    for i, header in enumerate(alert_headers):
        cell = ws4.cell(row=1, column=alert_start_col + i, value=header)
        cell.font = Font(bold=True, size=11, color="FFFFFF")
        cell.fill = PatternFill(start_color="ED7D31", end_color="ED7D31",
                                fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        thin = Side(border_style="thin", color="CCCCCC")
        cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    # 示例自选股
    ws4["A2"] = "中国平安"
    ws4["B2"] = "中国平安"
    # 示例预警条件：涨跌幅上限 5%，价格下限 40
    ws4.cell(row=2, column=alert_start_col + 1, value=5.0)   # 涨跌幅上限
    ws4.cell(row=2, column=alert_start_col + 2, value=40.0)  # 价格下限
    ws4["A3"] = "贵州茅台"
    ws4["B3"] = "贵州茅台"
    # 示例预警条件：价格上限 2000
    ws4.cell(row=3, column=alert_start_col + 3, value=2000.0)  # 价格上限

    # 设置列宽
    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 15

    wb.save(path)
    print(f"模板已生成: {path}")
    return path


if __name__ == "__main__":
    create_template()
