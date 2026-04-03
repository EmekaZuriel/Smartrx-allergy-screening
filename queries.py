# queries.py
# All SQL queries used by SmartRx, stored as constants.
# These are passed directly to Database.fetch_one() / Database.fetch_all().

# ---------------------------------------------------------------------------
# S1-T4a: Look up a medication by name (case-insensitive)
# Returns a single medication row or None.
# Usage: Database.fetch_one(LOOKUP_MEDICATION, (name,))
# ---------------------------------------------------------------------------
LOOKUP_MEDICATION = """
    SELECT medication_id, medication_name, dosage_form, strength,
           stock_quantity, therapeutic_class
    FROM medications
    WHERE LOWER(medication_name) = LOWER(%s)
"""

# ---------------------------------------------------------------------------
# S1-T4b: Get all ingredients for a given medication_id
# Joins medication_ingredients → ingredients via the many-to-many table.
# Usage: Database.fetch_all(GET_INGREDIENTS, (medication_id,))
# ---------------------------------------------------------------------------
GET_INGREDIENTS = """
    SELECT i.ingredient_id, i.ingredient_name, i.ingredient_class
    FROM ingredients i
    JOIN medication_ingredients mi ON i.ingredient_id = mi.ingredient_id
    WHERE mi.medication_id = %s
"""

# ---------------------------------------------------------------------------
# S1-T4c: Get all allergy records for a list of ingredient_ids
# Results are ordered Severe → Moderate → Mild.
# Usage: Database.fetch_all(GET_ALLERGY_RISKS, (ingredient_ids_tuple,))
# Note: pass ingredient_ids as a tuple, e.g. (1, 2, 3)
# ---------------------------------------------------------------------------
GET_ALLERGY_RISKS = """
    SELECT a.allergy_id, a.allergy_name, a.severity, a.symptoms,
           i.ingredient_name, i.ingredient_class
    FROM allergies a
    JOIN ingredients i ON a.ingredient_id = i.ingredient_id
    WHERE a.ingredient_id = ANY(%s)
    ORDER BY
        CASE a.severity
            WHEN 'Severe'   THEN 1
            WHEN 'Moderate' THEN 2
            WHEN 'Mild'     THEN 3
            ELSE 4
        END
"""

# ---------------------------------------------------------------------------
# S1-T4d: Get in-stock alternative medications in the same therapeutic class,
# excluding the originally prescribed medication.
# Usage: Database.fetch_all(GET_ALTERNATIVES, (therapeutic_class, medication_id))
# ---------------------------------------------------------------------------
GET_ALTERNATIVES = """
    SELECT medication_id, medication_name, dosage_form, strength,
           stock_quantity, therapeutic_class
    FROM medications
    WHERE therapeutic_class = %s
      AND medication_id != %s
      AND stock_quantity > 0
    ORDER BY medication_name
"""