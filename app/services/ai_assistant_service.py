"""
AI計画作成支援サービス

Ollama ローカルLLMを使用したサービス利用計画の作成支援機能を提供します。
"""
import ollama
from typing import Dict, Any, Optional, List
import json
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.plan import Plan
from app.models.plan_evaluation import PlanEvaluation
from app.models.consultation import Consultation
from app.models.medication import Medication


class OllamaAIAssistantService:
    """Ollama ローカルLLMを使用した計画作成支援サービス"""

    def __init__(self, db: Session, model: str = "llama3"):
        """
        初期化

        Args:
            db: データベースセッション
            model: 使用するOllamaモデル名
        """
        self.db = db
        self.model = model

    def generate_plan_proposal(
        self,
        user_id: int,
        previous_plan_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        利用者情報を総合的に分析し、計画案を生成

        Args:
            user_id: 利用者ID
            previous_plan_id: 前回の計画ID(任意)

        Returns:
            生成された計画提案とメタ情報

        Raises:
            ValueError: 利用者が見つからない場合
        """
        # コンテキストデータを収集
        context_data = self._gather_context_data(user_id, previous_plan_id)

        # プロンプトを構築
        prompt = self._build_prompt(context_data)

        # Ollamaを呼び出し
        response = self._call_ollama(prompt)

        # レスポンスをパース
        parsed_response = self._parse_response(response)

        return {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "model_used": self.model,
            "proposal": parsed_response,
            "data_sources": {
                "user_profile": True,
                "disability_info": context_data.get("disability_info") is not None,
                "medications": len(context_data.get("medications", [])) > 0,
                "previous_plan": previous_plan_id is not None,
                "previous_evaluation": context_data.get("previous_evaluation") is not None,
                "consultations": len(context_data.get("consultations", [])) > 0
            }
        }

    def _gather_context_data(
        self,
        user_id: int,
        previous_plan_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        計画作成に必要なコンテキストデータを収集

        Args:
            user_id: 利用者ID
            previous_plan_id: 前回の計画ID(任意)

        Returns:
            収集されたコンテキストデータ

        Raises:
            ValueError: 利用者が見つからない場合
        """
        # 利用者基本情報を取得
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"利用者ID {user_id} が見つかりません")

        context = {
            "user_profile": {
                "name": user.name,
                "age": user.age,
                "gender": user.gender,
                "disability_support_level": user.disability_support_level,
            },
            "disability_info": None,
            "medications": [],
            "consultations": [],
            "previous_plan": None,
            "previous_evaluation": None
        }

        # 障害特性・興味の偏り情報
        if user.disability_characteristics or user.interest_bias:
            context["disability_info"] = {
                "characteristics": user.disability_characteristics,
                "interests": user.interest_bias
            }

        # 服薬情報を取得
        medications = self.db.query(Medication).filter(
            Medication.user_id == user_id,
            Medication.is_current == True
        ).all()

        context["medications"] = [
            {
                "name": med.medication_name,
                "purpose": med.purpose,
                "dosage": med.dosage,
                "frequency": med.frequency
            }
            for med in medications
        ]

        # 最近の相談記録を取得(直近5件)
        consultations = self.db.query(Consultation).filter(
            Consultation.user_id == user_id
        ).order_by(Consultation.consultation_date.desc()).limit(5).all()

        context["consultations"] = [
            {
                "date": cons.consultation_date.isoformat(),
                "type": cons.consultation_type,
                "content": cons.content
            }
            for cons in consultations
        ]

        # 前回の計画と評価を取得
        if previous_plan_id:
            previous_plan = self.db.query(Plan).filter(Plan.id == previous_plan_id).first()
            if previous_plan:
                context["previous_plan"] = {
                    "start_date": previous_plan.start_date.isoformat(),
                    "end_date": previous_plan.end_date.isoformat(),
                    "current_situation": previous_plan.current_situation,
                    "hopes_and_needs": previous_plan.hopes_and_needs,
                    "support_policy": previous_plan.support_policy,
                    "long_term_goal": previous_plan.long_term_goal,
                    "short_term_goal": previous_plan.short_term_goal,
                    "services": previous_plan.services
                }

                # 前回計画の評価を取得
                evaluation = self.db.query(PlanEvaluation).filter(
                    PlanEvaluation.plan_id == previous_plan_id
                ).order_by(PlanEvaluation.evaluation_date.desc()).first()

                if evaluation:
                    context["previous_evaluation"] = {
                        "achievement_status": evaluation.achievement_status,
                        "achievement_details": evaluation.achievement_details,
                        "overall_evaluation": evaluation.overall_evaluation,
                        "challenges": evaluation.challenges,
                        "next_actions": evaluation.next_actions
                    }

        return context

    def _build_prompt(self, context_data: Dict[str, Any]) -> str:
        """
        Ollama用のプロンプトを構築

        Args:
            context_data: コンテキストデータ

        Returns:
            構築されたプロンプト文字列
        """
        user_profile = context_data["user_profile"]
        disability_info = context_data.get("disability_info")
        medications = context_data.get("medications", [])
        consultations = context_data.get("consultations", [])
        previous_plan = context_data.get("previous_plan")
        previous_evaluation = context_data.get("previous_evaluation")

        prompt = f"""あなたは経験豊富な計画相談支援専門員です。以下の情報をもとに、利用者のサービス利用計画を提案してください。

# 利用者基本情報
- 年齢: {user_profile['age']}歳
- 性別: {user_profile['gender'] or '未登録'}
- 障害支援区分: {f"区分{user_profile['disability_support_level']}" if user_profile['disability_support_level'] else '未設定'}

"""

        # 障害特性・興味の偏り
        if disability_info:
            prompt += "# 障害特性・興味の偏り\n"
            if disability_info.get("characteristics"):
                prompt += f"【障害特性】\n{disability_info['characteristics']}\n\n"
            if disability_info.get("interests"):
                prompt += f"【興味の偏り】\n{disability_info['interests']}\n\n"

        # 服薬情報
        if medications:
            prompt += "# 服薬情報\n"
            for med in medications:
                prompt += f"- {med['name']}"
                if med.get('purpose'):
                    prompt += f" ({med['purpose']})"
                if med.get('dosage'):
                    prompt += f" - {med['dosage']}"
                if med.get('frequency'):
                    prompt += f" - {med['frequency']}"
                prompt += "\n"
            prompt += "\n"

        # 最近の相談記録
        if consultations:
            prompt += "# 最近の相談記録\n"
            for cons in consultations[:3]:  # 最新3件のみ
                prompt += f"【{cons['date']}】\n{cons['content']}\n\n"

        # 前回計画の情報
        if previous_plan:
            prompt += "# 前回の計画\n"
            prompt += f"期間: {previous_plan['start_date']} ～ {previous_plan['end_date']}\n\n"

            if previous_plan.get('current_situation'):
                prompt += f"【前回の状況】\n{previous_plan['current_situation']}\n\n"

            if previous_plan.get('long_term_goal'):
                prompt += f"【前回の長期目標】\n{previous_plan['long_term_goal']}\n\n"

            if previous_plan.get('short_term_goal'):
                prompt += f"【前回の短期目標】\n{previous_plan['short_term_goal']}\n\n"

        # 前回計画の評価
        if previous_evaluation:
            prompt += "# 前回計画の評価\n"
            prompt += f"達成状況: {previous_evaluation['achievement_status']}\n\n"

            if previous_evaluation.get('achievement_details'):
                prompt += f"【達成状況詳細】\n{previous_evaluation['achievement_details']}\n\n"

            if previous_evaluation.get('challenges'):
                prompt += f"【課題・問題点】\n{previous_evaluation['challenges']}\n\n"

            if previous_evaluation.get('next_actions'):
                prompt += f"【次期計画への提言】\n{previous_evaluation['next_actions']}\n\n"

        # 回答フォーマットの指示
        prompt += """
# 以下の形式で計画を提案してください

【現在の状況】
(利用者の現状を100-200文字程度で記述)

【本人・家族の希望やニーズ】
(希望やニーズを100-200文字程度で記述)

【総合的な援助方針】
(援助の基本方針を150-250文字程度で記述)

【長期目標】
(6ヶ月～1年後の目標を80-150文字程度で記述)

【短期目標】
(3ヶ月程度の目標を80-150文字程度で記述)

【推奨サービス】
1. サービス種別名 - 提供内容(簡潔に)
2. サービス種別名 - 提供内容(簡潔に)
(必要に応じて3～5つ程度)

※具体的で実現可能な内容にしてください
※利用者の特性や状況に配慮した提案をしてください
"""

        return prompt

    def _call_ollama(self, prompt: str) -> str:
        """
        Ollama APIを呼び出し

        Args:
            prompt: 生成用プロンプト

        Returns:
            生成されたテキスト
        """
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'あなたは経験豊富な計画相談支援専門員です。利用者の状況を総合的に判断し、具体的で実現可能なサービス利用計画を提案してください。必ず日本語で回答してください。'
                    },
                    {
                        'role': 'user',
                        'content': prompt + '\n\n※必ず日本語で回答してください。'
                    }
                ],
                options={
                    'temperature': 0.7,  # 創造性と一貫性のバランス
                    'top_p': 0.9,
                    'top_k': 40,
                }
            )
            return response['message']['content']
        except Exception as e:
            raise Exception(f"Ollama呼び出しエラー: {str(e)}")

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Ollamaのレスポンスをパース

        Args:
            response: Ollamaからのレスポンステキスト

        Returns:
            パースされた計画提案
        """
        # セクションごとに分割
        sections = {
            "current_situation": "",
            "hopes_and_needs": "",
            "support_policy": "",
            "long_term_goal": "",
            "short_term_goal": "",
            "recommended_services": [],
            "raw_response": response
        }

        # 簡易的なパース(改善の余地あり)
        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if '【現在の状況】' in line or '現在の状況' in line:
                current_section = 'current_situation'
                continue
            elif '【本人・家族の希望やニーズ】' in line or '希望やニーズ' in line:
                current_section = 'hopes_and_needs'
                continue
            elif '【総合的な援助方針】' in line or '援助方針' in line:
                current_section = 'support_policy'
                continue
            elif '【長期目標】' in line or '長期目標' in line:
                current_section = 'long_term_goal'
                continue
            elif '【短期目標】' in line or '短期目標' in line:
                current_section = 'short_term_goal'
                continue
            elif '【推奨サービス】' in line or '推奨サービス' in line:
                current_section = 'recommended_services'
                continue

            # 内容を追加
            if current_section and line:
                if current_section == 'recommended_services':
                    # サービスはリストとして保存
                    if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')):
                        sections[current_section].append(line)
                else:
                    # その他のセクションはテキストとして結合
                    if sections[current_section]:
                        sections[current_section] += ' '
                    sections[current_section] += line

        return sections

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        利用可能なOllamaモデルのリストを取得

        Returns:
            モデル情報のリスト
        """
        try:
            models_response = ollama.list()
            models_list = models_response.get('models', [])
            return [
                {
                    "name": model.get('name', model.get('model', 'Unknown')),
                    "size": str(model.get('size', 'Unknown')),
                    "modified": str(model.get('modified_at', model.get('modified', 'Unknown')))
                }
                for model in models_list
            ]
        except Exception as e:
            raise Exception(f"モデル一覧取得エラー: {str(e)}")
