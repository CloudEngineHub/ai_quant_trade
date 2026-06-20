# -*- coding: utf-8 -*-
"""Excel 管理器：封装 xlwings 工作簿操作"""
import os
import logging
from typing import Optional, Tuple

import xlwings as xw
import pandas as pd


class ExcelManager:
    """管理 Excel 工作簿的打开、读写"""

    def __init__(self, xlsx_path: str):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._xlsx_path = xlsx_path

        if not os.path.exists(xlsx_path):
            raise FileNotFoundError(f"Excel 文件不存在: {xlsx_path}")

        self.wb = xw.Book(xlsx_path)
        self._logger.info(f"已打开 Excel: {xlsx_path}")

    def get_sheet_by_name(self, name: str) -> Optional[xw.Sheet]:
        """按名称获取 Sheet"""
        try:
            return self.wb.sheets[name]
        except Exception:
            self._logger.warning(f"Sheet 不存在: {name}")
            return None

    def sheet_to_df(self, sheet: xw.Sheet) -> Tuple[pd.DataFrame, int, int]:
        """将 Sheet 转为 DataFrame，返回 (df, row_num, col_num)"""
        row_num = sheet.api.UsedRange.Rows.count
        col_num = sheet.api.UsedRange.Columns.count

        if row_num <= 1 and col_num <= 1:
            val = sheet.range((1, 1)).value
            if val is None:
                return pd.DataFrame(), 0, 0

        df = sheet.range(
            (1, 1), (row_num, col_num)
        ).options(pd.DataFrame, headers=True, index=False).value

        if df is None:
            return pd.DataFrame(), 0, 0

        return df, row_num, col_num

    def write_df(self, sheet: xw.Sheet, df: pd.DataFrame,
                 start_row: int = 1, start_col: int = 1):
        """将 DataFrame 写入 Sheet"""
        if df is None or df.empty:
            self._logger.debug(f"写入空数据，跳过: {sheet.name}")
            return

        n_rows = df.shape[0]
        n_cols = df.shape[1]
        # 写入列名 + 数据（共 n_rows+1 行）
        sheet.range(
            (start_row, start_col),
            (start_row + n_rows, start_col + n_cols - 1)
        ).value = df

    def clear_range(self, sheet: xw.Sheet, start_row: int = 1,
                    start_col: int = 1, end_row: int = 200, end_col: int = 50):
        """清除指定区域内容"""
        sheet.range((start_row, start_col), (end_row, end_col)).clear_contents()

    def highlight_row(self, sheet: xw.Sheet, row: int,
                      start_col: int = 1, end_col: int = 20,
                      color: tuple = (255, 200, 200)):
        """高亮整行（默认浅红色背景）"""
        rng = sheet.range((row, start_col), (row, end_col))
        rng.color = color

    def clear_highlight(self, sheet: xw.Sheet, start_row: int = 1,
                        end_row: int = 200, start_col: int = 1, end_col: int = 20):
        """清除高亮格式"""
        rng = sheet.range((start_row, start_col), (end_row, end_col))
        rng.color = None

    def add_button(self, sheet: xw.Sheet, row: int, col: int,
                   text: str, macro: str, width: int = 100, height: int = 30):
        """在 Sheet 中添加按钮，绑定宏

        Args:
            sheet: 目标 Sheet
            row, col: 按钮左上角位置（行、列，从1开始）
            text: 按钮显示文字
            macro: 绑定的宏名称（VBA 函数名）
            width: 按钮宽度（像素）
            height: 按钮高度（像素）
        """
        try:
            left = sheet.cells(row, col).left
            top = sheet.cells(row, col).top
            button = sheet.shapes.add_button(
                left=left, top=top, width=width, height=height
            )
            button.text = text
            button.on_action = macro
            self._logger.info(f"按钮已添加: {text} -> {macro}")
            return button
        except Exception as e:
            self._logger.error(f"添加按钮失败: {e}")
            return None

    def insert_image(self, sheet: xw.Sheet, image_path: str,
                     row: int = 1, col: int = 1,
                     width: int = 600, height: int = 350):
        """在 Sheet 中插入图片

        Args:
            sheet: 目标 Sheet
            image_path: 图片文件路径
            row, col: 插入位置（行、列，从1开始）
            width: 图片宽度（像素）
            height: 图片高度（像素）
        """
        try:
            # 先清除该位置已有的图片（避免叠加）
            self.clear_images_in_range(sheet, row, col, row + 20, col + 10)

            anchor = sheet.cells(row, col)
            pic = sheet.pictures.add(
                image_path, left=anchor.left, top=anchor.top,
                width=width, height=height
            )
            self._logger.info(f"图片已插入: {image_path} -> 行{row}列{col}")
            return pic
        except Exception as e:
            self._logger.error(f"插入图片失败: {e}")
            return None

    def clear_images_in_range(self, sheet: xw.Sheet,
                              start_row: int, start_col: int,
                              end_row: int, end_col: int):
        """清除指定区域内的图片"""
        try:
            left = sheet.cells(start_row, start_col).left
            top = sheet.cells(start_row, start_col).top
            right = sheet.cells(end_row, end_col).left
            bottom = sheet.cells(end_row, end_col).top

            for pic in list(sheet.pictures):
                if (pic.left >= left and pic.top >= top and
                        pic.left < right and pic.top < bottom):
                    pic.delete()
                    self._logger.debug(f"已删除图片: {pic.name}")
        except Exception as e:
            self._logger.debug(f"清除图片时: {e}")

    def get_cell_value(self, sheet: xw.Sheet, row: int, col: int):
        """获取单元格值"""
        return sheet.cells(row, col).value

    def close(self):
        """关闭工作簿"""
        try:
            self.wb.close()
        except Exception as e:
            self._logger.error(f"关闭 Excel 失败: {e}")
