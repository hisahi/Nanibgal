
# Nanibgal
Nanibgal is a microblogging service. 

# Installing
Using Nanibgal when it is already hosted only requires a modern web browser.

To install the server software, one needs at least Python 3.5 and to install
the requirements as described in requirements.txt with pip.

To run the server, simply run main.py.

# Usage

## Account creation
When you first open Nanibgal, you will likely see a login screen.

You can log in with an existing account, or register a new one
In order to register, you have to choose an user name and a password, after
which the account will be created.

## Feed
The default view for logged-in users is the feed. It shows your messages
as well as the messages of people you are following.

There are two primary ways to find users to follow: you can either find
user names from other services or from friends or use the search feature
to find users and messages.

## Profile
Your user profile can be opened with a link in the top bar (or menu)
titled ~username, where username is your user name. To open someone
else's profile, you can either use the search, or navigate to the
feed and add /~username to the end of the address.

You can edit aspects of your profile in the settings.

## Messages
The main feature is creating posts. Posts may contain 256 characters
of text in addition to a link, which is too restricted to 256 characters.

Messages can be edited within 10 minutes of their posting and deleted
at any time.

It is also possible to reply to messages. In that case, the message,
when opened, will show the message it is a reply to, as well as showing
the replies to that given message.

## Reporting
Both users and messages can be reported. In such cases, administrators
can review the reports and appropriately remove the messages as well as
ban the users who sent them.

## Settings
User settings allow you to modify your profile, password and
other settings.

In order to perform any changes, you must type your current password
to the top field. The password can be changed by entering the new
password into the password fields; if the fields are left empty, the
password is not changed.

The settings also allow you to delete your account. This is done by
entering your user name and password into the field at the bottom of
the settings page. Note that when an user is deleted from the system,
all data associated with it is also deleted, such as the messages.
The operation cannot be undone, so think twice about deleting your account.

## Localization
Nanibgal supports full localization of the user interface.
