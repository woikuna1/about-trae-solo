#!/root/.pyenv/versions/3.11.15/bin/python3
# -*- coding: utf-8 -*-
"""STEP文件分析工具 - 解析STEP文件并生成Word分析报告"""

import argparse
import os
import sys
import math

from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import (
    TopAbs_VERTEX, TopAbs_EDGE, TopAbs_WIRE, TopAbs_FACE,
    TopAbs_SHELL, TopAbs_SOLID
)
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.GeomAbs import (
    GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Sphere,
    GeomAbs_Torus, GeomAbs_BSplineSurface, GeomAbs_BezierSurface,
    GeomAbs_SurfaceOfRevolution, GeomAbs_SurfaceOfExtrusion, GeomAbs_OtherSurface,
    GeomAbs_Line, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Hyperbola,
    GeomAbs_Parabola, GeomAbs_BezierCurve, GeomAbs_BSplineCurve, GeomAbs_OtherCurve
)
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Vec

from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


# ============================================================
# 几何类型名称映射
# ============================================================
FACE_TYPE_NAMES = {
    GeomAbs_Plane: "平面",
    GeomAbs_Cylinder: "圆柱面",
    GeomAbs_Cone: "圆锥面",
    GeomAbs_Sphere: "球面",
    GeomAbs_Torus: "环面",
    GeomAbs_BSplineSurface: "B样条曲面",
    GeomAbs_BezierSurface: "贝塞尔曲面",
    GeomAbs_SurfaceOfRevolution: "旋转曲面",
    GeomAbs_SurfaceOfExtrusion: "拉伸曲面",
    GeomAbs_OtherSurface: "其他曲面",
}

EDGE_TYPE_NAMES = {
    GeomAbs_Line: "直线",
    GeomAbs_Circle: "圆",
    GeomAbs_Ellipse: "椭圆",
    GeomAbs_Hyperbola: "双曲线",
    GeomAbs_Parabola: "抛物线",
    GeomAbs_BezierCurve: "贝塞尔曲线",
    GeomAbs_BSplineCurve: "B样条曲线",
    GeomAbs_OtherCurve: "其他曲线",
}


# ============================================================
# STEP文件读取
# ============================================================
def read_step_file(filepath):
    """读取STEP文件，返回TopoDS_Shape"""
    reader = STEPControl_Reader()
    status = reader.ReadFile(filepath)
    if status != 1:  # IFSelect_RetDone
        return None
    reader.TransferRoots()
    return reader.OneShape()


# ============================================================
# 拓扑信息统计
# ============================================================
def count_topology(shape):
    """统计顶点、边、线、面、壳、实体数量"""
    counts = {}
    for name, topo_type in [
        ("顶点", TopAbs_VERTEX),
        ("边", TopAbs_EDGE),
        ("线", TopAbs_WIRE),
        ("面", TopAbs_FACE),
        ("壳", TopAbs_SHELL),
        ("实体", TopAbs_SOLID),
    ]:
        exp = TopExp_Explorer(shape, topo_type)
        count = 0
        while exp.More():
            count += 1
            exp.Next()
        counts[name] = count
    return counts


# ============================================================
# 几何类型统计
# ============================================================
def count_face_types(shape):
    """统计各面类型数量"""
    type_counts = {}
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        adaptor = BRepAdaptor_Surface(face)
        t = adaptor.GetType()
        name = FACE_TYPE_NAMES.get(t, f"未知({t})")
        type_counts[name] = type_counts.get(name, 0) + 1
        exp.Next()
    return type_counts


def count_edge_types(shape):
    """统计各边类型数量"""
    type_counts = {}
    exp = TopExp_Explorer(shape, TopAbs_EDGE)
    while exp.More():
        edge = TopoDS.Edge_s(exp.Current())
        adaptor = BRepAdaptor_Curve(edge)
        t = adaptor.GetType()
        name = EDGE_TYPE_NAMES.get(t, f"未知({t})")
        type_counts[name] = type_counts.get(name, 0) + 1
        exp.Next()
    return type_counts


# ============================================================
# 尺寸信息
# ============================================================
def get_bounding_box(shape):
    """获取包围盒"""
    bbox = Bnd_Box()
    BRepBndLib.Add_s(shape, bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    return {
        "x_min": xmin, "x_max": xmax, "x_size": xmax - xmin,
        "y_min": ymin, "y_max": ymax, "y_size": ymax - ymin,
        "z_min": zmin, "z_max": zmax, "z_size": zmax - zmin,
    }


def get_volume(shape):
    """获取体积"""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass(), props.CentreOfMass()


def get_surface_area(shape):
    """获取表面积"""
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


# ============================================================
# 孔特征分析
# ============================================================
def analyze_holes(shape):
    """分析孔特征"""
    holes = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        adaptor = BRepAdaptor_Surface(face)
        surf_type = adaptor.GetType()

        # 统计面内的线数量
        wire_exp = TopExp_Explorer(face, TopAbs_WIRE)
        wire_count = 0
        while wire_exp.More():
            wire_count += 1
            wire_exp.Next()

        # 孔面条件：圆柱面/圆锥面且有内线(wire_count > 1)，或平面有内线
        is_hole_face = False
        if surf_type in (GeomAbs_Cylinder, GeomAbs_Cone) and wire_count > 1:
            is_hole_face = True
        elif surf_type == GeomAbs_Plane and wire_count > 1:
            is_hole_face = True

        if not is_hole_face:
            exp.Next()
            continue

        # 分析每条内线的边类型
        wire_exp = TopExp_Explorer(face, TopAbs_WIRE)
        wire_idx = 0
        inner_wires_data = []  # [(edge_types_list, [edge_adaptor_list]), ...]
        while wire_exp.More():
            if wire_idx > 0:  # 内线
                wire = wire_exp.Current()
                edge_exp = TopExp_Explorer(wire, TopAbs_EDGE)
                edge_types = []
                edge_adaptors = []
                while edge_exp.More():
                    edge = TopoDS.Edge_s(edge_exp.Current())
                    curve_adaptor = BRepAdaptor_Curve(edge)
                    edge_types.append(curve_adaptor.GetType())
                    edge_adaptors.append(curve_adaptor)
                    edge_exp.Next()
                inner_wires_data.append((edge_types, edge_adaptors))
            wire_idx += 1
            wire_exp.Next()

        # 提取参数
        if surf_type in (GeomAbs_Cylinder, GeomAbs_Cone):
            # 圆柱/圆锥面孔面 - 整个面就是一个孔
            hole_info = {"surface_type": surf_type}
            if surf_type == GeomAbs_Cylinder:
                cyl = adaptor.Cylinder()
                hole_info["radius"] = cyl.Radius()
                hole_info["diameter"] = cyl.Radius() * 2
                loc = cyl.Location()
                axis = cyl.Axis()
                d = axis.Direction()
                hole_info["axis_location"] = (loc.X(), loc.Y(), loc.Z())
                hole_info["axis_direction"] = (d.X(), d.Y(), d.Z())
            elif surf_type == GeomAbs_Cone:
                cone = adaptor.Cone()
                hole_info["radius"] = cone.RefRadius()
                hole_info["diameter"] = cone.RefRadius() * 2
                loc = cone.Location()
                axis = cone.Axis()
                d = axis.Direction()
                hole_info["axis_location"] = (loc.X(), loc.Y(), loc.Z())
                hole_info["axis_direction"] = (d.X(), d.Y(), d.Z())
                hole_info["semi_angle"] = cone.SemiAngle()

            # 分类
            all_edge_types = []
            for edge_types, _ in inner_wires_data:
                all_edge_types.extend(edge_types)
            hole_info["classification"] = _classify_hole(
                inner_wires_data, all_edge_types, surf_type
            )
            holes.append(hole_info)

        elif surf_type == GeomAbs_Plane:
            # 平面上的孔 - 每条内线代表一个孔
            for edge_types, edge_adaptors in inner_wires_data:
                hole_info = {"surface_type": surf_type}

                # 从内线的圆边获取半径和轴信息
                for adaptor_c in edge_adaptors:
                    if adaptor_c.GetType() == GeomAbs_Circle:
                        circ = adaptor_c.Circle()
                        hole_info["radius"] = circ.Radius()
                        hole_info["diameter"] = circ.Radius() * 2
                        loc = circ.Location()
                        d = circ.Axis().Direction()
                        hole_info["axis_location"] = (loc.X(), loc.Y(), loc.Z())
                        hole_info["axis_direction"] = (d.X(), d.Y(), d.Z())
                        break

                # 分类
                hole_info["classification"] = _classify_hole(
                    [(edge_types, edge_adaptors)], edge_types, surf_type
                )
                holes.append(hole_info)

        exp.Next()

    return holes


def _classify_hole(inner_wires_data, all_edge_types, surf_type):
    """分类孔类型"""
    has_bspline = GeomAbs_BSplineCurve in all_edge_types
    has_circle = GeomAbs_Circle in all_edge_types
    has_line = GeomAbs_Line in all_edge_types
    has_other = any(
        t not in (GeomAbs_Circle, GeomAbs_Line)
        for t in all_edge_types
    )

    # 检查周围面是否为B样条曲面
    surrounding_bspline = (surf_type == GeomAbs_BSplineSurface)

    if has_bspline or surrounding_bspline:
        return "不规则孔（含B样条曲线）"
    elif len(inner_wires_data) == 1 and len(inner_wires_data[0][0]) == 1 and inner_wires_data[0][0][0] == GeomAbs_Circle:
        return "规则孔（单圆）"
    elif has_circle and not has_line and not has_other:
        return "规则孔（多段圆弧）"
    elif has_circle and has_line and not has_other:
        return "规则孔（直线+圆弧，如键槽）"
    else:
        return "不规则孔"


# ============================================================
# 管状/方通结构分析
# ============================================================
def _vec_almost_equal(v1, v2, tol=1e-3):
    """比较两个方向向量是否近似相等（考虑反方向）"""
    dot = abs(v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2])
    return dot > (1.0 - tol)


def _axis_perp_position(axis_dir, axis_loc):
    """获取轴线上垂直于轴方向的位置（用于判断同轴）"""
    # 将位置投影到垂直于轴方向的平面上
    # 实际上用轴位置本身，但只取垂直于轴方向的分量
    d = axis_dir
    # 投影：loc - (loc·d)*d
    dot = axis_loc[0]*d[0] + axis_loc[1]*d[1] + axis_loc[2]*d[2]
    perp = (axis_loc[0] - dot*d[0], axis_loc[1] - dot*d[1], axis_loc[2] - dot*d[2])
    return perp


def _perp_distance(p1, p2):
    """两点间距离"""
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)


def analyze_tube_structures(shape):
    """分析管状结构（同轴圆柱面对）"""
    # 收集所有圆柱面信息
    cyl_faces = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        adaptor = BRepAdaptor_Surface(face)
        if adaptor.GetType() == GeomAbs_Cylinder:
            cyl = adaptor.Cylinder()
            loc = cyl.Location()
            axis = cyl.Axis()
            d = axis.Direction()
            radius = cyl.Radius()
            cyl_faces.append({
                "face": face,
                "radius": radius,
                "axis_location": (loc.X(), loc.Y(), loc.Z()),
                "axis_direction": (d.X(), d.Y(), d.Z()),
                "perp_pos": _axis_perp_position((d.X(), d.Y(), d.Z()), (loc.X(), loc.Y(), loc.Z())),
            })
        exp.Next()

    # 找同轴圆柱面对（相同轴方向，相同垂直位置）
    tubes = []
    used = set()
    for i, c1 in enumerate(cyl_faces):
        if i in used:
            continue
        for j, c2 in enumerate(cyl_faces):
            if j <= i or j in used:
                continue
            # 检查轴方向是否相同
            if not _vec_almost_equal(c1["axis_direction"], c2["axis_direction"]):
                continue
            # 检查垂直位置是否相同（同轴）
            if _perp_distance(c1["perp_pos"], c2["perp_pos"]) > 1e-3:
                continue
            # 找到同轴对
            outer = c1 if c1["radius"] > c2["radius"] else c2
            inner = c2 if c1["radius"] > c2["radius"] else c1
            wall_thickness = outer["radius"] - inner["radius"]
            if wall_thickness < 1e-6:
                continue
            tubes.append({
                "outer_radius": outer["radius"],
                "inner_radius": inner["radius"],
                "wall_thickness": wall_thickness,
                "axis_direction": c1["axis_direction"],
                "axis_location": c1["axis_location"],
                "outer_face": outer["face"],
                "inner_face": inner["face"],
            })
            used.add(i)
            used.add(j)

    # 计算管长度（投影包围盒到轴方向）
    for tube in tubes:
        bbox = Bnd_Box()
        BRepBndLib.Add_s(tube["outer_face"], bbox)
        xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
        d = tube["axis_direction"]
        # 投影包围盒对角线到轴方向
        proj_min = xmin*d[0] + ymin*d[1] + zmin*d[2]
        proj_max = xmax*d[0] + ymax*d[1] + zmax*d[2]
        tube["length"] = abs(proj_max - proj_min)
        tube["outer_diameter"] = tube["outer_radius"] * 2
        tube["inner_diameter"] = tube["inner_radius"] * 2

    return tubes


def analyze_square_tube_structures(shape):
    """分析方通结构（平行平面对）"""
    # 收集所有平面信息
    plane_faces = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        adaptor = BRepAdaptor_Surface(face)
        if adaptor.GetType() == GeomAbs_Plane:
            pln = adaptor.Plane()
            pos = pln.Position()
            loc = pos.Location()
            d = pos.Direction()
            plane_faces.append({
                "face": face,
                "location": (loc.X(), loc.Y(), loc.Z()),
                "direction": (d.X(), d.Y(), d.Z()),
            })
        exp.Next()

    # 找平行平面对（方向相同或相反，位置不同）
    square_tubes = []
    used = set()
    for i, p1 in enumerate(plane_faces):
        if i in used:
            continue
        for j, p2 in enumerate(plane_faces):
            if j <= i or j in used:
                continue
            d1 = p1["direction"]
            d2 = p2["direction"]
            # 检查是否平行（方向相同或相反）
            dot = d1[0]*d2[0] + d1[1]*d2[1] + d1[2]*d2[2]
            if abs(abs(dot) - 1.0) > 1e-3:
                continue
            # 计算平面间距
            # 使用法向量和位置差
            loc1 = p1["location"]
            loc2 = p2["location"]
            diff = (loc2[0]-loc1[0], loc2[1]-loc1[1], loc2[2]-loc1[2])
            # 间距 = diff · d1 (投影到法向量方向)
            distance = abs(diff[0]*d1[0] + diff[1]*d1[1] + diff[2]*d1[2])
            if distance < 1e-3:
                continue

            # 检查是否方向相反（内/外面）
            is_opposite = dot < 0

            square_tubes.append({
                "face1_idx": i,
                "face2_idx": j,
                "direction": d1,
                "distance": distance,
                "is_opposite_normal": is_opposite,
                "face1": p1["face"],
                "face2": p2["face"],
            })
            used.add(i)
            used.add(j)

    # 按方向分组，找方通截面
    # 方通通常有两组平行平面对（X方向和Y方向各一对）
    direction_groups = {}
    for st in square_tubes:
        d = st["direction"]
        # 归一化方向（取正方向）
        key = None
        for existing_key in direction_groups:
            if _vec_almost_equal(d, existing_key):
                key = existing_key
                break
        if key is None:
            key = d
        if key not in direction_groups:
            direction_groups[key] = []
        direction_groups[key].append(st)

    # 找有两组正交方向的方通
    result = []
    dir_list = list(direction_groups.keys())
    for i in range(len(dir_list)):
        for j in range(i+1, len(dir_list)):
            d1 = dir_list[i]
            d2 = dir_list[j]
            # 检查是否正交
            dot = abs(d1[0]*d2[0] + d1[1]*d2[1] + d1[2]*d2[2])
            if dot > 1e-3:
                continue
            group1 = direction_groups[dir_list[i]]
            group2 = direction_groups[dir_list[j]]
            # 取每组中距离最大的对（外表面）
            if group1 and group2:
                max_dist1 = max(g["distance"] for g in group1)
                max_dist2 = max(g["distance"] for g in group2)
                result.append({
                    "cross_section_dim1": max_dist1,
                    "cross_section_dim2": max_dist2,
                    "direction1": dir_list[i],
                    "direction2": dir_list[j],
                    "pairs_count_1": len(group1),
                    "pairs_count_2": len(group2),
                })

    return square_tubes, result


# ============================================================
# 壁厚分析
# ============================================================
def analyze_wall_thickness(shape, tubes):
    """分析壁厚"""
    wall_info = []

    # 从管状结构获取壁厚
    for tube in tubes:
        wall_info.append({
            "type": "管状结构",
            "wall_thickness": tube["wall_thickness"],
            "outer_radius": tube["outer_radius"],
            "inner_radius": tube["inner_radius"],
            "axis_direction": tube["axis_direction"],
        })

    # 使用BRepExtrema计算内外面之间的距离（通用方法）
    # 收集所有面
    all_faces = []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        all_faces.append(TopoDS.Face_s(exp.Current()))
        exp.Next()

    # 对管状结构的内外面计算距离
    for tube in tubes:
        try:
            dist_calc = BRepExtrema_DistShapeShape()
            dist_calc.LoadS1(tube["inner_face"])
            dist_calc.LoadS2(tube["outer_face"])
            dist_calc.Perform()
            if dist_calc.IsDone():
                min_dist = dist_calc.Value()
                wall_info.append({
                    "type": "内外面距离",
                    "wall_thickness": min_dist,
                    "axis_direction": tube["axis_direction"],
                })
        except Exception:
            pass

    return wall_info


# ============================================================
# 模型类型自动检测
# ============================================================
def detect_model_type(tubes, square_tube_pairs, square_tube_cross):
    """自动检测模型类型"""
    if square_tube_cross or square_tube_pairs:
        return "方通结构"
    if tubes:
        return "管状结构"
    return "一般机械件"


# ============================================================
# Word报告生成
# ============================================================
def fmt_length(val):
    """格式化长度值，3位小数+mm"""
    return f"{val:.3f} mm"


def fmt_area(val):
    """格式化面积值，2位小数+mm²"""
    return f"{val:.2f} mm²"


def fmt_volume(val):
    """格式化体积值，2位小数+mm³"""
    return f"{val:.2f} mm³"


def add_table_row(table, cells_data):
    """向表格添加一行"""
    row = table.add_row()
    for i, text in enumerate(cells_data):
        row.cells[i].text = str(text)
    return row


def generate_report(filepath, output_dir):
    """生成Word分析报告"""
    filename = os.path.basename(filepath)
    basename = os.path.splitext(filename)[0]

    print(f"正在分析: {filename}")

    # 读取STEP文件
    shape = read_step_file(filepath)
    if shape is None:
        print(f"  错误: 无法读取文件 {filename}")
        return False

    # ---- 分析 ----
    topology = count_topology(shape)
    face_types = count_face_types(shape)
    edge_types = count_edge_types(shape)
    bbox = get_bounding_box(shape)
    volume, center_of_mass = get_volume(shape)
    surface_area = get_surface_area(shape)
    holes = analyze_holes(shape)
    tubes = analyze_tube_structures(shape)
    sq_pairs, sq_cross = analyze_square_tube_structures(shape)
    wall_info = analyze_wall_thickness(shape, tubes)
    model_type = detect_model_type(tubes, sq_pairs, sq_cross)

    # 模型类型中文描述
    model_type_desc = {
        "管状结构": "该模型包含同轴的内外圆柱面，属于管状结构",
        "方通结构": "该模型包含多组平行平面对，属于方通结构",
        "一般机械件": "该模型为一般机械零件",
    }

    # ---- 生成Word文档 ----
    doc = Document()

    # 设置默认字体
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(10.5)

    # 标题
    doc.add_heading(f"{basename} 分析报告", level=0)

    # 1. 概览
    doc.add_heading("概览", level=1)
    overview_table = doc.add_table(rows=0, cols=2)
    overview_table.style = 'Table Grid'
    overview_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_row(overview_table, ["文件名", filename])
    add_table_row(overview_table, ["模型类型", model_type])
    add_table_row(overview_table, ["简要描述", model_type_desc.get(model_type, "")])
    add_table_row(overview_table, ["顶点数", str(topology["顶点"])])
    add_table_row(overview_table, ["边数", str(topology["边"])])
    add_table_row(overview_table, ["面数", str(topology["面"])])

    # 2. 拓扑信息
    doc.add_heading("拓扑信息", level=1)
    topo_table = doc.add_table(rows=1, cols=2)
    topo_table.style = 'Table Grid'
    topo_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    topo_table.rows[0].cells[0].text = "拓扑类型"
    topo_table.rows[0].cells[1].text = "数量"
    for name in ["顶点", "边", "线", "面", "壳", "实体"]:
        add_table_row(topo_table, [name, str(topology[name])])

    # 3. 几何类型分布
    doc.add_heading("几何类型分布", level=1)

    doc.add_heading("面类型统计", level=2)
    face_table = doc.add_table(rows=1, cols=2)
    face_table.style = 'Table Grid'
    face_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    face_table.rows[0].cells[0].text = "面类型"
    face_table.rows[0].cells[1].text = "数量"
    for tname, count in sorted(face_types.items(), key=lambda x: -x[1]):
        add_table_row(face_table, [tname, str(count)])

    doc.add_heading("边类型统计", level=2)
    edge_table = doc.add_table(rows=1, cols=2)
    edge_table.style = 'Table Grid'
    edge_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    edge_table.rows[0].cells[0].text = "边类型"
    edge_table.rows[0].cells[1].text = "数量"
    for tname, count in sorted(edge_types.items(), key=lambda x: -x[1]):
        add_table_row(edge_table, [tname, str(count)])

    # 4. 尺寸信息
    doc.add_heading("尺寸信息", level=1)
    dim_table = doc.add_table(rows=0, cols=2)
    dim_table.style = 'Table Grid'
    dim_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_row(dim_table, ["X方向尺寸", fmt_length(bbox["x_size"])])
    add_table_row(dim_table, ["Y方向尺寸", fmt_length(bbox["y_size"])])
    add_table_row(dim_table, ["Z方向尺寸", fmt_length(bbox["z_size"])])
    add_table_row(dim_table, ["X范围", f"[{bbox['x_min']:.3f}, {bbox['x_max']:.3f}] mm"])
    add_table_row(dim_table, ["Y范围", f"[{bbox['y_min']:.3f}, {bbox['y_max']:.3f}] mm"])
    add_table_row(dim_table, ["Z范围", f"[{bbox['z_min']:.3f}, {bbox['z_max']:.3f}] mm"])
    add_table_row(dim_table, ["体积", fmt_volume(volume)])
    add_table_row(dim_table, ["表面积", fmt_area(surface_area)])
    com_x, com_y, com_z = center_of_mass.X(), center_of_mass.Y(), center_of_mass.Z()
    add_table_row(dim_table, ["质心位置", f"({com_x:.3f}, {com_y:.3f}, {com_z:.3f}) mm"])

    # 5. 孔特征
    doc.add_heading("孔特征", level=1)
    if holes:
        regular_count = sum(1 for h in holes if h["classification"].startswith("规则"))
        irregular_count = sum(1 for h in holes if h["classification"].startswith("不规则"))
        doc.add_paragraph(f"孔总数: {len(holes)}，规则孔: {regular_count}，不规则孔: {irregular_count}")

        hole_table = doc.add_table(rows=1, cols=6)
        hole_table.style = 'Table Grid'
        hole_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["序号", "分类", "直径(mm)", "半径(mm)", "轴位置", "轴方向"]
        for i, h in enumerate(headers):
            hole_table.rows[0].cells[i].text = h

        for idx, hole in enumerate(holes, 1):
            diameter = f"{hole.get('diameter', 0):.3f}" if hole.get('diameter') else "N/A"
            radius = f"{hole.get('radius', 0):.3f}" if hole.get('radius') else "N/A"
            axis_loc = hole.get("axis_location", None)
            axis_dir = hole.get("axis_direction", None)
            loc_str = f"({axis_loc[0]:.3f}, {axis_loc[1]:.3f}, {axis_loc[2]:.3f})" if axis_loc else "N/A"
            dir_str = f"({axis_dir[0]:.3f}, {axis_dir[1]:.3f}, {axis_dir[2]:.3f})" if axis_dir else "N/A"
            add_table_row(hole_table, [
                str(idx), hole["classification"], diameter, radius, loc_str, dir_str
            ])
    else:
        doc.add_paragraph("未检测到孔特征")

    # 6. 管状/方通结构
    if tubes:
        doc.add_heading("管状结构", level=1)
        doc.add_paragraph(f"检测到 {len(tubes)} 组同轴圆柱面对")

        tube_table = doc.add_table(rows=1, cols=6)
        tube_table.style = 'Table Grid'
        tube_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["序号", "外径(mm)", "内径(mm)", "壁厚(mm)", "长度(mm)", "轴方向"]
        for i, h in enumerate(headers):
            tube_table.rows[0].cells[i].text = h

        for idx, tube in enumerate(tubes, 1):
            d = tube["axis_direction"]
            dir_str = f"({d[0]:.3f}, {d[1]:.3f}, {d[2]:.3f})"
            add_table_row(tube_table, [
                str(idx),
                fmt_length(tube["outer_diameter"]),
                fmt_length(tube["inner_diameter"]),
                fmt_length(tube["wall_thickness"]),
                fmt_length(tube["length"]),
                dir_str,
            ])

    if sq_cross:
        doc.add_heading("方通结构", level=1)
        for idx, sq in enumerate(sq_cross, 1):
            doc.add_paragraph(
                f"方通截面 {idx}: "
                f"尺寸1 = {fmt_length(sq['cross_section_dim1'])}, "
                f"尺寸2 = {fmt_length(sq['cross_section_dim2'])}, "
                f"方向1对数 = {sq['pairs_count_1']}, "
                f"方向2对数 = {sq['pairs_count_2']}"
            )
    elif sq_pairs:
        doc.add_heading("方通结构", level=1)
        doc.add_paragraph(f"检测到 {len(sq_pairs)} 组平行平面对")
        sq_table = doc.add_table(rows=1, cols=4)
        sq_table.style = 'Table Grid'
        sq_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["序号", "法向量方向", "间距(mm)", "法向量是否相反"]
        for i, h in enumerate(headers):
            sq_table.rows[0].cells[i].text = h
        for idx, pair in enumerate(sq_pairs, 1):
            d = pair["direction"]
            dir_str = f"({d[0]:.3f}, {d[1]:.3f}, {d[2]:.3f})"
            add_table_row(sq_table, [
                str(idx), dir_str, fmt_length(pair["distance"]),
                "是" if pair["is_opposite_normal"] else "否"
            ])

    # 7. 壁厚信息
    doc.add_heading("壁厚信息", level=1)
    if wall_info:
        wall_table = doc.add_table(rows=1, cols=4)
        wall_table.style = 'Table Grid'
        wall_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["序号", "类型", "壁厚(mm)", "备注"]
        for i, h in enumerate(headers):
            wall_table.rows[0].cells[i].text = h
        for idx, wi in enumerate(wall_info, 1):
            note = ""
            if wi.get("outer_radius"):
                note = f"外径={wi['outer_radius']*2:.3f}, 内径={wi['inner_radius']*2:.3f}"
            add_table_row(wall_table, [
                str(idx), wi["type"], fmt_length(wi["wall_thickness"]), note
            ])
    else:
        doc.add_paragraph("未检测到壁厚信息")

    # 保存文档
    output_filename = f"{basename}_分析报告.docx"
    output_path = os.path.join(output_dir, output_filename)
    doc.save(output_path)
    print(f"  报告已生成: {output_path}")
    return True


# ============================================================
# 主函数
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="STEP文件分析工具 - 解析STEP文件并生成Word分析报告")
    parser.add_argument("--input", required=True, help="STEP文件路径或包含STEP文件的目录")
    parser.add_argument("--output", help="输出目录，默认与输入相同")
    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output

    # 收集STEP文件
    step_files = []
    if os.path.isfile(input_path):
        step_files.append(input_path)
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(input_path))
    elif os.path.isdir(input_path):
        if output_dir is None:
            output_dir = input_path
        for f in os.listdir(input_path):
            ext = os.path.splitext(f)[1].lower()
            if ext in ('.step', '.stp'):
                step_files.append(os.path.join(input_path, f))
    else:
        print(f"错误: 输入路径不存在: {input_path}")
        sys.exit(1)

    if not step_files:
        print("未找到STEP文件")
        sys.exit(1)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 处理每个文件
    success_count = 0
    fail_count = 0
    for step_file in step_files:
        try:
            result = generate_report(step_file, output_dir)
            if result:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  错误: 处理文件 {os.path.basename(step_file)} 时出错: {e}")
            fail_count += 1

    print(f"\n处理完成: 成功 {success_count} 个, 失败 {fail_count} 个")


if __name__ == "__main__":
    main()
