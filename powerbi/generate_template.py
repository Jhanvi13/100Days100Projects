#!/usr/bin/env python3
"""
Generate Employee Performance Power BI Template (.pbit)
Professional dark theme with slicers, KPIs, charts, and logo/title area.
"""

import json
import zipfile
import uuid
import os

# ── helpers ──────────────────────────────────────────────────────────────────
def g():
    return str(uuid.uuid4()).upper()

def solid(c):
    return {"solid": {"color": c}}

def num(v):
    return {"numeric": v}

def lit(v):
    return {"expr": {"Literal": {"Value": f"'{v}'"}}}

def b(v):
    return {"bool": v}

# ── palette ──────────────────────────────────────────────────────────────────
BG      = "#0B1929"   # page background
HEADER  = "#0D2137"   # header bar
PANEL   = "#112840"   # slicer panel
CARD    = "#0F2133"   # KPI card bg
ACCENT  = "#38BDF8"   # sky-blue accent
ACCENT2 = "#22D3EE"   # cyan
GREEN   = "#34D399"   # positive
RED     = "#F87171"   # negative
AMBER   = "#FBBF24"   # warning
WHITE   = "#F8FAFC"
MUTED   = "#94A3B8"
BORDER  = "#1E3A5F"
LOGO_BG = "#0A1E2E"   # slightly darker for logo area

TABLE   = "EmployeePerformance"
W, H    = 1280, 720

# ── DataModelSchema ──────────────────────────────────────────────────────────
M_QUERY = [
    "let",
    "    Source = Table.FromRows(",
    "        Json.Document(Binary.Decompress(",
    "            Binary.FromText(\"\", BinaryEncoding.Base64),",
    "            Compression.Deflate)),",
    "        let _t = ((type nullable text) meta [Serialized.Text = true]) in",
    "        type table [",
    "            ID = _t, #\"DATE\" = _t, DATE_DATESTRING = _t,",
    "            CONTEXT_PLANT = _t, CONTEXT = _t, CONTEXT_ENTERPRISE = _t,",
    "            EMPLOYEENAME = _t, JOBTITLE = _t, EMPLOYEEPERFORMANCE = _t,",
    "            TOTAL_SCORE = _t, TARGETMET = _t, FORMPASSFAIL = _t,",
    "            FORMID = _t, OFFICIALTIME = _t, WALLTIME = _t,",
    "            PERFORMANCEOBSERVED = _t, PERSONWHOSUBMITTEDTHISFORM = _t,",
    "            STATUS_WORKFLOW = _t, STATUS_CREATEDBY = _t,",
    "            STATUS_LASTMODIFIED = _t, STATUS_LASTMODIFIEDBY = _t,",
    "            APPROVAL_STATUS = _t, APPROVAL_DATETIME = _t,",
    "            APPROVAL_USER = _t, WASEMPLOYEEADDRESSED = _t,",
    "            STATUSOVERRIDEREASON = _t, COMMENTS = _t",
    "        ]",
    "    ),",
    "    #\"Changed Type\" = Table.TransformColumnTypes(Source,{",
    "        {\"ID\", Int64.Type}, {\"DATE\", type date},",
    "        {\"EMPLOYEEPERFORMANCE\", type number}, {\"TOTAL_SCORE\", type number},",
    "        {\"PERFORMANCEOBSERVED\", type number}, {\"TARGETMET\", type logical},",
    "        {\"STATUS_LASTMODIFIED\", type datetime},",
    "        {\"APPROVAL_DATETIME\", type datetime}",
    "    })",
    "in",
    "    #\"Changed Type\""
]

COLS = [
    ("ID",                        "int64"),
    ("DATE",                      "dateTime"),
    ("DATE_DATESTRING",           "string"),
    ("CONTEXT_PLANT",             "string"),
    ("CONTEXT",                   "string"),
    ("CONTEXT_ENTERPRISE",        "string"),
    ("EMPLOYEENAME",              "string"),
    ("JOBTITLE",                  "string"),
    ("EMPLOYEEPERFORMANCE",       "double"),
    ("TOTAL_SCORE",               "double"),
    ("TARGETMET",                 "boolean"),
    ("FORMPASSFAIL",              "string"),
    ("FORMID",                    "string"),
    ("OFFICIALTIME",              "string"),
    ("WALLTIME",                  "string"),
    ("PERFORMANCEOBSERVED",       "double"),
    ("PERSONWHOSUBMITTEDTHISFORM","string"),
    ("STATUS_WORKFLOW",           "string"),
    ("STATUS_CREATEDBY",          "string"),
    ("STATUS_LASTMODIFIED",       "dateTime"),
    ("STATUS_LASTMODIFIEDBY",     "string"),
    ("APPROVAL_STATUS",           "string"),
    ("APPROVAL_DATETIME",         "dateTime"),
    ("APPROVAL_USER",             "string"),
    ("WASEMPLOYEEADDRESSED",      "string"),
    ("STATUSOVERRIDEREASON",      "string"),
    ("COMMENTS",                  "string"),
]

MEASURES = [
    ("Total Forms",   "COUNTROWS(EmployeePerformance)"),
    ("Pass Rate %",   "DIVIDE(COUNTROWS(FILTER(EmployeePerformance, EmployeePerformance[FORMPASSFAIL] = \"Pass\")), COUNTROWS(EmployeePerformance), 0) * 100"),
    ("Avg Score",     "AVERAGE(EmployeePerformance[TOTAL_SCORE])"),
    ("Forms Passed",  "COUNTROWS(FILTER(EmployeePerformance, EmployeePerformance[FORMPASSFAIL] = \"Pass\"))"),
    ("Forms Failed",  "COUNTROWS(FILTER(EmployeePerformance, EmployeePerformance[FORMPASSFAIL] = \"Fail\"))"),
    ("Target Met %",  "DIVIDE(COUNTROWS(FILTER(EmployeePerformance, EmployeePerformance[TARGETMET] = TRUE())), COUNTROWS(EmployeePerformance), 0) * 100"),
]

def data_model_schema():
    columns = [
        {
            "name": name,
            "dataType": dtype,
            "sourceColumn": name,
            "lineageTag": g(),
            "summarizeBy": "none" if dtype == "string" else ("sum" if dtype in ("double","int64") else "none"),
        }
        for name, dtype in COLS
    ]
    measures = [
        {
            "name": mname,
            "expression": expr,
            "formatString": "0" if "%" in mname else ("#,0" if mname in ("Total Forms","Forms Passed","Forms Failed") else "0.00"),
            "lineageTag": g(),
        }
        for mname, expr in MEASURES
    ]
    return {
        "name": "Model",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "tables": [
                {
                    "name": TABLE,
                    "lineageTag": g(),
                    "columns": columns,
                    "measures": measures,
                    "partitions": [
                        {
                            "name": TABLE,
                            "mode": "import",
                            "source": {"type": "m", "expression": M_QUERY}
                        }
                    ],
                    "annotations": [
                        {"name": "PBI_ResultType", "value": "Table"}
                    ]
                }
            ],
            "relationships": [],
            "annotations": [
                {"name": "PBIDesktopVersion", "value": "2.119.986.0"},
                {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
            ]
        }
    }

# ── Report Layout helpers ─────────────────────────────────────────────────────
def vc(x, y, w, h, cfg, z=2000, filters="[]"):
    """Build a visual container dict."""
    return {
        "x": float(x), "y": float(y),
        "z": float(z), "width": float(w), "height": float(h),
        "config": json.dumps(cfg, separators=(',', ':')),
        "filters": filters,
    }

def slicer_cfg(field, title, style="list"):
    """Slicer visual config."""
    return {
        "name": g(),
        "filters": "[]",
        "type": "slicer",
        "dataRoles": [{"name": "Field", "projections": [{"queryRef": f"{TABLE}.{field}", "active": True}]}],
        "objects": {
            "general": {
                "outlineColor": solid(ACCENT),
                "outlineWeight": num(1),
                "orientation": lit("Vertical"),
                "responsive": b(True),
            },
            "selection": {
                "selectAllCheckboxEnabled": b(True),
                "singleSelect": b(False),
            },
            "header": {
                "show": b(True),
                "fontColor": solid(ACCENT),
                "background": solid(PANEL),
                "textSize": num(11),
                "fontFamily": lit("Segoe UI Semibold"),
                "bold": b(True),
            },
            "items": {
                "fontColor": solid(WHITE),
                "background": solid("transparent"),
                "outline": lit("None"),
                "textSize": num(10),
                "fontFamily": lit("Segoe UI"),
            },
            "background": {"color": solid(PANEL), "transparency": num(0)},
            "border": {"show": b(True), "color": solid(BORDER), "radius": num(6)},
            "title": {
                "show": b(True),
                "text": lit(title),
                "fontColor": solid(WHITE),
                "background": solid(PANEL),
                "bold": b(True),
                "textSize": num(11),
                "fontFamily": lit("Segoe UI Semibold"),
            },
        },
    }

def date_slicer_cfg(field, title):
    """Between-date slicer."""
    return {
        "name": g(),
        "filters": "[]",
        "type": "slicer",
        "dataRoles": [{"name": "Field", "projections": [{"queryRef": f"{TABLE}.{field}", "active": True}]}],
        "objects": {
            "general": {
                "outlineColor": solid(ACCENT),
                "outlineWeight": num(1),
                "orientation": lit("Vertical"),
                "responsive": b(True),
            },
            "data": {"mode": lit("Between")},
            "header": {
                "show": b(True),
                "fontColor": solid(ACCENT),
                "background": solid(PANEL),
                "textSize": num(11),
                "fontFamily": lit("Segoe UI Semibold"),
                "bold": b(True),
            },
            "numericInputStyle": {
                "fontColor": solid(WHITE),
                "textSize": num(10),
                "fontFamily": lit("Segoe UI"),
            },
            "background": {"color": solid(PANEL), "transparency": num(0)},
            "border": {"show": b(True), "color": solid(BORDER), "radius": num(6)},
            "title": {
                "show": b(True),
                "text": lit(title),
                "fontColor": solid(WHITE),
                "background": solid(PANEL),
                "bold": b(True),
                "textSize": num(11),
                "fontFamily": lit("Segoe UI Semibold"),
            },
        },
    }

def card_cfg(field_or_measure, is_measure=True):
    ref = f"{TABLE}.{field_or_measure}" if is_measure else f"{TABLE}.{field_or_measure}"
    return {
        "name": g(),
        "filters": "[]",
        "type": "card",
        "dataRoles": [{"name": "Values", "projections": [{"queryRef": ref, "active": True}]}],
        "objects": {
            "general": {},
            "labels": {
                "show": b(True),
                "color": solid(ACCENT),
                "labelPrecision": num(0),
                "fontSize": num(28),
                "fontFamily": lit("Segoe UI Light"),
                "bold": b(True),
            },
            "categoryLabels": {
                "show": b(True),
                "color": solid(MUTED),
                "fontSize": num(11),
                "fontFamily": lit("Segoe UI"),
            },
            "background": {"color": solid(CARD), "transparency": num(0)},
            "border": {"show": b(True), "color": solid(ACCENT), "radius": num(8)},
            "dropShadow": {"show": b(True)},
            "title": {"show": b(False)},
        },
    }

def column_chart_cfg(cat_field, val_field, chart_title):
    return {
        "name": g(),
        "filters": "[]",
        "type": "columnChart",
        "dataRoles": [
            {"name": "Category", "projections": [{"queryRef": f"{TABLE}.{cat_field}", "active": True}]},
            {"name": "Y", "projections": [{"queryRef": f"{TABLE}.{val_field}", "active": True}]},
        ],
        "objects": {
            "general": {"responsive": b(True)},
            "categoryAxis": {
                "show": b(True),
                "labelColor": solid(MUTED),
                "fontSize": num(10),
                "fontFamily": lit("Segoe UI"),
                "gridlineShow": b(False),
            },
            "valueAxis": {
                "show": b(True),
                "labelColor": solid(MUTED),
                "fontSize": num(10),
                "fontFamily": lit("Segoe UI"),
                "gridlineShow": b(True),
                "gridlineColor": solid(BORDER),
            },
            "dataPoint": {
                "defaultColor": solid(ACCENT),
                "showAllDataPoints": b(False),
            },
            "background": {"color": solid(CARD), "transparency": num(0)},
            "border": {"show": b(True), "color": solid(BORDER), "radius": num(8)},
            "title": {
                "show": b(True),
                "text": lit(chart_title),
                "fontColor": solid(WHITE),
                "background": solid(CARD),
                "textSize": num(12),
                "fontFamily": lit("Segoe UI Semibold"),
                "bold": b(True),
            },
            "plotArea": {"transparency": num(0)},
            "legend": {"show": b(False)},
        },
    }

def donut_cfg(cat_field, val_field, chart_title):
    return {
        "name": g(),
        "filters": "[]",
        "type": "donutChart",
        "dataRoles": [
            {"name": "Category", "projections": [{"queryRef": f"{TABLE}.{cat_field}", "active": True}]},
            {"name": "Y", "projections": [{"queryRef": f"{TABLE}.{val_field}", "active": True}]},
        ],
        "objects": {
            "general": {"responsive": b(True)},
            "legend": {
                "show": b(True),
                "position": lit("Bottom"),
                "fontColor": solid(MUTED),
                "fontSize": num(10),
                "fontFamily": lit("Segoe UI"),
            },
            "dataPoint": {"showAllDataPoints": b(True)},
            "labels": {
                "show": b(True),
                "color": solid(WHITE),
                "fontSize": num(10),
                "fontFamily": lit("Segoe UI"),
            },
            "background": {"color": solid(CARD), "transparency": num(0)},
            "border": {"show": b(True), "color": solid(BORDER), "radius": num(8)},
            "title": {
                "show": b(True),
                "text": lit(chart_title),
                "fontColor": solid(WHITE),
                "background": solid(CARD),
                "textSize": num(12),
                "fontFamily": lit("Segoe UI Semibold"),
                "bold": b(True),
            },
        },
    }

def line_chart_cfg(axis_field, val_field, chart_title):
    return {
        "name": g(),
        "filters": "[]",
        "type": "lineChart",
        "dataRoles": [
            {"name": "Category", "projections": [{"queryRef": f"{TABLE}.{axis_field}", "active": True}]},
            {"name": "Y", "projections": [{"queryRef": f"{TABLE}.{val_field}", "active": True}]},
        ],
        "objects": {
            "general": {"responsive": b(True)},
            "categoryAxis": {
                "show": b(True),
                "labelColor": solid(MUTED),
                "fontSize": num(10),
                "fontFamily": lit("Segoe UI"),
            },
            "valueAxis": {
                "show": b(True),
                "labelColor": solid(MUTED),
                "fontSize": num(10),
                "fontFamily": lit("Segoe UI"),
                "gridlineShow": b(True),
                "gridlineColor": solid(BORDER),
            },
            "dataPoint": {"defaultColor": solid(ACCENT2)},
            "lineStyles": {"strokeWidth": num(2), "lineStyle": lit("solid"), "showMarker": b(True)},
            "background": {"color": solid(CARD), "transparency": num(0)},
            "border": {"show": b(True), "color": solid(BORDER), "radius": num(8)},
            "title": {
                "show": b(True),
                "text": lit(chart_title),
                "fontColor": solid(WHITE),
                "background": solid(CARD),
                "textSize": num(12),
                "fontFamily": lit("Segoe UI Semibold"),
                "bold": b(True),
            },
            "legend": {"show": b(False)},
        },
    }

def table_cfg(fields, chart_title):
    projections = [{"queryRef": f"{TABLE}.{f}", "active": True} for f in fields]
    return {
        "name": g(),
        "filters": "[]",
        "type": "tableEx",
        "dataRoles": [{"name": "Values", "projections": projections}],
        "objects": {
            "general": {"textSize": num(10), "totals": b(False), "autoSizeColumnWidth": b(True)},
            "grid": {
                "gridVertical": b(True),
                "gridVerticalColor": solid(BORDER),
                "gridVerticalWeight": num(1),
                "gridHorizontal": b(True),
                "gridHorizontalColor": solid(BORDER),
                "gridHorizontalWeight": num(1),
                "rowPadding": num(4),
                "outlineColor": solid(BORDER),
                "outlineWeight": num(1),
                "imageHeight": num(75),
            },
            "columnHeaders": {
                "fontColor": solid(ACCENT),
                "backColor": solid(HEADER),
                "textSize": num(11),
                "fontFamily": lit("Segoe UI Semibold"),
                "bold": b(True),
                "outline": lit("BottomOnly"),
                "wordWrap": b(False),
                "autoSizeColumnWidth": b(True),
            },
            "values": {
                "fontColorPrimary": solid(WHITE),
                "backColorPrimary": solid(CARD),
                "fontColorSecondary": solid(MUTED),
                "backColorSecondary": solid(PANEL),
                "textSize": num(10),
                "fontFamily": lit("Segoe UI"),
                "outline": lit("None"),
                "wordWrap": b(False),
            },
            "background": {"color": solid(CARD), "transparency": num(0)},
            "border": {"show": b(True), "color": solid(BORDER), "radius": num(8)},
            "title": {
                "show": b(True),
                "text": lit(chart_title),
                "fontColor": solid(WHITE),
                "background": solid(CARD),
                "textSize": num(12),
                "fontFamily": lit("Segoe UI Semibold"),
                "bold": b(True),
            },
        },
    }

def rect_cfg(fill, border_color=None, radius=0, opacity=0):
    obj = {
        "name": g(),
        "filters": "[]",
        "type": "shape",
        "objects": {
            "general": {},
            "line": {"weight": num(0), "color": solid(fill), "roundEdge": num(radius)},
            "fill": {"color": solid(fill), "transparency": num(opacity)},
        },
    }
    if border_color:
        obj["objects"]["line"]["color"] = solid(border_color)
    return obj

def text_cfg(txt, font_size=14, font_color=WHITE, bold=False, align="center", bg=None):
    obj = {
        "name": g(),
        "filters": "[]",
        "type": "textbox",
        "objects": {
            "general": {},
            "background": {"color": solid(bg or "transparent"), "transparency": num(100 if bg is None else 0)},
            "border": {"show": b(False)},
        },
        "content": json.dumps({
            "paragraphs": [{
                "textRuns": [{
                    "value": txt,
                    "textStyle": {
                        "fontWeight": "bold" if bold else "normal",
                        "fontSize": f"{font_size}pt",
                        "color": font_color,
                        "fontFamily": "Segoe UI Semibold" if bold else "Segoe UI",
                    }
                }],
                "horizontalTextAlignment": align.capitalize(),
            }]
        }),
    }
    return obj

# ── Page config ───────────────────────────────────────────────────────────────
def page_config():
    return json.dumps({
        "defaultVisual": "tableEx",
        "outspacePane": {
            "backgroundColor": solid(BG),
        },
        "background": solid(BG),
    }, separators=(',', ':'))

def report_config():
    return json.dumps({
        "version": "5.43",
        "themeCollection": {
            "baseTheme": {
                "name": "CY22SU12",
                "version": "5.43.0",
                "type": 2,
            }
        },
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "allowChangeFilterTypes": True,
        "settings": {
            "filterPaneEnabled": False,
            "navContentPaneEnabled": False,
            "useNewFilterPaneExperience": True,
            "allowChangeFilterTypes": True,
        }
    }, separators=(',', ':'))

# ── Layout positions ──────────────────────────────────────────────────────────
# Canvas: 1280 x 720
# Header bar:  y=0, h=70          (logo left + title center + date right)
# Slicer panel: x=0, y=70, w=220, h=650
# Content area: x=230, y=70, w=1050, h=650
#   KPI row:     y=80, h=90        (3 cards)
#   Charts row:  y=180, h=210      (column chart + donut + line)
#   Table:       y=400, h=310

PAD = 8
SX = 0         # slicer panel x
SW = 220       # slicer panel width
HH = 70        # header height
CX = SW + PAD  # content start x
CW = W - CX - PAD  # content width
CY = HH + PAD  # content start y

# KPI row
KH = 90
KW = (CW - 2*PAD) // 3

# Chart row
CH1 = 210
CY2 = CY + KH + PAD

# Table
TH = H - CY2 - CH1 - PAD - PAD
TY = CY2 + CH1 + PAD

def build_visuals():
    visuals = []
    z = 1000

    # ── Header background ────────────────────────────────────────────────────
    visuals.append(vc(0, 0, W, HH, rect_cfg(HEADER), z=z))
    z += 1

    # ── Accent line under header ─────────────────────────────────────────────
    visuals.append(vc(0, HH-2, W, 2, rect_cfg(ACCENT), z=z))
    z += 1

    # ── Logo placeholder (left side of header) ───────────────────────────────
    visuals.append(vc(PAD, PAD, 120, HH - 2*PAD,
                      rect_cfg(LOGO_BG, border_color=BORDER, radius=6), z=z))
    z += 1
    visuals.append(vc(PAD, PAD, 120, HH - 2*PAD,
                      text_cfg("[ LOGO ]", font_size=10, font_color=MUTED, align="center"), z=z))
    z += 1

    # ── Report Title (center of header) ──────────────────────────────────────
    visuals.append(vc(140, 10, 800, 50,
                      text_cfg("Employee Performance Dashboard",
                               font_size=20, font_color=WHITE, bold=True, align="center"), z=z))
    z += 1

    # ── Subtitle / report name right side ────────────────────────────────────
    visuals.append(vc(950, 15, 320, 40,
                      text_cfg("[ Report Period ]", font_size=11, font_color=MUTED, align="right"), z=z))
    z += 1

    # ── Slicer panel background ──────────────────────────────────────────────
    visuals.append(vc(0, HH, SW, H - HH, rect_cfg(PANEL), z=z))
    z += 1

    # ── Slicer panel title ───────────────────────────────────────────────────
    visuals.append(vc(4, HH+4, SW-8, 28,
                      text_cfg("FILTERS", font_size=10, font_color=ACCENT, bold=True, align="center"), z=z))
    z += 1

    # ── Divider under slicer title ───────────────────────────────────────────
    visuals.append(vc(8, HH+32, SW-16, 1, rect_cfg(BORDER), z=z))
    z += 1

    # ── 5 Slicers stacked in left panel ──────────────────────────────────────
    slicer_defs = [
        ("DATE",           "Date Range",      "date"),
        ("CONTEXT_PLANT",  "Plant / Location", "list"),
        ("JOBTITLE",       "Job Title",        "list"),
        ("FORMPASSFAIL",   "Pass / Fail",      "list"),
        ("APPROVAL_STATUS","Approval Status",  "list"),
    ]
    sy = HH + 40
    sh = (H - sy - PAD) // len(slicer_defs) - PAD
    for field, title, style in slicer_defs:
        cfg = date_slicer_cfg(field, title) if style == "date" else slicer_cfg(field, title, style)
        visuals.append(vc(PAD, sy, SW - 2*PAD, sh, cfg, z=z))
        sy += sh + PAD
        z += 1

    # ── 3 KPI Cards ──────────────────────────────────────────────────────────
    kpi_defs = [
        ("Total Forms",  "Total Forms",   ACCENT),
        ("Pass Rate %",  "Pass Rate %",   GREEN),
        ("Avg Score",    "Avg Score",     AMBER),
    ]
    for i, (measure, _, color) in enumerate(kpi_defs):
        kx = CX + i * (KW + PAD)
        cfg = card_cfg(measure)
        # Override label color per card
        cfg["objects"]["labels"]["color"] = solid(color)
        cfg["objects"]["border"]["color"] = solid(color)
        visuals.append(vc(kx, CY, KW, KH, cfg, z=z))
        z += 1

    # ── Charts row ───────────────────────────────────────────────────────────
    chart_w_col = int(CW * 0.45)
    chart_w_don = int(CW * 0.25)
    chart_w_lin = CW - chart_w_col - chart_w_don - 2*PAD

    # Column chart: forms by plant
    visuals.append(vc(CX, CY2, chart_w_col, CH1,
                      column_chart_cfg("CONTEXT_PLANT", "Total Forms", "Forms by Plant"), z=z))
    z += 1

    # Donut chart: pass vs fail
    visuals.append(vc(CX + chart_w_col + PAD, CY2, chart_w_don, CH1,
                      donut_cfg("FORMPASSFAIL", "Total Forms", "Pass vs Fail"), z=z))
    z += 1

    # Line chart: score trend
    visuals.append(vc(CX + chart_w_col + chart_w_don + 2*PAD, CY2, chart_w_lin, CH1,
                      line_chart_cfg("DATE_DATESTRING", "Avg Score", "Score Trend"), z=z))
    z += 1

    # ── Detail Table ─────────────────────────────────────────────────────────
    table_fields = [
        "EMPLOYEENAME", "JOBTITLE", "CONTEXT_PLANT",
        "DATE_DATESTRING", "TOTAL_SCORE", "FORMPASSFAIL",
        "APPROVAL_STATUS", "PERSONWHOSUBMITTEDTHISFORM",
    ]
    visuals.append(vc(CX, TY, CW, TH,
                      table_cfg(table_fields, "Employee Performance Detail"), z=z))

    return visuals


def build_layout():
    visuals = build_visuals()
    section_cfg = json.dumps({
        "id": 0,
        "displayName": "Dashboard",
        "filters": "[]",
        "background": solid(BG),
        "outspacePane": {"backgroundColor": solid(BG)},
        "defaultVisual": {},
        "wallpaper": {"show": b(False)},
    }, separators=(',', ':'))

    return {
        "id": 0,
        "resourcePackages": [],
        "sections": [
            {
                "id": 0,
                "name": "ReportSection1",
                "displayName": "Dashboard",
                "filters": "[]",
                "ordinal": 0,
                "visualContainers": visuals,
                "config": section_cfg,
                "displayOption": 1,
            }
        ],
        "config": report_config(),
        "layoutOptimization": 0,
    }


# ── PBIT assembly ─────────────────────────────────────────────────────────────
CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="xml" ContentType="application/xml" />
  <Override PartName="/DataModelSchema" ContentType="application/json" />
  <Override PartName="/DiagramLayout" ContentType="application/json" />
  <Override PartName="/Report/Layout" ContentType="application/json" />
  <Override PartName="/SecurityBindings" ContentType="application/json" />
  <Override PartName="/Settings" ContentType="application/json" />
  <Override PartName="/Version" ContentType="application/json" />
  <Override PartName="/Metadata" ContentType="application/json" />
</Types>"""

DIAGRAM_LAYOUT = json.dumps({
    "version": 1,
    "tables": [
        {"id": 0, "name": TABLE, "x": 0, "y": 0, "width": 300, "height": 400, "expanded": True}
    ],
    "relationships": [],
})

SECURITY_BINDINGS = "[]"

SETTINGS = json.dumps({
    "QueriesExtractedForMT": False,
    "QueryLayoutSerializer": "NewSerializer",
    "UseStrictJsonDate": False,
    "EnableSuperDaxFeatures": False,
})

VERSION = json.dumps({"version": "1.19"})

METADATA = json.dumps({
    "version": "4.0",
    "createdFrom": "Template",
    "upgradeInfo": {"applicationVersion": {"major": 2, "minor": 119}},
})


def generate_pbit(output_path):
    schema = json.dumps(data_model_schema(), ensure_ascii=False)
    layout = json.dumps(build_layout(), ensure_ascii=False)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("Version",             VERSION)
        z.writestr("Settings",            SETTINGS)
        z.writestr("Metadata",            METADATA)
        z.writestr("SecurityBindings",    SECURITY_BINDINGS)
        z.writestr("DataModelSchema",     schema)
        z.writestr("DiagramLayout",       DIAGRAM_LAYOUT)
        z.writestr("Report/Layout",       layout)

    size = os.path.getsize(output_path)
    print(f"Generated: {output_path}  ({size:,} bytes)")


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "EmployeePerformanceDashboard.pbit")
    generate_pbit(out)
