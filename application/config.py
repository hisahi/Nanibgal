
# Database configuration
# Ignored if run in an Heroku instance
DATABASE_URL = "postgresql://postgres:postgres@localhost/postgres"

# Debug mode.
# Do not enable unless you know what you are doing.
DEBUG = True

# Public mode.
# PUBLIC = True is not recommended on Flask dev server.
PUBLIC = False

# Port to run on.
PORT = 5000

# List of available languages. Key has the language code and value the
# native name of that language.
LANGUAGES = {"en": "English", "fi": "Suomi"}
if DEBUG:
    LANGUAGES["qqx"] = "language.string.codes"
