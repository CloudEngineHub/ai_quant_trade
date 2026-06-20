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

    # === Sheet 5: 配置 ===
    ws5 = wb.create_sheet(cfg.sheets["config"])
    # 标题
    ws5["A1"] = "=== 全局配置 ==="
    ws5["A1"].font = Font(bold=True, size=14)
    # 键值对表头
    ws5["A2"] = "配置项"
    ws5["B2"] = "值"
    _style_header(ws5["A2"])
    _style_header(ws5["B2"])
    # 标量配置项
    ws5["A3"] = "刷新间隔(秒)"
    ws5["B3"] = cfg.refresh_interval
    ws5["A4"] = "预警弹窗"
    ws5["B4"] = "true" if cfg.alert_popup_enabled else "false"
    ws5["A5"] = "新闻条数"
    ws5["B5"] = cfg.news_max_rows
    ws5["A6"] = "配置重载间隔"
    ws5["B6"] = cfg.config_reload_interval

    # 空行后是列表配置
    ws5["A8"] = "=== 列表配置 ==="
    ws5["A8"].font = Font(bold=True, size=14)
    ws5["A9"] = "自选股"
    ws5["B9"] = "指数"
    _style_header(ws5["A9"])
    _style_header(ws5["B9"])
    # 写入自选股和指数列表
    max_len = max(len(cfg.watch_stocks), len(cfg.market_indices))
    for i in range(max_len):
        row = 10 + i
        if i < len(cfg.watch_stocks):
            ws5.cell(row=row, column=1, value=cfg.watch_stocks[i])
        if i < len(cfg.market_indices):
            ws5.cell(row=row, column=2, value=cfg.market_indices[i])

    ws5.column_dimensions["A"].width = 20
    ws5.column_dimensions["B"].width = 20

    wb.save(path)
    print(f"模板已生成: {path}")
    return path


if __name__ == "__main__":
    create_template()
