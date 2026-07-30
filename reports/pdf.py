from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO


COLOR_PRIMARY = colors.HexColor("#334155")    
COLOR_MUTED = colors.HexColor("#64748b")      
COLOR_BORDER = colors.HexColor("#e2e8f0")     
COLOR_BG_LIGHT = colors.HexColor("#f8fafc")   
COLOR_ACCENT = colors.HexColor("#4f46e5")     
COLOR_SUCCESS = colors.HexColor("#10b981")    
COLOR_DANGER = colors.HexColor("#ef4444")     


CATEGORY_COLORS = {
    "salary": {"bg": "#ecfdf5", "text": "#065f46"},
    "freelancing": {"bg": "#e0f2fe", "text": "#0369a1"},
    "business": {"bg": "#f5f3ff", "text": "#5b21b6"},
    "investment": {"bg": "#fef3c7", "text": "#92400e"},
    "gift": {"bg": "#fce7f3", "text": "#9d174d"},
    "food": {"bg": "#fef3c7", "text": "#d97706"},
    "transport": {"bg": "#e0f2fe", "text": "#0284c7"},
    "shopping": {"bg": "#fce7f3", "text": "#db2777"},
    "bills": {"bg": "#fee2e2", "text": "#dc2626"},
    "entertainment": {"bg": "#f3e8ff", "text": "#9333ea"},
    "health": {"bg": "#dcfce7", "text": "#16a34a"},
    "education": {"bg": "#e0e7ff", "text": "#4f46e5"},
    "travel": {"bg": "#ccfbf1", "text": "#0d9488"},
    "mobile": {"bg": "#ffedd5", "text": "#ea580c"},
    "software": {"bg": "#fae8ff", "text": "#c026d3"},
    "other": {"bg": "#f3f4f6", "text": "#4b5563"},
}

PAYMENT_METHOD_COLORS = {
    "cash": {"bg": "#dcfce7", "text": "#15803d"},
    "bank_transfer": {"bg": "#e0f2fe", "text": "#0369a1"},
    "debit_card": {"bg": "#e0f7fa", "text": "#00838f"},
    "credit_card": {"bg": "#e0e7ff", "text": "#4338ca"},
    "jazzcash": {"bg": "#fef2f2", "text": "#dc2626"},
    "easypaisa": {"bg": "#f0fdf4", "text": "#16a34a"},
    "other": {"bg": "#f3f4f6", "text": "#4b5563"},
}

def make_badge(text, color_map):
    key = str(text).lower().replace(" ", "_")
    theme = color_map.get(key, {"bg": "#f3f4f6", "text": "#4b5563"})
    
    badge_style = ParagraphStyle(
        'BadgeText',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=1, # Centered
        textColor=colors.HexColor(theme["text"])
    )
    
    p = Paragraph(text.title(), badge_style)
    t = Table([[p]], colWidths=[90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(theme["bg"])),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t

def generate_report_pdf(*, username, report_title, report_period, report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    story = []

    style_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=COLOR_PRIMARY)
    style_subtitle = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=COLOR_MUTED, spaceAfter=20)
    style_h2 = ParagraphStyle('SectionHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=COLOR_PRIMARY, spaceBefore=18, spaceAfter=10)

    story.append(Paragraph(report_title, style_title))
    story.append(Paragraph(f"Aggregate financial statement for {report_period} — Prepared for {username}", style_subtitle))

    story.append(Paragraph("Financial Summary", style_h2))
    
    formatted_income = f"+Rs {int(report['total_income']):,}"
    formatted_expense = f"-Rs {int(report['total_expense']):,}"
    net_profit = report["net_profit"]
    formatted_net = f"+Rs {int(net_profit):,}" if net_profit >= 0 else f"-Rs {abs(int(net_profit)):,}"

    card_label = ParagraphStyle('CardLabel', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=COLOR_MUTED)
    card_inc_val = ParagraphStyle('CardIncVal', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=COLOR_SUCCESS)
    card_exp_val = ParagraphStyle('CardExpVal', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=COLOR_DANGER)
    card_net_val = ParagraphStyle('CardNetVal', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=COLOR_SUCCESS if net_profit >= 0 else COLOR_DANGER)
    card_sub = ParagraphStyle('CardSub', fontName='Helvetica', fontSize=8, leading=10, textColor=COLOR_MUTED)

    summary_data = [
        [
            Paragraph("TOTAL INCOME", card_label), "",
            Paragraph("TOTAL EXPENSE", card_label), "",
            Paragraph("NET PROFIT / LOSS", card_label)
        ],
        [
            Paragraph(formatted_income, card_inc_val), "",
            Paragraph(formatted_expense, card_exp_val), "",
            Paragraph(formatted_net, card_net_val)
        ],
        [
            Paragraph(f"{report['income_count']} transactions", card_sub), "",
            Paragraph(f"{report['expense_count']} transactions", card_sub), "",
            Paragraph("Net Statement Balance", card_sub)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[158, 15, 158, 15, 158])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('BACKGROUND', (0, 0), (0, -1), COLOR_BG_LIGHT),
        ('LINELEFT', (0, 0), (0, -1), 3, COLOR_SUCCESS),
        ('BOX', (0, 0), (0, -1), 1, COLOR_BORDER),
        ('BACKGROUND', (2, 0), (2, -1), COLOR_BG_LIGHT),
        ('LINELEFT', (2, 0), (2, -1), 3, COLOR_DANGER),
        ('BOX', (2, 0), (2, -1), 1, COLOR_BORDER),
        ('BACKGROUND', (4, 0), (4, -1), COLOR_BG_LIGHT),
        ('LINELEFT', (4, 0), (4, -1), 3, COLOR_ACCENT if net_profit >= 0 else COLOR_DANGER),
        ('BOX', (4, 0), (4, -1), 1, COLOR_BORDER),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.25 * inch))
    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=COLOR_MUTED)
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=9, leading=12, textColor=COLOR_PRIMARY)
    td_muted = ParagraphStyle('TDMuted', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=COLOR_MUTED)
    td_income_amt = ParagraphStyle('TDIncAmt', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=COLOR_SUCCESS, alignment=2)
    td_expense_amt = ParagraphStyle('TDExpAmt', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=COLOR_DANGER, alignment=2)

    
    story.append(Paragraph("Income Breakdown", style_h2))
    income_data = [[Paragraph("DATE", th_style), Paragraph("TITLE", th_style), Paragraph("CATEGORY", th_style), Paragraph("AMOUNT", th_style)]]

    for income in report["income_queryset"]:
        formatted_date = income.date.strftime("%B %d, %Y") if isinstance(income.date, datetime) else str(income.date)
        income_data.append([
            Paragraph(formatted_date, td_muted),
            Paragraph(str(income.title), td_style),
            make_badge(str(income.category), CATEGORY_COLORS), 
            Paragraph(f"+Rs {int(income.amount):,}", td_income_amt),
        ])

    income_table = Table(income_data, colWidths=[100, 204, 100, 100])
    income_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BG_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, COLOR_PRIMARY),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(income_table)
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("Expense Breakdown", style_h2))
    expense_data = [[Paragraph("DATE", th_style), Paragraph("TITLE", th_style), Paragraph("CATEGORY", th_style), Paragraph("PAYMENT METHOD", th_style), Paragraph("AMOUNT", th_style)]]

    for expense in report["expense_queryset"]:
        formatted_date = expense.date.strftime("%B %d, %Y") if isinstance(expense.date, datetime) else str(expense.date)
        expense_data.append([
            Paragraph(formatted_date, td_muted),
            Paragraph(str(expense.title), td_style),
            make_badge(expense.get_category_display(), CATEGORY_COLORS),              
            make_badge(expense.get_payment_method_display(), PAYMENT_METHOD_COLORS),  
            Paragraph(f"-Rs {int(expense.amount):,}", td_expense_amt),
        ])

    expense_table = Table(expense_data, colWidths=[90, 134, 100, 100, 80])
    expense_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_BG_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, COLOR_PRIMARY),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, COLOR_BORDER),
    ]))
    story.append(expense_table)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf