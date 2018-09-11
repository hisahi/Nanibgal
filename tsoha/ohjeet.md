
# Nanibgal
Nanibgal on mikroblogipalvelu.

# Asentaminen
Valmiina olevan Nanibgal-instanssin käyttö vaatii vain nykyaikaisen selaimen.

Palvelinohjelmiston asennukseen ja käyttöön vaaditaan Python 3.5. pip:n
kautta tulee asentaa requirements.txt-tiedostossa luetellut moduulit.

Palvelinohjelmisto tulisi ensin määritellä muokkaamalla applications-
kansion config.py-tiedostoa.

Palvelin käynnistetään suorittamalla main.py.

# Käyttö

## Tilin luominen
Kun Nanibgalin avaa ensimmäisen kerran, näkee todennäköisesti 
kirjautumisruudun.

Voit kirjautua olemassaolevalle käyttäjätilille tai luoda uuden.
Luodaksesi tilin sinun tulee valita käyttäjänimi ja salasana, jonka
jälkeen tilin voi luoda.

## Syöte
Syöte on oletusnäkymä kirjautuneille käyttäjille. Siinä näkyy viestiesi
lisäksi seuraamiesi käyttäjien lähettämät viestit.

There are two primary ways to find users to follow: you can either find
user names from other services or from friends or use the search feature
to find users and messages.

## Profiili
Your user profile can be opened with a link in the top bar (or menu)
titled ~username, where username is your user name. To open someone
else's profile, you can either use the search, or navigate to the
feed and add /~username to the end of the address.

You can edit aspects of your profile in the settings.

## Viestit
The main feature is creating posts. Posts may contain 256 characters
of text in addition to a link, which is too restricted to 256 characters.

Messages can be edited within 10 minutes of their posting and deleted
at any time.

It is also possible to reply to messages. In that case, the message,
when opened, will show the message it is a reply to, as well as showing
the replies to that given message.

## Ilmiantaminen
Both users and messages can be reported. In such cases, administrators
can review the reports and appropriately remove the messages as well as
ban the users who sent them.

## Asetukset
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

## Paikallistaminen
Nanibgal supports full localization of the user interface.
