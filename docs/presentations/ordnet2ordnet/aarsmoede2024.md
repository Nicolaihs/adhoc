---
marp: true
theme: gaia
#header: 'Fra ordnet.dk til ordnet.dk'
#footer: 'Nicolai Hartvig Sørensen'
paginate: true
size: 16:9
#backgroundImage: "linear-gradient(to top, rgb(3, 22, 39), rgb(7, 44, 79))"
#color: "white"


---

<style>
img {
    display: block;
    margin: 0 auto;
}
blockquote {
    border-left: 12px solid #0288d1;
}
blockquote::before {
    content: "";
}
</style>

<!-- paginate: skip
_class: invert lead -->

# Fra ordnet.dk til ordnet.dk

## Nicolai Hartvig Sørensen

### Det Danske Sprog- og Litteraturselskabs årsmøde 2024

---

# Om mig

* Nicolai Harvig Sørensen
* email: [nhs@dsl.dk](mailto:nhs@dsl.dk)
* ansat på DSL siden 2005, udvikler på ordnet.dk 2005-

![w:1024](images/tid.png)

<!-- Jeg skal tale om et projekt om en helt ny version af ordnet.dk som vi arbejder på i øjeblikket -->

---

# Om dette projekt
  
* særbevilling fra Kulturministeriet 2023
* Carlsbergfondets bevilling til DSL 2023-25

<!-- Arbejdet med et nyt ordnet.dk var egentlig allerede i gang, men med en særbevilling fra Kulturministeriet 2023 sammen med Carlsbergfondets bevilling blev det muligt at indhente ekstern konsulenthjælp -->

---

# Hvorfor?

![h:400px](images/hvorfor.jpeg)

<!-- Først er det måske nødvendigt at fortælle hvorfor det har været nødvendigt at med en ny version af ordnet.dk. Selvom den har kørt stort set uændret siden 2009 har vi faktisk ikke rigtigt fået klager over at den ikke er tidssvarende, så hvorfor kaste sig over dette arbejde? -->

---

# Derfor 1: Teknik

![h:400px](images/bomb.jpg)

<!-- 
Den vigtigtste grund er simpelthen teknik. Hjemmesiden bliver drevet af gammel teknik som er svær at vedligeholde og som det er svært at finde konsulenter til 
-->

---

# Derfor 2: Vokseværk

![h:400px](images/growingpains.jpeg)

<!-- 
Oprindeligt var ordnet.dk designet til at vise to ordbøger, Den Danske Ordbog og Ordbog over det danske Sprog. Men 
-->

---

<style scoped>
img {
    padding: 200px 0 0 0;
}
</style>

![w:1024px](images/faneblade.png)

---

# Derfor 3: Brand-forvirring

![w:700px](images/ordnet.png)
![w:700px](images/ddo.png)

---

# Derfor 4: Ændrede tider, ændrede brugere

![w:400px](images/caveman.jpeg)

<!-- 
Der er sket meget på 15 år, ikke kun med teknikken men også med den måde brugerne tilgår vores hjemmeside.
-->

<!-- 
-->
---

![w:1024px](images/devices.png)

<!-- Næsten halvdelen af alle brugere tilgår ordnet.dk fra en smartphone - også selv der findes en dedikeret app til Den Danske Ordbog 

Og det er selvom brugerne blive mødt af denne hjemmesiden på en smartphone:
-->

---

![w:400px](images/mock.png)

---

# Derfor 5: For meget af det hele

![h:400px](images/too_much.jpg)

---

![w:1024px](images/forsimpling2.png)

---

![w:1024px](images/forsimpling1.png)

---

![w:1024px](images/ordvaeg.png)

---
<!-- 
# Derfor 6: Designproblem

![h:400px](images/oops.gif)

---

![w:1024px](images/homografproblem.png)
---
-->

# Dwarf

![h:800px](images/dwarf.png)

---

# Overblik

* Hver ordbog sit site
* "Ordnet.dk" skjult
* Åbning opad
* Inddeling i perioder

---

![w:1024px](images/ddo_forside.png)

---

![w:1024px](images/ddo_forside_annoteret.png)

---

![w:1024px](images/ddo_forside_navigation.png)

---

![w:1024px](images/navigation.png)

---

![w:1024px](images/navigation_ordnet.png)

---

![w:1024px](images/navigation_navigation.png)

---

# Overblik: Farver

![w:1024px](images/farver.png)

---

# 2 Søgning

<!-- Det var egentlig den opgave Dwarf havde fået. Men det var umuligt at stoppe dem i også
at kigge på søgeresultatet.

Jeg havde håbet på en lidt pænere stil til den søgenavigation som jeg i mellemtiden havde udviklet, men ikke andet.

Den gik ikke med Mie.
-->

---

<style scoped>
section {
    padding-top: 150px;
}
blockquote {
    font-size: 150%
}
</style>
DISCLAIMER:

> »Jeg hadede Dwarfs forslag til søgning første gang jeg så den« – _Fiktivt citat, Nicolai Hartvig Sørensen_ (2024)

---

<!-- Grundidéen er at gøre selve søgeresulatet så roligt som muligt og samtidig at gøre det nemmere at komme videre til næste relevante opslag 

Og samtidig at sikre at man er bedre hjulpet til at finde det ønskede opslagsord i første hug. Dette sker gennem end udvide autofuldførelsesliste der kommer frem søgning
-->

![w:1024px](images/old_auto.png)

---

![w:1024px](images/new_auto.png)

---

# Søgeresultat

---

![w:1024px](images/krampe1.png)

<!-- Fokus er nu udelukkende på det ord der er slået op, men stadig mulighed for at vælge en anden homograf -->

---

![w:1024px](images/krampe_below.png)

<!-- ... og under selve opslaget er der links til den samme søgning i andre bøger og i andre opslag i samme ordbog.

Modsat før er der nu plads til at vise snaser fra matchet, så brugeren med det samme kan se om det er et relevant link. I den gamle version må brugeren klikke sig ind på hver enkelt opslag for at se om det er relevant
se fx dette eksempel på en fritekst søgning i ODS nu: -->

 ---

 ![w:1024px](images/krampe_fritekst_old.png)

---

 ![bg contain](images/forside_mobil.png)
 ![bg contain](images/krampe_mobil.png)

---

<!-- Prisen for denne luksus er denne: -->

![bg cover 180%](images/krampe_annoteret.png)

<!-- Så brugeren ikke drukner i lange opslag uden at opdage de andre muligheder der nu findes under opslaget. Dette skal nok - og har allerede internt in DDO-redaktionen skabt debat -->

<!-- Og også internt i mig. Jeg protesterede over Vis mere-knappen, jeg protesterede over udelukkelsen af Alfabetisk liste og fjernelse af søgeresultatlisten til højre -->