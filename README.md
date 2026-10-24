# SmartRx: AI-Assisted Allergy Screening at the Point of Dispensing

SmartRx is a Streamlit decision-support tool for pharmacists. Enter a prescribed medication, and SmartRx checks its ingredients against a database of known allergy risks, generates plain-language screening questions for the patient, and, if an allergy is confirmed, recommends a safer in-stock alternative from the same therapeutic class.

> ⚠️ **Demo project, not for clinical use.** The medication and allergy data is a small illustrative seed dataset, and AI-generated content must always be verified by a qualified pharmacist.

## Why I built it
As a pharmacist with over 20 years' experience, I know allergy checks at the point of dispensing often depend on memory and on what the patient remembers to mention. SmartRx combines structured database checks with an LLM that turns allergy data into practical questions a pharmacist can ask at the counter.

## How it works
1. **Medication lookup.** The pharmacist enters a medication name; SmartRx finds it in the inventory (case-insensitive) with its dosage form, strength, stock level and therapeutic class.
2. **Ingredient resolution.** Ingredients, including excipients, are retrieved through a many-to-many link table.
3. **Allergy risk detection.** Known allergies for those ingredients are returned and ranked **Severe → Moderate → Mild**, each with symptoms and the triggering ingredient.
4. **AI screening questions.** Google Gemini generates 3–6 plain-language Yes/No questions for the patient, plus a cross-reactivity note on risks not already in the database (e.g. penicillin–cephalosporin).
5. **Patient responses.** The pharmacist records Yes/No answers.
6. **Safer alternatives.** If an allergy is confirmed, SmartRx retrieves in-stock alternatives in the same therapeutic class, and Gemini explains each option's suitability and recommends the best pick. If no safe option exists, it advises contacting the prescriber.

## Tech stack
| Layer | Technology |
|---|---|
| Front end | Streamlit with custom CSS |
| Database | PostgreSQL (Neon serverless), accessed with psycopg2 |
| AI | Google Gemini 2.5 Flash via LangChain, with Pydantic schemas for structured output |
| Language | Python |

## Database design
Four related tables:
- **medications**: name, dosage form, strength, stock quantity, therapeutic class
- **ingredients**: active ingredients and excipients, with drug class
- **medication_ingredients**: many-to-many link between medications and ingredients
- **allergies**: allergy name, severity (Mild/Moderate/Severe) and symptoms, linked to an ingredient

The seed data covers 15 medications across penicillins, cephalosporins, macrolides, NSAIDs/aspirin, sulfonamides, opioids, tetracyclines and a paracetamol control.

## Project structure
```
├── app.py            Streamlit interface and screening workflow
├── pharmacy.py       Allergy detection pipeline (lookup → ingredients → risks → alternatives)
├── queries.py        Parameterised SQL queries
├── database.py       PostgreSQL connection handling with automatic reconnect
├── llm.py            Gemini prompts and structured-output chains
├── seed_data.sql     Schema and sample data
└── requirements.txt
```

## Running locally
1. Clone the repository and install dependencies:
```bash
   pip install -r requirements.txt
```
2. Create a PostgreSQL database (e.g. a free [Neon](https://neon.tech) project) and run `seed_data.sql` against it.
3. Add your credentials to `.streamlit/secrets.toml` (never commit this file):
```toml
   NEON_DB_CONNECTION_STRING = "postgresql://user:password@host/dbname?sslmode=require"
   GEMINI_API_KEY = "your-gemini-api-key"
```
4. Start the app:
```bash
   streamlit run app.py
```

## Design decisions
- **Database first, AI second.** Allergy risks come from structured data, not the LLM; Gemini only turns that data into questions and explanations, which reduces the risk of hallucinated allergies.
- **Structured LLM output.** Pydantic schemas make Gemini return predictable fields (questions, cross-reactivity note, analysis, recommendation) that the interface can render reliably.
- **Parameterised queries** throughout, to prevent SQL injection.
- **Secrets kept out of code.** Credentials are read from Streamlit secrets or environment variables.

## Limitations and next steps
- Small illustrative dataset; a production version would draw on a clinical source such as the NHS Dictionary of Medicines and Devices (dm+d).
- No patient records: allergies are confirmed per session through screening questions.
- Possible extensions: drug–drug interaction checks, fuzzy search for misspelt drug names, and an audit log of screening decisions.

## Author
**Emeka Chukwuma**, pharmacist (51), BPharm(Benin),MSc Health Informatics (Swansea), building toward a career in health data analysis and data engineering.
