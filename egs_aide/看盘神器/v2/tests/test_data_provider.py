# -*- coding: utf-8 -*-
"""DataProvider 纯逻辑方法测试"""
import pandas as pd

from excel_monitor.core.data_provider import DataProvider


def test_clean_stock_code_removes_postfix():
    """测试去除代码后缀 (.SZ / .SH)"""
    dp = DataProvider()
    assert dp.clean_code("000001.SZ") == "000001"
    assert dp.clean_code("600000.SH") == "600000"
    assert dp.clean_code("300001") == "300001"


def test_filter_columns():
    """测试按指定列过滤 DataFrame"""
    dp = DataProvider()
    df = pd.DataFrame({
        "代码": ["000001"], "名称": ["平安银行"],
        "最新": [10.5], "涨幅": [2.3], "多余列": [0],
    })
    result = dp.filter_columns(df, ["代码", "名称", "最新", "涨幅"])
    assert list(result.columns) == ["代码", "名称", "最新", "涨幅"]
    assert "多余列" not in result.columns


def test_rename_columns():
    """测试列名重命名映射"""
    dp = DataProvider()
    df = pd.DataFrame({"最新": [10.5], "涨幅": [2.3]})
    result = dp.rename_columns(df, {"最新": "最新价", "涨幅": "涨跌幅"})
    assert "最新价" in result.columns
    assert "涨跌幅" in result.columns
