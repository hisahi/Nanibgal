
# Database configuration (Nanibgal is designed for PostgreSQL)
# Ignored if run in an Heroku instance
DATABASE_URL = "postgresql://postgres:postgres@localhost/postgres"

# Debug mode.
# Do not enable unless you know what you are doing.
DEBUG = False

# Public mode.
# PUBLIC = True is not recommended on Flask dev server.
PUBLIC = True

# Port to run on.
PORT = 5000

# List of available languages. Key has the language code and value the
# native name of that language.
LANGUAGES = {"en": "English", "fi": "Suomi"}
if DEBUG:
    LANGUAGES["qqx"] = "language.string.codes"

# Report reasons; these are considered translation strings
# For example, user report reason "test" is under "reportuser.reason.test"
# while message report reason "test" is under "reportmsg.reason.test"
USER_REPORT_REASONS = ["inappropriate", "impersonation", "spam"]
MSG_REPORT_REASONS = ["inappropriate", "spam", "privacyviolation", "copyright"]

# Maximum age ot notifications, read or unread, in hours.
NOTIFICATIONS_MAX_AGE = 24 * 7
