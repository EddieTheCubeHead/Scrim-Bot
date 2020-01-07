###############################################################################

                             scrimbotti beta0.9.8
							      07.11.2019

###############################################################################

                           t‰m‰nhetkiset toiminnot

###############################################################################

discord-botti scrim-pelien, eli tuttujen kesken pelattavien pelien, miss‰
pelaajat jaetaan kahteen joukkueeseen ja joukkueet pelaavat toisiaan vastaan,
j‰rjest‰miseen discord-serverin k‰ytt‰jien kesken. botti luo '/setup (peli)'
-komennolla kutsuttaessa embed-viestin, joka toimii botin k‰yttˆliittym‰n‰.
botti tunnistaa kutsutun pelin sis‰isest‰ kirjastosta ja tarkistaa milloin 
scrimiin on liittynyt tarpeeksi pelaajia. scrim-sessio tukee pelaajana
liittymisen lis‰ksi katsojana liittymist‰, joskin t‰st‰ ei ole toistaiseksi
mit‰‰n hyˆty‰, vaan toiminto on l‰hinn‰ future-proof metodi.

kun vaadittu pelaajam‰‰r‰ on saavutettu, pelaajat voidaan lukita '/lock'
-komennolla. t‰llˆin scrimin pelaajia, tai katsojia ei voi en‰‰ muokata. t‰ss‰
vaiheessa pelaajat jakautuvat tiimeihin. botti tukee t‰ll‰ hetkell‰ manuaalista
joukkueiden tekoa (eli jokainen pelaaja valitsee tiimins‰ itse), joukkueiden
arpomista ja tasaisten joukkueiden tekoa sis‰isen elo-j‰rjestelm‰n avulla.

lukitussa tilassa joukkueita voidaan manipuloida joko reaktio-ui:n avulla, tai
komennoilla. komento '/teams random' jakaa joukkueet satunnaisesti ja
komento '/teams clear' siirt‰‰ kaikki joukkueen valinneet pelaajat
takaisin joukkueettomiin pelaajiin. '/teams balanced' jakaa sis‰isen
elo-j‰rjestelm‰n mukaan mahdollisimman tasaiset joukkueet ja
'/teams balancedrandom (kipukynnys) jakaa joukkueet, joilla oletettu
voittoprosentti poikkeaa viidest‰kymmenest‰ korkeintaan kipukynnyksen verran.

tiimien valinnan voi j‰rjest‰‰ myˆs '/teams pickup' -komennolla
huutojakoja varten. argumenttej‰ ovat huutajien valinnan muoto:
random, choose ja elon mukaan. random ja elo
ovat botin puolesta automaattisia, mutta choose toteutetaan
reaktioilla k‰yttˆliittym‰n johdonmukaisuuden yll‰pit‰miseksi. lis‰ksi huuto-
j‰rjestys (perinteinen abababab vai tasoitettu abbaabba)on
valittavissa argumenteilla.

kun tiimit ovat valmiit komennolla '/start' botti tarkistaa onko serverill‰
kanavat nimelt‰ "team 1" ja "team 2". jos kanavat ovat olemassa botti siirt‰‰
pelaajat kanaville "team 1" ja "team 2", tarkistettuaan ensin, ett‰ pelaajat
ovat jollain kanavalla ja odotettuaan loppujen liittymisen jollekulle kanavalle.
lis‰ksi, siirtyi pelaajia tai ei, /start lukitsee tiimit ja p‰ivitt‰‰
embedin.

pelattuaan scrimin pelaajat sulkevat nykyisen instanssin scrimist‰ komennolla
'/winner(voittaja)'. t‰m‰ p‰‰tt‰‰ scrimin, resetoi sis‰isen current-
luokan ja p‰ivitt‰‰ osallistujien elo-tilastot

Botin sis‰isen pelilistan voi p‰ivitt‰‰ komennolla '/update'. Komento on k‰ytˆss‰
vain admineille. Koska komento poistaa v‰liaikaisesti kaikki Game-luokan instanssit,
komentoa voi k‰ytt‰‰ vain, kun yht‰‰n scrimi‰ ei ole kesken. Komento lataa
uudestaan myˆs kaikki cogs-moduulit, l‰hinn‰ kehitt‰misen helppoutta ajatellen

###############################################################################

                      elo-j‰rjestelm‰ ja elo-komennot

###############################################################################

botin matchmaking-j‰rjestelm‰ pohjaa vahvasti mm. shakissa k‰ytett‰v‰‰n elo-
j‰rjestelm‰‰n. tarvittavat luokat ja funktiot ovat erillisess‰ elo_module-
moduulissa.

'/elo (pelaaja) (peli) (arvo)' asettaa annetulle pelaajalle elon annettuun
peliin annetuksi arvoksi ja '/leaderboard (peli) (tilasto)' n‰ytt‰‰ annetun
pelin pelaajien tilastot j‰rjestettyn‰ annetun tilaston mukaan.


###############################################################################

                                 kehitysideat

###############################################################################

  -pelit luokkaan muutoksia, joilla tunnistetaan, onko peliss‰ karttoja ja
      m‰‰ritell‰‰n miten toimitaan kartan valinnan suhteen. voisi ulottaa
      myˆs puolten valintaan ja pick orderiin, jos pelist‰ niit‰ lˆytyy.
  -suolakerroin (huumoriarvo): ƒ‰nestys joukkueen suolaisimmasta pelin j‰lkeen
  -fill -argumentti '/teams' -komentoon
  -Mahdollisuus "tilata" tietyn serverin tietyn pelin scrimit
  -Mahdollisuus alustaa botin tarvitsevat kanavat admin-komennolla

###############################################################################

                                versiohistoria

###############################################################################

  beta 0.9.8 -- 5.11.2019
	-Koko koodin siistint‰ kommentteilla, docstringeill‰, selke‰mmill‰ muuttujilla
	ja uusilla funktioilla
	-Joka scrimill‰ on nyt mestarik‰ytt‰j‰, eli scrimin luoja. Vain mestarik‰ytt‰j‰
	voi antaa scrimille komentoja.

  beta 0.9.7b -- 31.10.2019

	-Cogs -implementaatio j‰tti osan Scrim-luokkaan sidotuista toiminnoista
	kodittomaksi. Siirsin n‰m‰ omaan scrim_methods moduuliinsa ja uudelleennimesin
	elo_module -moduulin elo_methods -moduuliksi yhten‰isen nime‰misk‰yt‰nnˆn
	yll‰pit‰miseksi.
		-Samalla korjaantui '/update' -komennossa ollut bugi, joka pyyhki
		Scrim-instanssit

  beta 0.9.7 -- 31.10.2019
	
	-Cogs -j‰rjestelm‰n integrointi
		-elo -komentojen siirto omaan moduuliin
		-scrim -komentojen siirto omaan moduuliin
		-help -komentojen siirto omaan moduuliin
		-update -komennon p‰ivitys lataamaan moduulit uudestaan
			-bottia ei tarvitse en‰‰ k‰ynnist‰‰ uudestaan komentoja p‰ivitett‰ess‰
	-pieni‰ bugikorjauksia
		-'/leaderboard (game) games' ei j‰rjestynyt oikein
		-osaan v‰liaikaisista viesteist‰ ei oltu implementoitu temporary_feedback
		funktiota


  beta 0.9.6 -- 30.10.2019

	-Config-tiedoston lis‰‰minen.
	-Pelien listan siirt‰minen p‰‰moduulista configiin
		-t‰h‰n liittyen get_games -funktion implementointi
		-'/update' -komennon implementointi
			-p‰ivitt‰‰ pelit config-tiedostosta
	-Huutojoukkueiden muuttaminen display_name -pohjaisesta @k‰ytt‰j‰ -pohjaiseksi
	-Huutojoukkueiden bugikorjauksia



  beta 0.9.5 -- 29.10.2019

	-komentojen suoraviivaistus ja '/help' - komennon uudistus vastaamaan uusia
	komentoja.
	-Tuki usealle eri scrimille omilla ‰‰nikanavillaan samalla serverill‰
	-'/leaderboard' -komennon siistint‰
		-v‰‰r‰ntyyppisist‰ muuttujatyypeist‰ johtuvat j‰rjestysvirheet kuriin
		-turhat sanakirjat j‰rjestelyn helpottamiseen korjattu tehokkaammalla
		j‰rjestelyll‰
	-Yleit‰ koodin siistint‰‰
		-kanavan tunnistamisen ja asiaankuuluvan scrim-olion haku funktioon
		-v‰liaikaiset viestit funktioon
		-Testaukseen k‰ytettyj‰ print-rivej‰ poistettu reilulla k‰dell‰
	-Muita pieni‰ bugikorjauksia testik‰ytˆss‰ ilmenneille ongelmille



  beta 0.9.4 -- 24.10.2019

	-tuki usealle samanaikaiselle scrimille.
		-toimii niin, ett‰ jokaisella "scrim" -alkuisella kanavalla voi olla
		oma pelins‰



  beta 0.9.3 -- 23.10.2019

	-laadukkaampi tallenusmetodi ja backup-j‰rjestelm‰



  beta 0.9.2 -- 17.10.2019

	-yleisi‰ bugikorjauksia rewriten j‰lkeen



  beta 0.9.1 -- 16.10.2019

	-dokumentaation p‰ivitys muun ohjelmiston kanssa samaan vaiheeseen



  beta 0.9.0 -- 16.10.2019

	-pienimuotoinen rewrite globaalien muuttujien poistamiseksi
	implementoimalla luokka "scrim" ja pit‰m‰ll‰ muuttujat luokan
	instanssin "current" sis‰ll‰. lis‰ksi globaali lista peleist‰
	implementoitiin elo-moduulin game-luokan sis‰‰n.
	-huomioitavaa: testaajien puuttumisesta johtuen suurinta osaa komennoista
	ei ole testattu rewriten j‰lkeen.



  beta 0.8.2 -- 15.10.2019

	-'/help' -uudelleenkirjoitus
	-'leaderboard' bugikorjauksia
	-'/scrim teams pickup balanced' -implementointi elon avulla
	-'/pick random' -implementointi
	-huomioitavaa: testaajien puuttumisesta johtuen pickup- ja pick -komennot
	ovat testaamattomia. todenn‰kˆisesti tarvitsevat jonkin verran s‰‰tˆ‰.



  beta 0.8.1 -- 14.10.2019

	-/leaderboard (peli) (statistiikka)



  beta 0.8.0 -- 11.10.2019

	-elo -toimintojen implementointi
		-/scrim teams balanced
		-/scrim teams balancedrandom
		-/elo (pelaaja) (peli) (arvo)



  v 0.7.0 -- 10.10.2019

	-elo-moduulin implementointi. huomioitava, ett‰ toiminnallisuus s‰ilyi
	identtisen‰.



  v 0.6.0 -- 9.10.2019

	-/scrim teams pickup -komennon implementointi
	-reaktio-ui:n implementointi 'choose' argumentille
	-/pick (k‰ytt‰j‰) -komennon implementointi



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

							l‰hteit‰:

###############################################################################

https://discordpy.readthedocs.io/en/latest/api.html
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
lukemattomia yhden sivun oppaita ja stack overflow ongelmia kaikista kuviteltavissa
olevista Python -ominaisuuksista
