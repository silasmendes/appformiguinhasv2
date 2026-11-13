# Formiguinhas — local development

Flask application using SQLite by default. Python 3.12 is recommended for the
pinned dependencies. Azure SQL and ODBC are no longer required.

From PowerShell in the repository directory, with uv installed:

```powershell
uv venv --python 3.12
uv pip install -r requirements.txt
# Optional, if you do not already have a .env:
Copy-Item .env.example .env
.venv\Scripts\python.exe manage.py --with-demo-data
.venv\Scripts\python.exe -m flask --app main run --debug
```

Open http://127.0.0.1:5000 and sign in as **admin**, using the password you
entered during initialization. Initialization can be repeated without deleting
data or changing an existing administrator's password. `SENHA_ADMIN` can also
provide the initial password through the environment or `.env`.

With `--with-demo-data`, initialization also seeds four fictitious families matching the CPFs displayed
in the appointment modal: **525.067.333-37**, **928.105.770-05**,
**955.314.618-01**, and **742.691.086-57**. Each includes address, household,
contact, housing, health, employment, income, education and appointment records.
Their names contain `(Teste)`. Run `manage.py --with-demo-data` again to add missing sample
families to an existing local database. Existing CPFs (with or without punctuation)
are skipped, preserving any edits made during testing. Without `--with-demo-data`,
initialization creates tables, lookup data and the administrator only. It never
deletes demo families that were previously created.
For the four sample CPFs, rerunning setup also repairs empty text fields saved
as SQL `NULL` or the literal `None`, replacing them with empty strings. Filled-in
values and other families are preserved.

The database files are `instance/formiguinhas.db` and `instance/precadastro.db`.
Both are ignored by Git. The pre-registration database starts empty and uses
the same SQLAlchemy table schema as the main database; family searches return
no pre-registrations until you populate it. It is independent of the main
database. Existing Azure data is not copied automatically.

An existing `.env` may be kept: legacy `DB_USER`, `DB_PASSWORD`, `DB_SERVER`, and
`DB_NAME` variables are no longer used. Optional `DATABASE_URL` and
`PRE_CADASTRO_DATABASE_URL` override the SQLite locations. Use absolute paths
and create their parent directories first when overriding them.

AI summaries use the direct OpenAI API. Set these values in your `.env`:

```dotenv
OPENAI_API_KEY=your-project-api-key
OPENAI_MODEL=gpt-5.6-luna
```

Restart Flask after changing configuration. The app calls only
`POST https://api.openai.com/v1/chat/completions`, with low reasoning effort and
a 2,000 completion-token limit (including reasoning). Use a model supporting
these parameters; ensure your project has access to the configured model.
Azure credentials, deployment names, endpoints and API versions are no longer used.
Without a key, or if a request fails, the app generates a local fallback summary;
fallbacks are not cached or saved as AI summaries. Successful summaries are reused
for up to 12 hours. Token usage is recorded locally in SQLite, without calling
OpenAI's usage or billing endpoints. Cost figures in the app are estimates.

Create a **Restricted** project API key and allow only **Model capabilities →
Chat Completions → Request/Write**, leaving every other endpoint at **None**.
The app does not need Models Read, Responses, Files, Assistants, Threads, Batch,
Fine-tuning, Images, Audio, Embeddings, Usage or administrative permissions.
Under project Limits → Model usage, allow the configured model only.
See the [official key permissions guide](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform)
and [model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

Password-reset emails require SendGrid configuration. Neither service is needed
for local login and CRUD.
The Flask debug server and default development secret are for local use only.

For a Linux VPS using Docker Compose, see [Deployment on a VPS](docs/deploy-vps.md).

Run the SQLite regression checks with:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_sqlite_local.py -q
```

These tests use temporary databases and do not modify your local development data.
`manage.py` creates missing tables; it does not migrate existing table definitions
after model changes.
