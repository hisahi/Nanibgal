
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, validators

class LoginForm(FlaskForm):
    username = StringField("User name", [validators.Length(min=4, max=20)])
    password = PasswordField("Password", [validators.Length(max=256)])
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
    verify = PasswordField("Verify password", [validators.EqualTo(password, message="register.error.password_not_match")])
    remember = BooleanField("Remember me")

    def localized(self, lang):
        self.username.label = lang.tr("register.username")
        self.password.label = lang.tr("register.password")
        self.verify.label = lang.tr("register.verify_password")
        self.remember.label = lang.tr("register.remember")
        return self

class SettingsForm(FlaskForm):
    oldpassword = PasswordField("Password", [validators.Length(max=256, message="settings.invalid_old_password")])
    displayname = StringField("Display name", [validators.Length(max=64, message="settings.error.invalid_display_name_length")])
    #email = StringField("email", [validators.Email(message="register.error.invalid_email")])
    password = PasswordField("New password", [validators.Length(min=8, max=256, message="settings.error.invalid_password_length")])
    verify = PasswordField("Verify password", [validators.EqualTo(password, message="settings.error.password_not_match")])
    privatemessages = BooleanField("Make my messages private")
    privatefollows = BooleanField("Make my followers and follows private")
    deleteaccount = StringField("Enter your username exactly to DELETE your account")

    def localized(self, lang):
        self.oldpassword.label = lang.tr("settings.old_password")
        self.displayname.label = lang.tr("settings.display_name")
        self.password.label = lang.tr("settings.new_password")
        self.verify.label = lang.tr("settings.verify_password")
        self.privatemessages.label = lang.tr("settings.private_messages")
        self.privatefollows.label = lang.tr("settings.private_follows")
        self.deleteaccount.label = lang.tr("settings.delete_account")
        return self

class NewPostForm(FlaskForm):
    def localized(self, lang):
        return self
