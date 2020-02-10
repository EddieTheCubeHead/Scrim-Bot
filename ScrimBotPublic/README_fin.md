###############################################################################

                               scrimbotti 1.0.0
							      07.11.2019

###############################################################################

                           tämänhetkiset toiminnot

###############################################################################

discord-botti scrim-pelien, eli tuttujen kesken pelattavien pelien, missä
pelaajat jaetaan kahteen joukkueeseen ja joukkueet pelaavat toisiaan vastaan,
järjestämiseen discord-serverin käyttäjien kesken. botti luo '/setup (peli)'
-komennolla kutsuttaessa embed-viestin, joka toimii botin käyttöliittymänä.
botti tunnistaa kutsutun pelin sisäisestä kirjastosta ja tarkistaa milloin 
scrimiin on liittynyt tarpeeksi pelaajia. scrim-sessio tukee pelaajana
liittymisen lisäksi katsojana liittymistä, joskin tästä ei ole toistaiseksi
mitään hyötyä, vaan toiminto on lähinnä future-proof metodi.

kun vaadittu pelaajamäärä on saavutettu, pelaajat voidaan lukita '/lock'
-komennolla. tällöin scrimin pelaajia, tai katsojia ei voi enää muokata. tässä
vaiheessa pelaajat jakautuvat tiimeihin. botti tukee tällä hetkellä manuaalista
joukkueiden tekoa (eli jokainen pelaaja valitsee tiiminsä itse), joukkueiden
arpomista ja tasaisten joukkueiden tekoa sisäisen elo-järjestelmän avulla.

lukitussa tilassa joukkueita voidaan manipuloida joko reaktio-ui:n avulla, tai
komennoilla. komento '/teams random' jakaa joukkueet satunnaisesti ja
komento '/teams clear' siirtää kaikki joukkueen valinneet pelaajat
takaisin joukkueettomiin pelaajiin. '/teams balanced' jakaa sisäisen
elo-järjestelmän mukaan mahdollisimman tasaiset joukkueet ja
'/teams balancedrandom (kipukynnys) jakaa joukkueet, joilla oletettu
voittoprosentti poikkeaa viidestäkymmenestä korkeintaan kipukynnyksen verran.

tiimien valinnan voi järjestää myös '/teams pickup' -komennolla
huutojakoja varten. argumenttejä ovat huutajien valinnan muoto:
random, choose ja elon mukaan. random ja elo
ovat botin puolesta automaattisia, mutta choose toteutetaan
reaktioilla käyttöliittymän johdonmukaisuuden ylläpitämiseksi. lisäksi huuto-
järjestys (perinteinen abababab vai tasoitettu abbaabba)on
valittavissa argumenteilla.

kun tiimit ovat valmiit komennolla '/start' botti tarkistaa onko serverillä
kanavat nimeltä "team 1" ja "team 2". jos kanavat ovat olemassa botti siirtää
pelaajat kanaville "team 1" ja "team 2", tarkistettuaan ensin, että pelaajat
ovat jollain kanavalla ja odotettuaan loppujen liittymisen jollekulle kanavalle.
lisäksi, siirtyi pelaajia tai ei, /start lukitsee tiimit ja päivittää
embedin.

pelattuaan scrimin pelaajat sulkevat nykyisen instanssin scrimistä komennolla
'/winner(voittaja)'. tämä päättää scrimin, resetoi sisäisen current-
luokan ja päivittää osallistujien elo-tilastot

Botin sisäisen pelilistan voi päivittää komennolla '/update'. Komento on käytössä
vain admineille. Koska komento poistaa väliaikaisesti kaikki Game-luokan instanssit,
komentoa voi käyttää vain, kun yhtään scrimiä ei ole kesken. Komento lataa
uudestaan myös kaikki cogs-moduulit, lähinnä kehittämisen helppoutta ajatellen

###############################################################################

                      elo-järjestelmä ja elo-komennot

###############################################################################

botin matchmaking-järjestelmä pohjaa vahvasti mm. shakissa käytettävään elo-
järjestelmään. tarvittavat luokat ja funktiot ovat erillisessä elo_module-
moduulissa.

'/elo (pelaaja) (peli) (arvo)' asettaa annetulle pelaajalle elon annettuun
peliin annetuksi arvoksi ja '/leaderboard (peli) (tilasto)' näyttää annetun
pelin pelaajien tilastot järjestettynä annetun tilaston mukaan.


###############################################################################

                                 kehitysideat

###############################################################################

  -pelit luokkaan muutoksia, joilla tunnistetaan, onko pelissä karttoja ja
      määritellään miten toimitaan kartan valinnan suhteen. voisi ulottaa
      myös puolten valintaan ja pick orderiin, jos pelistä niitä löytyy.
  -suolakerroin (huumoriarvo): Äänestys joukkueen suolaisimmasta pelin jälkeen
  -fill -argumentti '/teams' -komentoon
  -Mahdollisuus "tilata" tietyn serverin tietyn pelin scrimit
  -Mahdollisuus alustaa botin tarvitsevat kanavat admin-komennolla

###############################################################################

                                versiohistoria

###############################################################################

  1.0.0 -- 02.02.2020
    -Koulutöiden vuoksi projekti sivuroolissia pitkän aikaa, suuria muutoksia ei
	ole tehty, mutta käytön myötä ilmenneitä bugeja korjattu tarpeeksi, jotta
	botti tuntuu vakaalta ja valmiilta.
		-Tiimien muokkaus uudelleenkirjoitettava 1.1.0: tällö hetkellä botti voi
		mennä jumiin, jos suorituksessa tulee ongelma kesken tiimien muokkauksen, jättäen
		puolivalmiita listoja muuttujiin ja pakottaen uudelleenkäynnistyksen
		muuttujien tyhjentämiseksi.
	-Pieniä käytettävyysparannuksia ja pohjakoodi asetukset systeemille (1.2.0?)
		-Aktiivinen scrim estää viestin lähettämisen kanavalle
		-/note tämä kiertämiseksi
		-Lukitsemattomat scrimit terminoidaan viidentoista minuutin jälkeen. Ajastin
		uudelleenkäynnistetään kaikissa interaktioissa

  beta 0.9.8 -- 5.11.2019
	-Koko koodin siistintä kommentteilla, docstringeillä, selkeämmillä muuttujilla
	ja uusilla funktioilla
	-Joka scrimillä on nyt mestarikäyttäjä, eli scrimin luoja. Vain mestarikäyttäjä
	voi antaa scrimille komentoja.

  beta 0.9.7b -- 31.10.2019

	-Cogs -implementaatio jätti osan Scrim-luokkaan sidotuista toiminnoista
	kodittomaksi. Siirsin nämä omaan scrim_methods moduuliinsa ja uudelleennimesin
	elo_module -moduulin elo_methods -moduuliksi yhtenäisen nimeämiskäytännön
	ylläpitämiseksi.
		-Samalla korjaantui '/update' -komennossa ollut bugi, joka pyyhki
		Scrim-instanssit

  beta 0.9.7 -- 31.10.2019
	
	-Cogs -järjestelmän integrointi
		-elo -komentojen siirto omaan moduuliin
		-scrim -komentojen siirto omaan moduuliin
		-help -komentojen siirto omaan moduuliin
		-update -komennon päivitys lataamaan moduulit uudestaan
			-bottia ei tarvitse enää käynnistää uudestaan komentoja päivitettäessä
	-pieniä bugikorjauksia
		-'/leaderboard (game) games' ei järjestynyt oikein
		-osaan väliaikaisista viesteistä ei oltu implementoitu temporary_feedback
		funktiota


  beta 0.9.6 -- 30.10.2019

	-Config-tiedoston lisääminen.
	-Pelien listan siirtäminen päämoduulista configiin
		-tähän liittyen get_games -funktion implementointi
		-'/update' -komennon implementointi
			-päivittää pelit config-tiedostosta
	-Huutojoukkueiden muuttaminen display_name -pohjaisesta @käyttäjä -pohjaiseksi
	-Huutojoukkueiden bugikorjauksia



  beta 0.9.5 -- 29.10.2019

	-komentojen suoraviivaistus ja '/help' - komennon uudistus vastaamaan uusia
	komentoja.
	-Tuki usealle eri scrimille omilla äänikanavillaan samalla serverillä
	-'/leaderboard' -komennon siistintä
		-vääräntyyppisistä muuttujatyypeistä johtuvat järjestysvirheet kuriin
		-turhat sanakirjat järjestelyn helpottamiseen korjattu tehokkaammalla
		järjestelyllä
	-Yleitä koodin siistintää
		-kanavan tunnistamisen ja asiaankuuluvan scrim-olion haku funktioon
		-väliaikaiset viestit funktioon
		-Testaukseen käytettyjä print-rivejä poistettu reilulla kädellä
	-Muita pieniä bugikorjauksia testikäytössä ilmenneille ongelmille



  beta 0.9.4 -- 24.10.2019

	-tuki usealle samanaikaiselle scrimille.
		-toimii niin, että jokaisella "scrim" -alkuisella kanavalla voi olla
		oma pelinsä



  beta 0.9.3 -- 23.10.2019

	-laadukkaampi tallenusmetodi ja backup-järjestelmä



  beta 0.9.2 -- 17.10.2019

	-yleisiä bugikorjauksia rewriten jälkeen



  beta 0.9.1 -- 16.10.2019

	-dokumentaation päivitys muun ohjelmiston kanssa samaan vaiheeseen



  beta 0.9.0 -- 16.10.2019

	-pienimuotoinen rewrite globaalien muuttujien poistamiseksi
	implementoimalla luokka "scrim" ja pitämällä muuttujat luokan
	instanssin "current" sisällä. lisäksi globaali lista peleistä
	implementoitiin elo-moduulin game-luokan sisään.
	-huomioitavaa: testaajien puuttumisesta johtuen suurinta osaa komennoista
	ei ole testattu rewriten jälkeen.



  beta 0.8.2 -- 15.10.2019

	-'/help' -uudelleenkirjoitus
	-'leaderboard' bugikorjauksia
	-'/scrim teams pickup balanced' -implementointi elon avulla
	-'/pick random' -implementointi
	-huomioitavaa: testaajien puuttumisesta johtuen pickup- ja pick -komennot
	ovat testaamattomia. todennäköisesti tarvitsevat jonkin verran säätöä.



  beta 0.8.1 -- 14.10.2019

	-/leaderboard (peli) (statistiikka)



  beta 0.8.0 -- 11.10.2019

	-elo -toimintojen implementointi
		-/scrim teams balanced
		-/scrim teams balancedrandom
		-/elo (pelaaja) (peli) (arvo)



  v 0.7.0 -- 10.10.2019

	-elo-moduulin implementointi. huomioitava, että toiminnallisuus säilyi
	identtisenä.



  v 0.6.0 -- 9.10.2019

	-/scrim teams pickup -komennon implementointi
	-reaktio-ui:n implementointi 'choose' argumentille
	-/pick (käyttäjä) -komennon implementointi



  v 0.5.0 -- 9.10.2019

	-/scrim start komennon implementointi



  v 0.4.2 -- 8.10.2019

	-dokumentaation luominen
	-olemassaolevan koodin siistiminen



  v 0.4.1 -- 8.10.2019

	-turhien listojen poistaminen
		-osallistujien id ja displayname voidaan listan sijaan kutsua objektista



  v 0.4.0 -- 8.10.2019

	-/scrim teams random- ja /scrim teams clear -komentojen implementointi
	-/scrim teams -komentoluokan implementointi



  v 0.3.1 -- 7.10.2019

	-/scrim lock -komennon reaktio-ui:n implementointi



  v 0.3.0 -- 7.10.2019

	-/scrim lock -komennon implementointi



  v 0.2.0 -- 7.10.2019

	-/scrim setup -komennon reaktio-ui



  v 0.1.0 -- 7.10.2019

	-/scrim setup -komennon implementointi



###############################################################################

							lähteitä:

###############################################################################

https://discordpy.readthedocs.io/en/latest/api.html
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
lukemattomia yhden sivun oppaita ja stack overflow ongelmia kaikista kuviteltavissa
olevista Python -ominaisuuksista
