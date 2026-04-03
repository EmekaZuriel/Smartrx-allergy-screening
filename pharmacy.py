"""
pharmacy.py
-----------
Sprint 2 — Core Logic & Allergy Detection Pipeline.

All database query functions live as static methods on the Pharmacy class.
Import and call directly:

    from pharmacy import Pharmacy

    med  = Pharmacy.lookup_medication("Amoxicillin")
    ings = Pharmacy.get_ingredients(med["medication_id"])
    risks = Pharmacy.get_allergy_risks([i["ingredient_id"] for i in ings])
    alts = Pharmacy.get_alternatives(med["therapeutic_class"], med["medication_id"])
"""

from database import Database
from queries import (
    LOOKUP_MEDICATION,
    GET_INGREDIENTS,
    GET_ALLERGY_RISKS,
    GET_ALTERNATIVES,
)


class Pharmacy:

    @staticmethod
    def lookup_medication(name: str) -> dict | None:
        """
        S2-T1: Look up a medication by name (case-insensitive).

        Returns the matching medications row as a dict, or None if not found.

        Args:
            name: The medication name typed by the pharmacist.

        Returns:
            dict with keys: medication_id, medication_name, dosage_form,
                            strength, stock_quantity, therapeutic_class
            None if no match found.
        """
        return Database.fetch_one(LOOKUP_MEDICATION, (name,))

    @staticmethod
    def get_ingredients(medication_id: int) -> list[dict]:
        """
        S2-T2: Resolve all ingredients for a given medication.

        Joins medication_ingredients → ingredients via the many-to-many table.

        Args:
            medication_id: The primary key from the medications table.

        Returns:
            List of dicts with keys: ingredient_id, ingredient_name, ingredient_class
            Empty list if the medication has no ingredient records.
        """
        return Database.fetch_all(GET_INGREDIENTS, (medication_id,))

    @staticmethod
    def get_allergy_risks(ingredient_ids: list[int]) -> list[dict]:
        """
        S2-T3: Find all allergy records for a list of ingredient IDs.

        Results are ordered Severe → Moderate → Mild.

        Args:
            ingredient_ids: List of ingredient_id values from get_ingredients().

        Returns:
            List of dicts with keys: allergy_id, allergy_name, severity,
                                     symptoms, ingredient_name, ingredient_class
            Empty list if no known allergies for these ingredients.
        """
        if not ingredient_ids:
            return []
        return Database.fetch_all(GET_ALLERGY_RISKS, (ingredient_ids,))

    @staticmethod
    def get_alternatives(therapeutic_class: str, exclude_medication_id: int) -> list[dict]:
        """
        S2-T4: Find in-stock alternative medications in the same therapeutic class.

        Excludes the originally prescribed medication from the results.

        Args:
            therapeutic_class:    The drug class from the original medication row.
            exclude_medication_id: The medication_id to exclude from results.

        Returns:
            List of dicts with keys: medication_id, medication_name, dosage_form,
                                     strength, stock_quantity, therapeutic_class
            Empty list if no in-stock alternatives exist.
        """
        return Database.fetch_all(GET_ALTERNATIVES, (therapeutic_class, exclude_medication_id))

    @staticmethod
    def get_allergy_summary(medication_name: str) -> dict:
        """
        S2-T5: Run the full detection pipeline for a given medication name.

        Convenience method that chains all four steps and returns a single
        summary dict ready to hand off to the Streamlit UI and LLM layer.

        Args:
            medication_name: The medication name typed by the pharmacist.

        Returns:
            {
                "found":        bool,
                "medication":   dict | None,
                "ingredients":  list[dict],
                "risks":        list[dict],
                "alternatives": list[dict],
            }
        """
        medication = Pharmacy.lookup_medication(medication_name)

        if not medication:
            return {
                "found": False,
                "medication": None,
                "ingredients": [],
                "risks": [],
                "alternatives": [],
            }

        ingredients = Pharmacy.get_ingredients(medication["medication_id"])
        ingredient_ids = [i["ingredient_id"] for i in ingredients]
        risks = Pharmacy.get_allergy_risks(ingredient_ids)
        alternatives = (
            Pharmacy.get_alternatives(
                medication["therapeutic_class"],
                medication["medication_id"],
            )
            if risks
            else []
        )

        return {
            "found": True,
            "medication": medication,
            "ingredients": ingredients,
            "risks": risks,
            "alternatives": alternatives,
        }
