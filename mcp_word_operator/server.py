from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_word_operator.backup import check_file_writable, ensure_backup, list_backups, restore_from_backup
from mcp_word_operator.docx_ops import (
    add_heading,
    add_page_break,
    add_paragraph,
    add_table,
    batch_modify_paragraphs,
    delete_paragraph,
    find_text,
    insert_image,
    modify_core_properties,
    modify_header_footer,
    modify_page_margins,
    modify_page_size,
    modify_paragraph_style,
    modify_run_style,
    modify_table_cell,
    modify_table_style,
    read_document_info,
    replace_text,
)

mcp = FastMCP(
    name="Word Document Operator",
    instructions=(
        "你是一个 Word 文档操作助手。你可以读取 Word 文档信息、修改段落样式、"
        "替换文本、添加/删除段落、操作表格、修改页面设置等。"
        "每次修改操作前会自动备份原文件。如果文件被 Word/WPS 占用，会提示用户关闭后重试。"
    ),
)


def _safe_execute(func, **kwargs) -> str:
    file_path = kwargs.get("file_path")
    if file_path:
        writable_error = check_file_writable(file_path)
        if writable_error:
            return json.dumps({"success": False, "error": writable_error}, ensure_ascii=False)

        if "read" not in func.__name__ and "find" not in func.__name__:
            try:
                backup_path = ensure_backup(file_path)
            except FileNotFoundError as e:
                return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    try:
        result = func(**kwargs)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"success": False, "error": f"操作失败: {type(e).__name__}: {e}"}, ensure_ascii=False)


@mcp.tool()
def read_doc_info(file_path: str) -> str:
    """读取 Word 文档的基本信息，包括段落数、表格数、页面设置、可用样式等。用于了解文档结构后再进行修改。"""
    return _safe_execute(read_document_info, file_path=file_path)


@mcp.tool()
def modify_paragraph(
    file_path: str,
    paragraph_index: int,
    style_name: str | None = None,
    alignment: str | None = None,
    font_name: str | None = None,
    font_size: float | None = None,
    font_size_unit: str = "pt",
    bold: bool | None = None,
    italic: bool | None = None,
    underline: bool | None = None,
    font_color: str | None = None,
    line_spacing: float | None = None,
    space_before: float | None = None,
    space_after: float | None = None,
    spacing_unit: str = "pt",
    first_line_indent: float | None = None,
    first_line_indent_unit: str = "cm",
) -> str:
    """修改指定段落的样式。可设置字体、字号、加粗、斜体、对齐方式、行距、段前段后间距、首行缩进等。paragraph_index 从 0 开始。alignment 可选: left/center/right/justify。font_color 格式: #RRGGBB。"""
    return _safe_execute(
        modify_paragraph_style,
        file_path=file_path,
        paragraph_index=paragraph_index,
        style_name=style_name,
        alignment=alignment,
        font_name=font_name,
        font_size=font_size,
        font_size_unit=font_size_unit,
        bold=bold,
        italic=italic,
        underline=underline,
        font_color=font_color,
        line_spacing=line_spacing,
        space_before=space_before,
        space_after=space_after,
        spacing_unit=spacing_unit,
        first_line_indent=first_line_indent,
        first_line_indent_unit=first_line_indent_unit,
    )


@mcp.tool()
def modify_run(
    file_path: str,
    paragraph_index: int,
    run_index: int,
    font_name: str | None = None,
    font_size: float | None = None,
    font_size_unit: str = "pt",
    bold: bool | None = None,
    italic: bool | None = None,
    underline: bool | None = None,
    font_color: str | None = None,
    highlight_color: str | None = None,
) -> str:
    """修改段落中指定 Run（文本片段）的样式。Run 是 Word 中具有相同样式的连续文本。通过 read_doc_info 查看段落和 Run 索引。highlight_color 可选: yellow/green/cyan/magenta/blue/red/dark_blue/dark_cyan/dark_green/dark_magenta/dark_red/dark_yellow/dark_gray/light_gray/black。"""
    return _safe_execute(
        modify_run_style,
        file_path=file_path,
        paragraph_index=paragraph_index,
        run_index=run_index,
        font_name=font_name,
        font_size=font_size,
        font_size_unit=font_size_unit,
        bold=bold,
        italic=italic,
        underline=underline,
        font_color=font_color,
        highlight_color=highlight_color,
    )


@mcp.tool()
def replace_text_in_doc(
    file_path: str,
    old_text: str,
    new_text: str,
    match_case: bool = True,
) -> str:
    """在 Word 文档中查找并替换文本。会替换段落、表格、页眉页脚中的匹配文本。match_case 为 True 时区分大小写。"""
    return _safe_execute(
        replace_text,
        file_path=file_path,
        old_text=old_text,
        new_text=new_text,
        match_case=match_case,
    )


@mcp.tool()
def add_paragraph_to_doc(
    file_path: str,
    text: str,
    style_name: str | None = None,
    alignment: str | None = None,
    font_name: str | None = None,
    font_size: float | None = None,
    font_size_unit: str = "pt",
    bold: bool | None = None,
    italic: bool | None = None,
    font_color: str | None = None,
    insert_after_index: int | None = None,
) -> str:
    """向 Word 文档添加新段落。默认追加到文档末尾，可通过 insert_after_index 指定插入位置。alignment 可选: left/center/right/justify。font_color 格式: #RRGGBB。"""
    return _safe_execute(
        add_paragraph,
        file_path=file_path,
        text=text,
        style_name=style_name,
        alignment=alignment,
        font_name=font_name,
        font_size=font_size,
        font_size_unit=font_size_unit,
        bold=bold,
        italic=italic,
        font_color=font_color,
        insert_after_index=insert_after_index,
    )


@mcp.tool()
def delete_paragraph_from_doc(
    file_path: str,
    paragraph_index: int,
) -> str:
    """删除 Word 文档中指定索引的段落。paragraph_index 从 0 开始。删除前会自动备份。"""
    return _safe_execute(
        delete_paragraph,
        file_path=file_path,
        paragraph_index=paragraph_index,
    )


@mcp.tool()
def add_heading_to_doc(
    file_path: str,
    text: str,
    level: int = 1,
    font_name: str | None = None,
    font_size: float | None = None,
    font_size_unit: str = "pt",
    font_color: str | None = None,
) -> str:
    """向 Word 文档添加标题。level 范围 0-9，0 为文档标题，1-9 为各级标题。"""
    return _safe_execute(
        add_heading,
        file_path=file_path,
        text=text,
        level=level,
        font_name=font_name,
        font_size=font_size,
        font_size_unit=font_size_unit,
        font_color=font_color,
    )


@mcp.tool()
def batch_modify_paragraphs_in_doc(
    file_path: str,
    style_name: str | None = None,
    alignment: str | None = None,
    font_name: str | None = None,
    font_size: float | None = None,
    font_size_unit: str = "pt",
    bold: bool | None = None,
    italic: bool | None = None,
    font_color: str | None = None,
    line_spacing: float | None = None,
    space_before: float | None = None,
    space_after: float | None = None,
    spacing_unit: str = "pt",
    first_line_indent: float | None = None,
    first_line_indent_unit: str = "cm",
    paragraph_indices: list[int] | None = None,
    heading_only: bool = False,
    body_only: bool = False,
) -> str:
    """批量修改多个段落的样式。可通过 paragraph_indices 指定段落索引列表，或通过 heading_only/body_only 筛选标题段落/正文段落。不指定筛选条件则修改所有段落。"""
    return _safe_execute(
        batch_modify_paragraphs,
        file_path=file_path,
        style_name=style_name,
        alignment=alignment,
        font_name=font_name,
        font_size=font_size,
        font_size_unit=font_size_unit,
        bold=bold,
        italic=italic,
        font_color=font_color,
        line_spacing=line_spacing,
        space_before=space_before,
        space_after=space_after,
        spacing_unit=spacing_unit,
        first_line_indent=first_line_indent,
        first_line_indent_unit=first_line_indent_unit,
        paragraph_indices=paragraph_indices,
        heading_only=heading_only,
        body_only=body_only,
    )


@mcp.tool()
def modify_table_in_doc(
    file_path: str,
    table_index: int,
    style_name: str | None = None,
    alignment: str | None = None,
) -> str:
    """修改 Word 文档中表格的样式。table_index 从 0 开始。alignment 可选: left/center/right。"""
    return _safe_execute(
        modify_table_style,
        file_path=file_path,
        table_index=table_index,
        style_name=style_name,
        alignment=alignment,
    )


@mcp.tool()
def modify_table_cell_in_doc(
    file_path: str,
    table_index: int,
    row_index: int,
    col_index: int,
    text: str | None = None,
    font_name: str | None = None,
    font_size: float | None = None,
    font_size_unit: str = "pt",
    bold: bool | None = None,
    italic: bool | None = None,
    font_color: str | None = None,
    alignment: str | None = None,
) -> str:
    """修改 Word 文档中表格指定单元格的内容和样式。table_index、row_index、col_index 均从 0 开始。"""
    return _safe_execute(
        modify_table_cell,
        file_path=file_path,
        table_index=table_index,
        row_index=row_index,
        col_index=col_index,
        text=text,
        font_name=font_name,
        font_size=font_size,
        font_size_unit=font_size_unit,
        bold=bold,
        italic=italic,
        font_color=font_color,
        alignment=alignment,
    )


@mcp.tool()
def add_table_to_doc(
    file_path: str,
    rows: int,
    cols: int,
    data: list[list[str]] | None = None,
    style_name: str | None = None,
) -> str:
    """向 Word 文档添加表格。data 为二维字符串数组，按行列填充表格内容。style_name 可指定表格样式，如 'Table Grid'。"""
    return _safe_execute(
        add_table,
        file_path=file_path,
        rows=rows,
        cols=cols,
        data=data,
        style_name=style_name,
    )


@mcp.tool()
def modify_page_margins_in_doc(
    file_path: str,
    section_index: int = 0,
    top: float | None = None,
    bottom: float | None = None,
    left: float | None = None,
    right: float | None = None,
    unit: str = "cm",
) -> str:
    """修改 Word 文档的页边距。section_index 从 0 开始。unit 可选: cm/inch/pt。"""
    return _safe_execute(
        modify_page_margins,
        file_path=file_path,
        section_index=section_index,
        top=top,
        bottom=bottom,
        left=left,
        right=right,
        unit=unit,
    )


@mcp.tool()
def modify_page_size_in_doc(
    file_path: str,
    section_index: int = 0,
    width: float | None = None,
    height: float | None = None,
    unit: str = "cm",
) -> str:
    """修改 Word 文档的页面尺寸。section_index 从 0 开始。unit 可选: cm/inch/pt。A4 纸约 21cm x 29.7cm。"""
    return _safe_execute(
        modify_page_size,
        file_path=file_path,
        section_index=section_index,
        width=width,
        height=height,
        unit=unit,
    )


@mcp.tool()
def modify_header_footer_in_doc(
    file_path: str,
    section_index: int = 0,
    header_text: str | None = None,
    footer_text: str | None = None,
    header_font_name: str | None = None,
    header_font_size: float | None = None,
    header_font_size_unit: str = "pt",
    footer_font_name: str | None = None,
    footer_font_size: float | None = None,
    footer_font_size_unit: str = "pt",
) -> str:
    """修改 Word 文档的页眉页脚。section_index 从 0 开始。设置 header_text 或 footer_text 来更新对应内容。"""
    return _safe_execute(
        modify_header_footer,
        file_path=file_path,
        section_index=section_index,
        header_text=header_text,
        footer_text=footer_text,
        header_font_name=header_font_name,
        header_font_size=header_font_size,
        header_font_size_unit=header_font_size_unit,
        footer_font_name=footer_font_name,
        footer_font_size=footer_font_size,
        footer_font_size_unit=footer_font_size_unit,
    )


@mcp.tool()
def modify_doc_properties(
    file_path: str,
    title: str | None = None,
    author: str | None = None,
    subject: str | None = None,
    keywords: str | None = None,
    comments: str | None = None,
) -> str:
    """修改 Word 文档的核心属性，如标题、作者、主题、关键词、备注等。"""
    return _safe_execute(
        modify_core_properties,
        file_path=file_path,
        title=title,
        author=author,
        subject=subject,
        keywords=keywords,
        comments=comments,
    )


@mcp.tool()
def add_page_break_to_doc(
    file_path: str,
    insert_after_index: int | None = None,
) -> str:
    """向 Word 文档添加分页符。默认追加到文档末尾，可通过 insert_after_index 指定在某个段落后插入。"""
    return _safe_execute(
        add_page_break,
        file_path=file_path,
        insert_after_index=insert_after_index,
    )


@mcp.tool()
def insert_image_to_doc(
    file_path: str,
    image_path: str,
    width: float | None = None,
    height: float | None = None,
    unit: str = "cm",
) -> str:
    """向 Word 文档插入图片。image_path 为图片的本地路径。可通过 width/height 指定尺寸，unit 可选: cm/inch/pt。"""
    return _safe_execute(
        insert_image,
        file_path=file_path,
        image_path=image_path,
        width=width,
        height=height,
        unit=unit,
    )


@mcp.tool()
def find_text_in_doc(
    file_path: str,
    search_text: str,
    match_case: bool = True,
) -> str:
    """在 Word 文档中查找文本。返回匹配的段落和表格单元格的位置信息。match_case 为 True 时区分大小写。"""
    return _safe_execute(
        find_text,
        file_path=file_path,
        search_text=search_text,
        match_case=match_case,
    )


@mcp.tool()
def manage_backups(
    file_path: str,
    action: str = "list",
    backup_path: str | None = None,
) -> str:
    """管理 Word 文档的备份。action 可选: list（列出备份）/ restore（恢复备份，需指定 backup_path）。"""
    try:
        if action == "list":
            backups = list_backups(file_path)
            return json.dumps({"success": True, "backups": backups}, ensure_ascii=False)
        elif action == "restore":
            if not backup_path:
                return json.dumps({"success": False, "error": "恢复操作需要指定 backup_path"}, ensure_ascii=False)
            restored = restore_from_backup(file_path, backup_path)
            return json.dumps({"success": True, "restored_to": restored}, ensure_ascii=False)
        else:
            return json.dumps({"success": False, "error": f"未知操作: {action}，可选: list/restore"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
