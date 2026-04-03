-- =============================================================================
-- SmartRx — S1-T2: Seed Data
-- Run this script once against your Neon database to populate test data.
-- Covers: Penicillin, Aspirin/NSAIDs, Sulfonamides, Cephalosporins,
--         Codeine (opioid), and a safe paracetamol control.
-- =============================================================================

-- Drop tables in reverse dependency order and recreate cleanly
DROP TABLE IF EXISTS allergies CASCADE;
DROP TABLE IF EXISTS medication_ingredients CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS medications CASCADE;

-- =============================================================================
-- TABLE 1: medications
-- =============================================================================
CREATE TABLE medications (
    medication_id     SERIAL PRIMARY KEY,
    medication_name   TEXT NOT NULL,
    dosage_form       TEXT,
    strength          TEXT,
    stock_quantity    INTEGER DEFAULT 0,
    therapeutic_class TEXT
);

INSERT INTO medications (medication_name, dosage_form, strength, stock_quantity, therapeutic_class) VALUES
    ('Amoxicillin',       'Capsule',  '500mg',       120, 'Penicillin Antibiotic'),
    ('Flucloxacillin',    'Capsule',  '250mg',       80,  'Penicillin Antibiotic'),
    ('Azithromycin',      'Tablet',   '250mg',       95,  'Macrolide Antibiotic'),
    ('Clarithromycin',    'Tablet',   '500mg',       60,  'Macrolide Antibiotic'),
    ('Ibuprofen',         'Tablet',   '400mg',       200, 'NSAID'),
    ('Naproxen',          'Tablet',   '500mg',       150, 'NSAID'),
    ('Celecoxib',         'Capsule',  '200mg',       70,  'NSAID'),
    ('Co-trimoxazole',    'Tablet',   '960mg',       50,  'Sulfonamide Antibiotic'),
    ('Trimethoprim',      'Tablet',   '200mg',       90,  'Antibiotic'),
    ('Cefalexin',         'Capsule',  '500mg',       110, 'Cephalosporin Antibiotic'),
    ('Paracetamol',       'Tablet',   '500mg',       300, 'Analgesic'),
    ('Codeine Phosphate', 'Tablet',   '30mg',        40,  'Opioid Analgesic'),
    ('Dihydrocodeine',    'Tablet',   '30mg',        35,  'Opioid Analgesic'),
    ('Aspirin',           'Tablet',   '300mg',       180, 'NSAID'),
    ('Doxycycline',       'Capsule',  '100mg',       75,  'Tetracycline Antibiotic');


-- =============================================================================
-- TABLE 2: ingredients
-- =============================================================================
CREATE TABLE ingredients (
    ingredient_id    SERIAL PRIMARY KEY,
    ingredient_name  TEXT NOT NULL,
    ingredient_class TEXT
);

INSERT INTO ingredients (ingredient_name, ingredient_class) VALUES
    ('Amoxicillin',          'Penicillin'),         -- 1
    ('Flucloxacillin',       'Penicillin'),         -- 2
    ('Azithromycin',         'Macrolide'),          -- 3
    ('Clarithromycin',       'Macrolide'),          -- 4
    ('Ibuprofen',            'NSAID'),              -- 5
    ('Naproxen',             'NSAID'),              -- 6
    ('Celecoxib',            'NSAID'),              -- 7
    ('Sulfamethoxazole',     'Sulfonamide'),        -- 8
    ('Trimethoprim',         'Diaminopyrimidine'),  -- 9
    ('Cefalexin',            'Cephalosporin'),      -- 10
    ('Paracetamol',          'Analgesic'),          -- 11
    ('Codeine',              'Opioid'),             -- 12
    ('Dihydrocodeine',       'Opioid'),             -- 13
    ('Aspirin',              'Salicylate/NSAID'),   -- 14
    ('Doxycycline',          'Tetracycline'),       -- 15
    ('Microcrystalline Cellulose', 'Excipient'),    -- 16
    ('Magnesium Stearate',   'Excipient');          -- 17


-- =============================================================================
-- TABLE 3: medication_ingredients (many-to-many)
-- =============================================================================
CREATE TABLE medication_ingredients (
    medication_id  INTEGER REFERENCES medications(medication_id),
    ingredient_id  INTEGER REFERENCES ingredients(ingredient_id),
    PRIMARY KEY (medication_id, ingredient_id)
);

-- Amoxicillin (med 1)
INSERT INTO medication_ingredients VALUES (1, 1), (1, 16), (1, 17);
-- Flucloxacillin (med 2)
INSERT INTO medication_ingredients VALUES (2, 2), (2, 16), (2, 17);
-- Azithromycin (med 3)
INSERT INTO medication_ingredients VALUES (3, 3), (3, 16);
-- Clarithromycin (med 4)
INSERT INTO medication_ingredients VALUES (4, 4), (4, 16);
-- Ibuprofen (med 5)
INSERT INTO medication_ingredients VALUES (5, 5), (5, 16), (5, 17);
-- Naproxen (med 6)
INSERT INTO medication_ingredients VALUES (6, 6), (6, 16);
-- Celecoxib (med 7)
INSERT INTO medication_ingredients VALUES (7, 7), (7, 16), (7, 17);
-- Co-trimoxazole (med 8) — contains both Sulfamethoxazole AND Trimethoprim
INSERT INTO medication_ingredients VALUES (8, 8), (8, 9), (8, 16);
-- Trimethoprim (med 9)
INSERT INTO medication_ingredients VALUES (9, 9), (9, 16);
-- Cefalexin (med 10)
INSERT INTO medication_ingredients VALUES (10, 10), (10, 16), (10, 17);
-- Paracetamol (med 11)
INSERT INTO medication_ingredients VALUES (11, 11), (11, 16), (11, 17);
-- Codeine Phosphate (med 12)
INSERT INTO medication_ingredients VALUES (12, 12), (12, 11), (12, 16);
-- Dihydrocodeine (med 13)
INSERT INTO medication_ingredients VALUES (13, 13), (13, 11), (13, 16);
-- Aspirin (med 14)
INSERT INTO medication_ingredients VALUES (14, 14), (14, 16);
-- Doxycycline (med 15)
INSERT INTO medication_ingredients VALUES (15, 15), (15, 16), (15, 17);


-- =============================================================================
-- TABLE 4: allergies
-- =============================================================================
CREATE TABLE allergies (
    allergy_id     SERIAL PRIMARY KEY,
    ingredient_id  INTEGER REFERENCES ingredients(ingredient_id),
    allergy_name   TEXT,
    severity       TEXT CHECK (severity IN ('Mild', 'Moderate', 'Severe')),
    symptoms       TEXT
);

INSERT INTO allergies (ingredient_id, allergy_name, severity, symptoms) VALUES
    -- Penicillin allergies
    (1, 'Penicillin Allergy',           'Severe',   'Anaphylaxis, urticaria, angioedema, bronchospasm. Can be life-threatening within minutes of exposure.'),
    (1, 'Penicillin Rash',              'Mild',     'Maculopapular rash, itching, mild hives. Usually appears 3–10 days after starting treatment.'),
    (2, 'Penicillin Allergy',           'Severe',   'Anaphylaxis, urticaria, angioedema, bronchospasm. Can be life-threatening within minutes of exposure.'),

    -- Cephalosporin allergy (cross-reactivity with Penicillin possible)
    (10, 'Cephalosporin Allergy',       'Moderate', 'Skin rash, fever, joint pain. Note: possible cross-reactivity in patients with Penicillin allergy.'),

    -- NSAID / Aspirin allergies
    (5,  'NSAID Hypersensitivity',      'Severe',   'Bronchospasm, urticaria, angioedema. Aspirin-exacerbated respiratory disease (AERD) possible.'),
    (5,  'GI Sensitivity to NSAIDs',    'Mild',     'Nausea, stomach pain, indigestion. Risk increases with long-term use.'),
    (6,  'NSAID Hypersensitivity',      'Moderate', 'Urticaria, nasal polyps, mild bronchospasm.'),
    (7,  'Sulfa Cross-reactivity',      'Moderate', 'Celecoxib contains a sulfonamide group; patients with sulfa allergy may react.'),
    (14, 'Aspirin / Salicylate Allergy','Severe',   'Bronchospasm, anaphylaxis, severe urticaria. Cross-reacts with most NSAIDs.'),
    (14, 'Aspirin GI Intolerance',      'Mild',     'Gastric irritation, nausea, risk of GI bleed with prolonged use.'),

    -- Sulfonamide allergy
    (8,  'Sulfonamide Allergy',         'Severe',   'Stevens-Johnson Syndrome, toxic epidermal necrolysis, anaphylaxis, severe rash. Life-threatening.'),
    (8,  'Sulfa Drug Rash',             'Moderate', 'Maculopapular rash, fever, photosensitivity. Onset typically 7–14 days into treatment.'),

    -- Macrolide allergy
    (3,  'Macrolide Allergy',           'Moderate', 'Urticaria, skin rash, QT prolongation risk. GI upset common.'),
    (4,  'Macrolide Allergy',           'Moderate', 'Urticaria, skin rash, QT prolongation risk.'),

    -- Opioid allergy / intolerance
    (12, 'Opioid Hypersensitivity',     'Moderate', 'Urticaria, pruritus, hypotension. True anaphylaxis rare but possible.'),
    (12, 'Codeine Intolerance',         'Mild',     'Nausea, vomiting, constipation, dizziness. More common in ultra-rapid metabolisers.'),
    (13, 'Opioid Hypersensitivity',     'Moderate', 'Urticaria, pruritus, hypotension.'),

    -- Tetracycline allergy
    (15, 'Tetracycline Allergy',        'Moderate', 'Rash, photosensitivity, drug fever. Avoid in pregnancy and children under 12.');


-- =============================================================================
-- Quick verification queries — run these to confirm the seed worked
-- =============================================================================

-- Expected: 15 medications
SELECT COUNT(*) AS medication_count FROM medications;

-- Expected: 17 ingredients
SELECT COUNT(*) AS ingredient_count FROM ingredients;

-- Expected: 18 allergy records
SELECT COUNT(*) AS allergy_count FROM allergies;

-- Spot-check: Amoxicillin ingredients
SELECT m.medication_name, i.ingredient_name, i.ingredient_class
FROM medications m
JOIN medication_ingredients mi ON m.medication_id = mi.medication_id
JOIN ingredients i ON mi.ingredient_id = i.ingredient_id
WHERE m.medication_name = 'Amoxicillin';

-- Spot-check: allergy risks for Amoxicillin's active ingredient
SELECT a.allergy_name, a.severity, a.symptoms
FROM allergies a
JOIN ingredients i ON a.ingredient_id = i.ingredient_id
WHERE i.ingredient_name = 'Amoxicillin';