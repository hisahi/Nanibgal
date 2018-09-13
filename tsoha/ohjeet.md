
# Nanibgal
Nanibgal on mikroblogipalvelu.

# Asentaminen
Valmiina olevan Nanibgal-instanssin käyttö vaatii vain nykyaikaisen selaimen.

Palvelinohjelmiston asennukseen ja käyttöön vaaditaan Python 3.5. pip:n
kautta tulee asentaa requirements.txt-tiedostossa luetellut moduulit.
Tarvitset myös PostgreSQL-tietokannan.

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

Uusien seurattavien käyttäjien löytämiseen on kaksi päätapaa: voit etsiä
käyttäjänimiä toisista palveluista tai kavereilta, tai käyttää haku-
toimintoa löytääksesi käyttäjiä sekä viestejä.

## Profiili
Käyttäjäprofiilin voi löytää yläpalkin (tai valikon) linkistä ~-
alkuisella linkillä, jonka perässä on käyttäjänimesi. Voit avata toisen
henkilön profiiliin haun kautta tai siirtymällä syötteeseesi ja lisäämällä
verkko-osoitteen loppuun /~ sarjan ja sen perään käyttäjänimen.

Profiilia voi mukauttaa asetuksista.

## Viestit
Palvelun päätoimintoja on viestien kirjoittaminen. Niissä voi olla
256 merkkiä tekstiä linkin lisäksi, joka sekin on rajoitettu 256 merkkiin.

Viestejä voi muokata 10 minuutin sisällä niiden lähettämishetkestä ja
poistaa milloin vain.

Viesteihin voi myös vastata. Siinä tapauksessa kun viestin avaa, se
näyttää viestin, mihin se on itse vastaus, sekä myöskin siihen vastauksena
olevat viestit.

## Ilmiantaminen
Sekä käyttäjiä että viestejä voi ilmiantaa. Ilmiannon tapauksissa
valvojat voivat käydä ilmiannot läpi ja joko poistaa viestit taikka
antaa porttikieltoja ne lähettäneille käyttäjille.

## Asetukset
Käyttäjäasetukset antavat sinun muokata profiiliasi, muuttaa salasanaasi
sekä mukauttaa muita asetuksia.

Muokkausten tekemiseksi sinun tulee ensin syöttää nykyisen salasanasi
ylälaidassa olevaan kenttään. Salasanan voi vaihtaa kirjoittamalla uuden
salasanan niille suunniteltuun kenttään; jos kentät jätetään tyhjiksi,
salasana jää ennalleen.

Asetuksissa on myös lomake käyttäjätilin poistoon. Tämä täytetään
kirjoittamalla käyttäjänimi ja salasana asetussivun alalaidassa
olevaan lomakkeeseen. Huomioithan, että kun käyttäjä poistetaan
järjestelmästä, kaikki siihen liittyvä tieto, kuten viestit, poistetaan
myös. Tätä toimintoa ei voi perua, joten harkitse asiaa ennen tilin poistoa.

## Paikallistaminen
Nanibgal tukee täyttä käyttöliittymän paikallistamista.
