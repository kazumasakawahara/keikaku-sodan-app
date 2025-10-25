"""
PDF生成サービス

利用者情報、計画、モニタリング記録のPDF出力機能を提供します。
"""
from datetime import datetime
from io import BytesIO
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from app.models.user import User
from app.models.plan import Plan
from app.models.monitoring import Monitoring
from app.models.consultation import Consultation
from app.models.medication import Medication

import base64
from reportlab.lib.utils import ImageReader
from PIL import Image
import io


class PDFService:
    """PDF生成サービスクラス"""

    def __init__(self):
        """初期化"""
        self.page_size = A4
        self.page_width = self.page_size[0]
        self.page_height = self.page_size[1]

        # 日本語フォントの登録
        # まずCIDフォントを登録（Paragraphで使用可能）
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
        self.font_name = 'HeiseiMin-W3'  # デフォルトフォント

        try:
            # ヒラギノフォント（macOS）を試す
            pdfmetrics.registerFont(TTFont('Japanese', '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'))
            self.font_name = 'Japanese'
        except:
            try:
                # MS ゴシック（Windows）を試す
                pdfmetrics.registerFont(TTFont('Japanese', 'msgothic.ttc'))
                self.font_name = 'Japanese'
            except:
                # TTFontが使えない場合はCIDフォントを使用
                pass

    def _create_styles(self):
        """スタイルを作成"""
        styles = getSampleStyleSheet()

        # タイトルスタイル
        styles.add(ParagraphStyle(
            name='JapaneseTitle',
            fontName=self.font_name,
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20
        ))

        # 見出しスタイル
        styles.add(ParagraphStyle(
            name='JapaneseHeading',
            fontName=self.font_name,
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=10,
            textColor=colors.HexColor('#333333')
        ))

        # 本文スタイル
        styles.add(ParagraphStyle(
            name='JapaneseBody',
            fontName=self.font_name,
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6
        ))

        return styles

    def _add_header(self, canvas, doc, title: str):
        """ヘッダーを追加"""
        canvas.saveState()
        canvas.setFont(self.font_name, 9)
        canvas.drawString(20*mm, self.page_height - 15*mm, f"計画相談支援システム - {title}")
        canvas.drawString(20*mm, self.page_height - 20*mm, f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
        canvas.line(20*mm, self.page_height - 22*mm, self.page_width - 20*mm, self.page_height - 22*mm)
        canvas.restoreState()

    def _add_footer(self, canvas, doc):
        """フッターを追加"""
        canvas.saveState()
        canvas.setFont(self.font_name, 9)
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(self.page_width / 2, 15*mm, f"- {page_num} -")
        canvas.restoreState()

    def generate_user_profile_pdf(self, user: User) -> BytesIO:
        """
        利用者情報PDFを生成

        Args:
            user: 利用者モデル

        Returns:
            BytesIO: PDFデータ
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=30*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        story = []

        # タイトル（Paragraphの代わりにTableを使用）
        title_table = Table([["利用者基本情報"]], colWidths=[170*mm])
        title_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 16),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 10*mm))

        # 基本情報テーブル
        data = [
            ["氏名", user.name or ""],
            ["氏名（カナ）", user.name_kana or ""],
            ["生年月日", user.birth_date.strftime('%Y年%m月%d日') if user.birth_date else ""],
            ["年齢", f"{user.age}歳" if user.age else ""],
            ["性別", user.gender or ""],
            ["郵便番号", user.postal_code or ""],
            ["住所", user.address or ""],
            ["電話番号", user.phone or ""],
            ["メールアドレス", user.email or ""],
        ]

        table = Table(data, colWidths=[50*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
        story.append(Spacer(1, 10*mm))

        # 緊急連絡先（見出し）
        heading_table = Table([["緊急連絡先"]], colWidths=[170*mm])
        heading_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(heading_table)
        data = [
            ["氏名", user.emergency_contact_name or ""],
            ["電話番号", user.emergency_contact_phone or ""],
        ]
        table = Table(data, colWidths=[50*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
        story.append(Spacer(1, 10*mm))

        # 障害支援区分
        if user.disability_support_level:
            heading_table = Table([["障害支援区分"]], colWidths=[170*mm])
            heading_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(heading_table)
            data = [
                ["区分", f"{user.disability_support_level}" if user.disability_support_level else ""],
                ["認定日", user.disability_support_certified_date.strftime('%Y年%m月%d日') if user.disability_support_certified_date else ""],
                ["有効期限", user.disability_support_expiry_date.strftime('%Y年%m月%d日') if user.disability_support_expiry_date else ""],
            ]
            table = Table(data, colWidths=[50*mm, 120*mm])
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 10),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(table)
            story.append(Spacer(1, 10*mm))

        # 後見人情報
        if user.guardian_type:
            heading_table = Table([["後見人情報"]], colWidths=[170*mm])
            heading_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(heading_table)
            data = [
                ["種別", user.guardian_type or ""],
                ["氏名", user.guardian_name or ""],
                ["連絡先", user.guardian_contact or ""],
            ]
            table = Table(data, colWidths=[50*mm, 120*mm])
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 10),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(table)

        # PDF生成
        def add_page_decorations(canvas, doc):
            self._add_header(canvas, doc, "利用者基本情報")
            self._add_footer(canvas, doc)

        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer

    def generate_plan_pdf(self, plan: Plan) -> BytesIO:
        """
        サービス利用計画PDFを生成

        Args:
            plan: 計画モデル

        Returns:
            BytesIO: PDFデータ
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=30*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        styles = self._create_styles()
        story = []

        # タイトル
        story.append(Paragraph("サービス利用計画", styles['JapaneseTitle']))
        story.append(Spacer(1, 10*mm))

        # 基本情報
        data = [
            ["計画番号", plan.plan_number or ""],
            ["計画種別", plan.plan_type or ""],
            ["作成日", plan.created_date.strftime('%Y年%m月%d日') if plan.created_date else ""],
            ["計画期間", f"{plan.start_date.strftime('%Y年%m月%d日')} 〜 {plan.end_date.strftime('%Y年%m月%d日')}" if plan.start_date and plan.end_date else ""],
            ["承認状況", plan.approval_status or ""],
        ]

        table = Table(data, colWidths=[50*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Japanese', 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
        story.append(Spacer(1, 10*mm))

        # 利用者の状況
        story.append(Paragraph("利用者の状況", styles['JapaneseHeading']))
        story.append(Paragraph(plan.current_situation or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # 希望・ニーズ
        story.append(Paragraph("本人・家族の希望やニーズ", styles['JapaneseHeading']))
        story.append(Paragraph(plan.hopes_and_needs or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # 援助方針
        story.append(Paragraph("総合的な援助方針", styles['JapaneseHeading']))
        story.append(Paragraph(plan.support_policy or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # 目標
        story.append(Paragraph("長期目標", styles['JapaneseHeading']))
        story.append(Paragraph(f"{plan.long_term_goal or '記載なし'} ({plan.long_term_goal_period or '期間未設定'})", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        story.append(Paragraph("短期目標", styles['JapaneseHeading']))
        story.append(Paragraph(f"{plan.short_term_goal or '記載なし'} ({plan.short_term_goal_period or '期間未設定'})", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # サービス内容
        if plan.services:
            story.append(Paragraph("サービス内容", styles['JapaneseHeading']))
            service_data = [["サービス種別", "提供事業所", "頻度", "時間"]]
            for service in plan.services:
                service_data.append([
                    service.get('service_type', ''),
                    service.get('provider', ''),
                    service.get('frequency', ''),
                    service.get('hours', '')
                ])

            table = Table(service_data, colWidths=[40*mm, 50*mm, 40*mm, 40*mm])
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Japanese', 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(table)

        # PDF生成
        def add_page_decorations(canvas, doc):
            self._add_header(canvas, doc, "サービス利用計画")
            self._add_footer(canvas, doc)

        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer

    def generate_monitoring_pdf(self, monitoring: Monitoring) -> BytesIO:
        """
        モニタリング記録PDFを生成

        Args:
            monitoring: モニタリングモデル

        Returns:
            BytesIO: PDFデータ
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=30*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        styles = self._create_styles()
        story = []

        # タイトル
        story.append(Paragraph("モニタリング記録", styles['JapaneseTitle']))
        story.append(Spacer(1, 10*mm))

        # 基本情報
        data = [
            ["実施日", monitoring.monitoring_date.strftime('%Y年%m月%d日') if monitoring.monitoring_date else ""],
            ["種別", monitoring.monitoring_type or ""],
            ["満足度", monitoring.satisfaction or ""],
            ["計画変更の必要性", "必要" if monitoring.plan_revision_needed else "不要"],
            ["次回予定日", monitoring.next_monitoring_date.strftime('%Y年%m月%d日') if monitoring.next_monitoring_date else ""],
        ]

        table = Table(data, colWidths=[50*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Japanese', 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
        story.append(Spacer(1, 10*mm))

        # サービス利用状況
        story.append(Paragraph("サービス利用状況", styles['JapaneseHeading']))
        story.append(Paragraph(monitoring.service_usage_status or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # 目標達成状況
        story.append(Paragraph("目標達成状況", styles['JapaneseHeading']))
        story.append(Paragraph(monitoring.goal_achievement or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # ニーズの変化
        story.append(Paragraph("ニーズの変化", styles['JapaneseHeading']))
        story.append(Paragraph(monitoring.changes_in_needs or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # 課題・問題点
        story.append(Paragraph("課題・問題点", styles['JapaneseHeading']))
        story.append(Paragraph(monitoring.issues_and_concerns or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # 今後の方針
        story.append(Paragraph("今後の方針", styles['JapaneseHeading']))
        story.append(Paragraph(monitoring.future_policy or "記載なし", styles['JapaneseBody']))

        # PDF生成
        def add_page_decorations(canvas, doc):
            self._add_header(canvas, doc, "モニタリング記録")
            self._add_footer(canvas, doc)

        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer

    def generate_consultation_pdf(self, consultation: Consultation) -> BytesIO:
        """
        相談記録PDFを生成

        Args:
            consultation: 相談記録モデル

        Returns:
            BytesIO: PDFデータ
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=30*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        styles = self._create_styles()
        story = []

        # タイトル
        story.append(Paragraph("相談記録", styles['JapaneseTitle']))
        story.append(Spacer(1, 10*mm))

        # 基本情報
        data = [
            ["相談日", consultation.consultation_date.strftime('%Y年%m月%d日') if consultation.consultation_date else ""],
            ["相談形態", consultation.consultation_type or ""],
        ]

        table = Table(data, colWidths=[50*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Japanese', 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
        story.append(Spacer(1, 10*mm))

        # 相談内容
        story.append(Paragraph("相談内容", styles['JapaneseHeading']))
        story.append(Paragraph(consultation.content or "記載なし", styles['JapaneseBody']))
        story.append(Spacer(1, 5*mm))

        # 対応内容
        story.append(Paragraph("対応内容", styles['JapaneseHeading']))
        story.append(Paragraph(consultation.response or "記載なし", styles['JapaneseBody']))

        # PDF生成
        def add_page_decorations(canvas, doc):
            self._add_header(canvas, doc, "相談記録")
            self._add_footer(canvas, doc)

        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer

    def generate_network_pdf(self, image_data: str, user_name: str) -> BytesIO:
        """
        ネットワーク図PDFを生成

        Args:
            image_data: Base64エンコードされた画像データ（PNG形式）
            user_name: 利用者名

        Returns:
            BytesIO: PDFデータ
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=30*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        styles = self._create_styles()
        story = []

        # タイトル
        story.append(Paragraph(f"ネットワーク図 - {user_name}", styles['JapaneseTitle']))
        story.append(Spacer(1, 10*mm))

        # Base64画像をPDFに埋め込み
        try:
            # Base64データからヘッダーを削除
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]

            # Base64デコード
            img_bytes = base64.b64decode(image_data)
            img_buffer = io.BytesIO(img_bytes)

            # PILで画像を開く
            img = Image.open(img_buffer)

            # ページサイズに合わせてスケーリング
            available_width = self.page_width - 40*mm
            available_height = self.page_height - 100*mm

            img_width = img.width
            img_height = img.height

            # アスペクト比を維持してスケーリング
            scale_w = available_width / img_width
            scale_h = available_height / img_height
            scale = min(scale_w, scale_h, 1.0)

            new_width = img_width * scale
            new_height = img_height * scale

            # ReportLabのImageReaderに変換
            img_buffer.seek(0)
            img_reader = ImageReader(img_buffer)

            # Tableを使って画像を中央配置
            from reportlab.platypus import Image as RLImage
            rl_image = RLImage(img_buffer, width=new_width, height=new_height)
            story.append(rl_image)

        except Exception as e:
            story.append(Paragraph(f"ネットワーク図の変換エラー: {str(e)}", styles['JapaneseBody']))

        # PDF生成
        def add_page_decorations(canvas, doc):
            self._add_header(canvas, doc, f"ネットワーク図 - {user_name}")
            self._add_footer(canvas, doc)

        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer

    def generate_medications_pdf(self, user: User, medications: list) -> BytesIO:
        """
        服薬情報一覧PDFを生成

        Args:
            user: 利用者モデル
            medications: 服薬情報リスト

        Returns:
            BytesIO: PDFデータ
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            topMargin=30*mm,
            bottomMargin=20*mm,
            leftMargin=20*mm,
            rightMargin=20*mm
        )

        story = []

        # タイトル
        title_table = Table([[f"服薬情報一覧 - {user.name}"]], colWidths=[170*mm])
        title_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 16),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 10*mm))

        # 利用者基本情報
        user_info_table = Table([["利用者基本情報"]], colWidths=[170*mm])
        user_info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(user_info_table)

        user_data = [
            ["氏名", user.name or ""],
            ["生年月日", user.birth_date.strftime('%Y年%m月%d日') if user.birth_date else ""],
            ["年齢", f"{user.age}歳" if user.age else ""],
        ]
        user_table = Table(user_data, colWidths=[50*mm, 120*mm])
        user_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 10*mm))

        # 現在服用中の薬
        current_medications = [m for m in medications if m.is_current]
        if current_medications:
            heading_table = Table([["現在服用中の薬"]], colWidths=[170*mm])
            heading_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(heading_table)

            med_data = [["薬品名", "用量", "回数", "タイミング", "処方医", "開始日"]]
            for med in current_medications:
                doctor_name = med.prescribing_doctor.name if med.prescribing_doctor else ""
                start_date = med.start_date.strftime('%Y/%m/%d') if med.start_date else ""
                med_data.append([
                    med.medication_name or "",
                    med.dosage or "",
                    med.frequency or "",
                    med.timing or "",
                    doctor_name,
                    start_date
                ])

            med_table = Table(med_data, colWidths=[40*mm, 25*mm, 25*mm, 25*mm, 30*mm, 25*mm])
            med_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c8e6c9')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(med_table)
            story.append(Spacer(1, 10*mm))

        # 過去の服薬情報
        past_medications = [m for m in medications if not m.is_current]
        if past_medications:
            heading_table = Table([["過去の服薬情報"]], colWidths=[170*mm])
            heading_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(heading_table)

            past_data = [["薬品名", "用量", "処方医", "開始日", "終了日"]]
            for med in past_medications:
                doctor_name = med.prescribing_doctor.name if med.prescribing_doctor else ""
                start_date = med.start_date.strftime('%Y/%m/%d') if med.start_date else ""
                end_date = med.end_date.strftime('%Y/%m/%d') if med.end_date else ""
                past_data.append([
                    med.medication_name or "",
                    med.dosage or "",
                    doctor_name,
                    start_date,
                    end_date
                ])

            past_table = Table(past_data, colWidths=[45*mm, 30*mm, 35*mm, 30*mm, 30*mm])
            past_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(past_table)

        # 服薬情報がない場合
        if not medications:
            no_data_table = Table([["現在、登録されている服薬情報はありません。"]], colWidths=[170*mm])
            no_data_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ]))
            story.append(no_data_table)

        # PDF生成
        def add_page_decorations(canvas, doc):
            self._add_header(canvas, doc, f"服薬情報一覧 - {user.name}")
            self._add_footer(canvas, doc)

        doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
        buffer.seek(0)
        return buffer
