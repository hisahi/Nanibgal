
# Käyttäjäryhmät
Teknisesti käyttäjäryhmiä on määritelmän mukaan kaksi tai kolme: normaalit
käyttäjät, valvojat sekä mahdollisesti porttikiellon saaneet käyttäjät.

Mahdollisia käyttäjiä on kuitenkin laajalti, sillä mikroblogipalveluna
käyttäjiä voi tulla monelta eri saralta.

# User storyt
* Käyttäjänä voin kirjautua ja luoda itselleni tilin, sekä poistaa sen.
* Käyttäjänä voin muokata tilini asetuksia.
* Käyttäjänä voin lähettää, muokata sekä poistaa viestejäni.
* Käyttäjänä voin hakea viestejä tekstihaulla.
* Käyttäjänä voin tykätä viestejä.
* Käyttäjänä voin seurata toisia käyttäjiä.
* Valvojana voin lukea ilmiantoja.
* Valvojana voin antaa porttikiellon käyttäjälle.

# Toiminnot

## Kirjautuminen
Sivulle voi kirjautua käyttäjänimellä ja salasanalla, sekä tunnuksen
voi luoda jos sellaista ei ole. Kirjautuminen vaaditaan viestien
kirjoittamiseen, niihin tykkäämiseen, syötteeseen, käyttäjien seuraamiseen, 
viestien sekä käyttäjien ilmiantamiseen ja asetuksiin. Sivulta voi
kirjautua ulos.

Salasanat säilötään tietokannassa käyttäen bcrypt:iä, joten vaikka tieto-
kantaan pääsisikin haitallinen tekijä, tämä ei saisi käyttäjien salasanoja
tietoonsa sellaisenaan.

Salasanan tiivisteen hakeminen:
`SELECT passhash FROM users WHERE username = 'testiuser';`

## Tilin luominen
Yllä mainitun osion mukaisesti käyttäjätilin voi itselleen luoda. Luomiseen
vaaditaan käyttäjänimi sekä salasana. Sähköposti säilötään tietokantaan,
mutta sitä ei muuten käytetä, eikä sitä myöskään vaadita käyttö-
liittymässä.

Tilin luominen (salasanatiiviste tulee laskea itse):
`INSERT INTO users (username, displayname, email, passhash, registered) VALUES ('testiuser', 'testiuser', '', '\x2432622431322442792e744f3842516453653647776c696b53786472654f625837417059755653653078665144546a64386536746d2e4b3156783071', CURRENT_TIMESTAMP);`

## Tilin muokkaaminen
Tilin käyttäjänimeä, näyttönimeä, salasanaa, käyttäjäkuvausta sekä asetuksia
voi muokata.

Tilin näyttönimen muuttaminen:
`UPDATE users SET displayname = 'Testi Nimi' WHERE username = 'testiuser';`

## Tilin poistaminen
Käyttäjätilin voi poistaa, jolloin myös kaikki tiliin liittyvä tieto,
kuten viestit, poistetaan.

Käyttäjätilin poistaminen:
`DELETE FROM users WHERE username = 'testiuser';`

## Viestin hakeminen
Viestejä voi lukea sekä hakea niistä tiedot, kuten lähettäneen käyttäjän,
lähetysajan, mahdollisen muokkausajan, sen onko viesti vastaus ja mihin
viestiin jos on sekä sisällön ja linkin.

Viestin hakeminen, hakee lähettäneen käyttäjän ID:n, viestin sisällön
sekä linkin:
`SELECT author, contents, link FROM msgs WHERE msgid = 5;`

## Viestin lisääminen
Viestejä voi lisätä, ja niihin voi lisätä sekä sisältöä että mahdollisesti
linkin.

Viestin lisääminen:
`INSERT INTO msgs (author, contents, link, postdate) VALUES (3, 'viesti', 'https://example.com/', CURRENT_TIMESTAMP);`

## Viestin muokkaaminen
Viestiä voi muokata. Tämän voi tehdä käyttöliittymän kautta vain 10
minuuttia viestin lähettämishetkestä.

Viestien muokkaaminen, muuttaa sisältöä (käyttäjän ID = 5):
`UPDATE msgs SET contents = 'uusi viest', editdate = CURRENT_TIMESTAMP WHERE msgid = 5;`

## Viestin poistaminen
Viestejä voi poistaa, jolloin niiden tykkäykset häviävät. Vastaukset
poistettuun viestiin pysyvät vastauksina, mutta niitä katsoessa poistettua
viestiä ei voi katsoa.

Viestin poistaminen:
`DELETE FROM msgs WHERE msgid = 5;`

## Viestien tekstihaku
Viestejä voi hakea sisällön sekä linkkien perusteella.

Viestin hakeminen sisällön perusteella:
`SELECT * FROM msgs WHERE ' ' + contents + ' ' LIKE '% sana %';` 

## Viestin tykkääminen
Käyttäjät voivat tykätä viestejä ja poistaa tykkäyksen. Viestejä voi
tykätä vain kerran.

Viestin tykkääminen (käyttäjän ID = 3, viestin ID = 10):
`INSERT INTO likes ("user", msg) VALUES (3, 10);`

## Käyttäjien seuraaminen
Käyttäjiä voi seurata ja seuraamisen voi poistaa.

Käyttäjän seuraaminen (seuraajan ID = 3, seurattavan ID = 5):
`INSERT INTO follows (follower, followed) VALUES (3, 5);`

## Ilmiantojen lukeminen
Valvojat voivat lukea ilmiantoja sekä viesteistä että käyttäjistä.

Kaikkien viesti-ilmiantojen lukeminen:
`SELECT * FROM msgreports;`

## Porttikiellon antaminen käyttäjälle
Valvojat voivat antaa porttikiellon käyttäjälle.

Porttikiellon antaminen (käyttäjälle, jonka ID on 5):
`UPDATE users SET banned = True WHERE userid = 5;`
