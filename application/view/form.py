
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, TextAreaField, PasswordField, BooleanField, validators

from application.misc import generate_language_list, generate_user_report_reason_list, generate_msg_report_reason_list

class LoginForm(FlaskForm):
    username = StringField("User name", [validators.Length(min=4, max=20, message="register.error.invalid_username_length")])
    password = PasswordField("Password", [validators.Length(max=256, message="register.error.invalid_password_length")])
    remember = BooleanField("Remember me")

    def localized(self, lang):
        self.username.label = lang.tr("login.username")
        self.password.label = lang.tr("login.password")
        self.remember.label = lang.tr("login.remember")
        return self

class RegisterForm(FlaskForm):
    username = StringField("User name", [validators.Length(min=4, max=20, message="register.error.invalid_username_length")])
    #email = StringField("email", [validators.Email(message="register.error.invalid_email")])
    password = PasswordField("Password", [validators.Length(min=8, max=256, message="register.error.invalid_password_length")])
    verify = PasswordField("Verify password", [validators.EqualTo("password", message="register.error.password_not_match")])
    remember = BooleanField("Remember me")

    def localized(self, lang):
        self.username.label = lang.tr("register.username")
        self.password.label = lang.tr("register.password")
        self.verify.label = lang.tr("register.verify_password")
        self.remember.label = lang.tr("register.remember")
        return self

class SettingsForm(FlaskForm):
    oldpassword = PasswordField("Password", [validators.Length(max=256, message="settings.error.invalid_old_password")])
    username = StringField("User name", [validators.Length(min=4, max=20, message="register.error.invalid_username_length")])
    displayname = StringField("Display name", [validators.Length(max=64, message="settings.error.invalid_display_name_length")])
    bio = TextAreaField("Bio", [validators.Optional(), validators.Length(max=256, message="settings.error.invalid_bio_length")])
    #email = StringField("email", [validators.Email(message="register.error.invalid_email")])
    password = PasswordField("New password", [validators.Optional(), validators.Length(min=8, max=256, message="settings.error.invalid_password_length")])
    verify = PasswordField("Verify password", [validators.EqualTo("password", message="settings.error.password_not_match")])
    language = SelectField("Languages", choices = generate_language_list(None))
    privatemessages = BooleanField("Make my messages private")
    privatefollows = BooleanField("Make my followers and follows private")
    privatelikes = BooleanField("Make messages I have liked private")

    def localized(self, lang):
        self.oldpassword.label = lang.tr("settings.old_password")
        self.username.label = lang.tr("settings.username")
        self.displayname.label = lang.tr("settings.display_name")
        self.bio.label = lang.tr("settings.bio")
        self.password.label = lang.tr("settings.new_password")
        self.verify.label = lang.tr("settings.verify_password")
        self.language.label = lang.tr("settings.language")
        self.language.choices = generate_language_list(lang)
        self.privatemessages.label = lang.tr("settings.private_messages")
        self.privatefollows.label = lang.tr("settings.private_follows")
        self.privatelikes.label = lang.tr("settings.private_likes")
        return self

class DeleteAccountForm(FlaskForm):
    deleteaccount = StringField("Enter your username exactly to DELETE your account")
    oldpassword = PasswordField("Password", [validators.Length(max=256, message="settings.error.invalid_old_password")])

    def localized(self, lang):
        self.deleteaccount.label = lang.tr("settings.delete_account_user")
        self.oldpassword.label = lang.tr("settings.delete_account_password")
        return self

class NewPostForm(FlaskForm):
    reply = IntegerField("Reply", [validators.Optional()])
    contents = TextAreaField("Contents", [validators.Length(min=1, max=256, message="new.error.invalid_length")])
    link = StringField("Link", [validators.Optional(), validators.Length(min=1, max=256, message="new.error.invalid_link_length"), validators.URL(require_tld=True, message="new.error.invalid_link")])

    def localized(self, lang):
        self.link.label = lang.tr("newpost.link")
        return self

class EditPostForm(FlaskForm):
    msg = IntegerField("msg")
    contents = TextAreaField("Contents", [validators.Length(min=1, max=256, message="new.error.invalid_length")])
    link = StringField("Link", [validators.Optional(), validators.Length(min=1, max=256, message="new.error.invalid_link_length"), validators.URL(require_tld=True, message="new.error.invalid_link")])

    def localized(self, lang):
        self.link.label = lang.tr("editpost.link")
        return self

class ReportUserForm(FlaskForm):
    user = IntegerField("user")
    reason = SelectField("reason", choices = generate_user_report_reason_list(None))

    def localized(self, lang):
        self.reason.label = lang.tr("reportuser.reason")
        self.reason.choices = generate_user_report_reason_list(lang)
        return self

class ReportPostForm(FlaskForm):
    msg = IntegerField("msg")
    reason = SelectField("reason", choices = generate_msg_report_reason_list(None))

    def localized(self, lang):
        self.reason.label = lang.tr("reportmsg.reason")
        self.reason.choices = generate_msg_report_reason_list(lang)
        return self

class SearchMessageForm(FlaskForm):
    q = StringField("q")

    def localized(self, lang):
        return self

class SearchUserForm(FlaskForm):
    q = StringField("q")

    def localized(self, lang):
        return self
