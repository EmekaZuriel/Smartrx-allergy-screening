import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


# ── Output schemas ─────────────────────────────────────────────────────────────

class ScreeningOutput(BaseModel):
    questions: list[str] = Field(
        description=(
            "3–6 plain-language Yes/No questions for the pharmacist to ask "
            "the patient, each mapping to at least one known allergy risk"
        )
    )
    cross_reactivity_note: str = Field(
        description=(
            "Brief note (1–3 sentences) on cross-reactivity risks not already "
            "in the database list. Set to 'None identified.' if none apply."
        )
    )


class RecommendationOutput(BaseModel):
    analysis: str = Field(
        description=(
            "Per-alternative analysis: 1–2 sentences per alternative explaining "
            "its suitability given the patient's confirmed allergy profile"
        )
    )
    recommendation: str = Field(
        description=(
            "Single-sentence final recommendation naming the best alternative "
            "and why, or stating that no safe option exists"
        )
    )


# ── Prompts ────────────────────────────────────────────────────────────────────

_SCREENING_SYSTEM = (
    "You are a clinical decision support assistant helping a pharmacist screen a patient "
    "for potential allergic reactions before dispensing a medication. "
    "Keep all language simple and direct. Avoid medical jargon."
)

_SCREENING_USER = """\
MEDICATION BEING DISPENSED:
{medication_name}

INGREDIENTS IN THIS MEDICATION:
{ingredients}

KNOWN ALLERGY RISKS FROM THE DATABASE (most severe first):
{allergy_risks}

Write 3–6 Yes/No screening questions the pharmacist should ask the patient before \
dispensing. Each question must map to at least one of the allergy risks listed above.

Then provide a brief cross-reactivity note flagging any additional allergy or intolerance \
risks NOT in the database list but known to be associated with this medication's ingredient \
classes. Keep it to 1–3 sentences. If none apply, set cross_reactivity_note to \
"None identified."
"""

_RECOMMENDATION_SYSTEM = (
    "You are a clinical decision support assistant helping a pharmacist choose a safer "
    "alternative medication for a patient with confirmed allergies. "
    "Write directly to the pharmacist. Keep all language simple."
)

_RECOMMENDATION_USER = """\
ORIGINAL MEDICATION:
{medication_name}

CONFIRMED ALLERGY RISKS FOR THIS PATIENT:
{confirmed_allergies}

IN-STOCK ALTERNATIVES FROM THE SAME THERAPEUTIC CLASS:
{alternatives}

For each alternative, explain in 1–2 plain sentences why it is or is not a safer choice \
given the patient's confirmed allergy profile. Flag any cross-reactive ingredient classes \
clearly.

End with a single recommendation sentence naming the best option and why. If no safe \
alternative exists, say so clearly.
"""


# ── Model singleton + chains ───────────────────────────────────────────────────

class LLM:

    _model = None

    @staticmethod
    def _get_model() -> ChatGoogleGenerativeAI:
        if LLM._model is None:
            api_key = os.getenv("GEMINI_API_KEY")

            if not api_key:
                try:
                    import streamlit as st
                    api_key = st.secrets["GEMINI_API_KEY"]
                except Exception:
                    pass

            if not api_key:
                raise ValueError(
                    "Gemini API key not found. "
                    "Set GEMINI_API_KEY in your .env file or Streamlit secrets.toml."
                )

            LLM._model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                temperature=0.3,
            )

        return LLM._model

    # -------------------------------------------------------------------------
    # Chain 1 — Screening Question Generation
    # ----------------------------
    @staticmethod
    def generate_screening_questions(
        medication_name: str,
        ingredients: list[dict],
        risks: list[dict],
    ) -> ScreeningOutput:
        """
        S3-T2: Generate structured screening questions from DB allergy data.

        Returns:
            ScreeningOutput with:
              .questions             — list of Yes/No question strings
              .cross_reactivity_note — clinical cross-reactivity note string
        """
        if not risks:
            return ScreeningOutput(questions=[], cross_reactivity_note="")

        ingredients_text = "\n".join(
            f"  - {i['ingredient_name']} ({i['ingredient_class']})"
            for i in ingredients
        )
        risks_text = "\n".join(
            f"  - [{r['severity']}] {r['allergy_name']} "
            f"(triggered by {r['ingredient_name']}): {r['symptoms']}"
            for r in risks
        )

        messages = [
            {"role": "system", "content": _SCREENING_SYSTEM},
            {
                "role": "user",
                "content": _SCREENING_USER.format(
                    medication_name=medication_name,
                    ingredients=ingredients_text,
                    allergy_risks=risks_text,
                ),
            },
        ]

        return LLM._get_model().with_structured_output(ScreeningOutput).invoke(messages)

    # -------------------------------------------------------------------------
    # Chain 2 — Alternative Medication Recommendation
    # -------------------------------------------------------------------------
    @staticmethod
    def generate_alternative_recommendation(
        medication_name: str,
        confirmed_allergies: list[str],
        alternatives: list[dict],
    ) -> RecommendationOutput:
        """
        S3-T3: Explain which alternative medications are safer and why.

        Returns:
            RecommendationOutput with:
              .analysis        — per-alternative reasoning paragraph
              .recommendation  — single best-pick sentence
        """
        if not alternatives:
            return RecommendationOutput(
                analysis="No in-stock alternatives were found in the same therapeutic class.",
                recommendation="Please consult with the prescribing physician before dispensing.",
            )

        allergies_text = "\n".join(f"  - {a}" for a in confirmed_allergies)
        alternatives_text = "\n".join(
            f"  - {a['medication_name']} | {a['dosage_form']} | "
            f"{a['strength']} | {a['stock_quantity']} units in stock"
            for a in alternatives
        )

        messages = [
            {"role": "system", "content": _RECOMMENDATION_SYSTEM},
            {
                "role": "user",
                "content": _RECOMMENDATION_USER.format(
                    medication_name=medication_name,
                    confirmed_allergies=allergies_text,
                    alternatives=alternatives_text,
                ),
            },
        ]

        return LLM._get_model().with_structured_output(RecommendationOutput).invoke(messages)
        
