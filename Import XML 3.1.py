#Python programming by Eric Dankaart
#Copyright by Eric Dankaart, 2020
#XML Loonaangifte importer



"""RELEASE NOTES Import  XML 3.1

New in 3.1. Versie:

- In de functie dashboard zijn een aantal standaard queries gedefinieerd. "Leeftijden" toont de leeftijden van het personeelbestand. Daartoe is de 'datetime' library ingeladen. Ook de gemiddelde leeftijd wordt berekend. Hiervoor is een global var 'somleeftijden' aangemaakt. 



In versie 3.1 zijn de volgende functies aanwezig:
- inlezen van loonaangiften (keuze naar naam van de file). Loonaangifte.xml is de standaard, andere testfiles zijn nu LBTEST12JAN.txt en LBTEST12FEB.txt. Het aantal van 12 slaat op het aantal werknemers; deze files zijn een stuk kleiner en derhalve sneller voor testdoeleinden.
- afsplitsen collectieve deel aangifte 
- inlezen individuele werknemerdata in een numpy array
- inlezen van de 85 mogelijke veldnamen die gebruikt worden als headers in de werknemerdata array
- mogelijkheid om de file waarin de standaardveldnamen staan (LHTAGS) in te lezen en te bewerken (voor de zekerheid bestaat ook een LHTAGS KOPIE)
- ontbrekende veldnamen in de individuele werknemerdata worden aangevuld met de ontbrekende veldnaam, als waarde wordt "None" weergegeven. Toegvoegde veldnamen zijn herkenbaar omdat zowel begin als eindtag hetzelfde zijn; de eindtag heeft geen "/".
- simpele routine voor slicen & dicen


- probleem met het inlezen van het onjuiste aantal werknemers is opgelost door bij het inlezen gebruik te maken van twee lijsten; de lijst met daarin de laatste positie van <InkomstenverhoudingInitieel> en de lijst met de eerste positie van de eindtag </InkomstenverhoudingInitieel>. 
- probleem met woonplaats A/D is opgelost. Het teken "/" werd niet ingelezen waardoor een verkeerd aantal velden ontstond. Oplossing is gevonden door wel het teken "/" uit de werknemerdata in te lezen. Consequentie hiervan is dat nu bij de ingelezen tags begin en eindtag verschillend zijn, <voorbeeld> en </voorbeeld>, waardoor ook de zoekfunctie in showvalues() aangevuld moest worden.
- er is een nieuwe 'slicedice' functie, waarmee gekozen kan worden welke rijen en welke kolommen geprint moeten worden. De 'oude' slicedice-functie waarin er van-tot geselecteerd kon worden in de rijen en kolommen is hier direct onder nog opgenomen (commented out). 
Nieuw t.o.v. 3.0 version:

Er wordt niet langer altijd dezelfde file ingelezen, maar er kan gekozen worden. Met 's' wordt de 'standaardfile" ingelezen. Dit maakt het mogelijk om te werken met een wat kortere (en andere) testfile.
De collectieve gegevens die nog in letters waren ingelezen zijn nu vertaald in tags (colltags).
De bug in 3.0 m.b.t. het inlezen van de collectieve gegevens is hersteld; er wordt nu ingelezen t/m </CollectieveAangifte> zodat alle collectieve data ingeladen worden
Dashboard toegevoegd: de functie 'colltagsmeaning' is toegevoegd om de tags in het collectieve deel en meer begrijpelijke naam te geven waarna ze verzameld in een lijst (dash). Per dash[item] kan er nu een maatwerk rapport van gemaakt worden. De functie dashboard() roept deze aan.
De functie 'meaning' is toegevoegd, deze functie vertaalt de werknemer tags naar meer begrijpelijke begrippen. De functie bevat nog niet alle tags.
Er is een overzicht van de soorten inkomstenverhouding ingevoegd, vooral om te kijken of e.e.a. handig zou kunnen werken (koppeling met een dictionaire).




Issues to be solved:
- het is vastgesteld dat er 2 maal een tag "DatAanv" voorkomt in de werknemerstags, op positie 1 en op positie 19. De 1e tag (positie 1) gaat over de Datum Aanvang Inkomstenverhouding, de 2e tag (positie 19) gaat over begindatum van de Inkomstenperiode. 


Ideas voor next releases:

- Een functie convertfig(); deze functie verwijdert betekenisloze voorloopnullen uit cijfers.
- Slicedice keuzemenu maken tussen de 2 verschillende manieren (selectie aansluitende rijen/kolommen of bepaalde rijen/kolommen)
- Wegschrijven van de numpy-array als voorbereiding op:
- inlezen meerdere maanden en creeren gecombineerde 3d-array

"""


import re
import numpy as np
import datetime
x = datetime.datetime.now()
print(x)

data=np.array([]) #this array stores the incoming xml wage tax return data
 # this array stores the collective part of the wage tax return, see the function collective
wn=np.array([]) # this array stores the data of the individual employees, not yet sorted in tags. The sorted data array is...
tagswn=[] # this list contains the various tags in the individual part of the wage tax return
span=(0,0)
endofcol=0
colltags=[]
startpuntwn=[]# this list contains the startposition of the individual employeedata in the datafile "data".
eindpuntwn=[]# this list containt the eindposition of the individual employeedata in the datafile "data".
aantalwn=0
veld=0
velden=[]
veldnamen=np.array([])
werknemer=[]#lijst met alle waarden voor een individuele werknemer. De veldnamen zijn hier geen onderdeel meer van. De gegevens worden overgezet in de array werknemers, waar gecombineerd met de bijbehorende array velnamen alles in een array is verzameld (m.u.v. collectieve deel)
werknemers=np.array([])
veld_werknemers=np.array([])
dash=[]


def fileread(): # this function reads the Loonaangifte.xml file and stores it in the array 'data'
    global data
    global naam
    naam=""
    while naam=="":
        naam=input("Wat is de naam van de file die je wil inlezen? Druk op s voor de standardfile. Druk op t voor kleine testfile van 12 werknemers. ")
        if naam=="s":
            naam="Loonaangifte.xml"
        if naam=="t":
            naam="LBTEST12JAN.txt"
    file=open(naam,"r")
    data=file.read()
    print("De file is ingelezen. ", end="")
    print("Het aantal tekens van de file bedraagt ", len(data))
    file.close()
   
    
def findword(zoek): # zoekfunctie die het woord "zoek" in de xml-file opzoek. Als output wordt de variabele start teruggegeven met daarin als waarde het EINDE van het woord. De variabele heeft start omdat het de start is van de INHOUD van een tag die als zoekwoord is ingegeven. De functie readcont() gebruikt start als variabel om vervolgen de content van de tag weer te geven. Bijvoorbeeld LhNr zoekt naar deze tag en levert via de functie reterug het loonheffingennummer in de file. 
    global span
    gevonden=re.search(zoek,data)
    if gevonden:
        #print(gevonden.group())
        #print(gevonden.start())
        span=gevonden.span()
        #print(span) #begin en einde van het gevonden woord worden geprint
        #print(zoek,": ")
        start=span[1]+1 #start is the var that indicates the exact position of the content after the word found, hence the second value in span[0,1]. Since it's known that there is always a ">" character after the word, we add 1 for the starting point
        return start
    else:
        start=0#als het woord niet in de file gevonden wordt, dan wordt er fictief 0 als startwaarde genoemd.
        print("Woord niet in file gevonden")
        return start
    
def readcont(start):# this routine reads the content at a given position in the file untill it encounters a "<" or ">". The findword() function can be nested in, the output will than be the content of a certain tag.
    content=""
    for i in range(0,30):#het getal 30 is genomen omdat verondersteld wordt dat dit de maximale lengte van het woord is
        letter=data[start+i]
        if letter!="<" and letter!=">":
            #print("Ik vond de letter ",letter," op positie ",start+i)
            content+=letter
        else:
            continue
        return content
        
def collective():# deze functie splitst het collectieve deel van de aangifte af
    global endofcol #dit getal wordt hergebruikt voor andere functies
    global colltags
    colltags=[]
    inhoud=""
    found=re.search("/CollectieveAangifte",data)#zoek het laatste woord van het collectieve deel, nl "CollectieveAangifte".
    if found:
        wloc=found.span() # de tuple 'wloc (van "woordlocatie") bevat het nummer waarop het woorde "CollectieveAangifte" begint en waarop het eindigt. De waarde in wloc[1] is het begin van de individuele gegevens. Deze var wordt hierna opgenomen in endofcol (=einde van het collectieve deel van de aangifte)
        endofcol=wloc[1] #hier wordt in de var endofcol (=einde van de collectieve aangifte) het tweede cijfer van de tuple wloc overgenomen.
    else:
        print("Error,einde van collectieve aangifte niet gevonden")
        raise ValueError
    collfile=np.array([])
    for i in range(0,endofcol):
        collfile=np.append(collfile,data[i])
    print(collfile.shape)
    print(collfile) # print de collfile uit, oftwel alle collectieve gegevens. Valt te overwegen om nog met de routine in gettagswn er tags van te maken.
    for q in range(0,endofcol):
        letter=collfile[q]
        if letter!="<" and letter!=">" and letter!="/" and letter!="": #de letters worden hier toegevoegd aan de var content totdat de for loop een < of > of / of "" tegenkomt, dat is nl het teken dat er een nieuwe tag begint met daarin ook evt. waarden
            inhoud+=letter
        elif inhoud!="":
            colltags.append(inhoud)
            inhoud=""
    #print(colltags)
        

def colltagsmeaning():
    global dash
    for q in range(0, len(colltags)-2):#omdat deze functie 2 vooruit kijkt (colltags[q+2]) moet er -2 in de de for loop, anders ontstaat een list index out of range error...
        if colltags[q]=="DatTdAanm" and colltags[q+2]=="DatTdAanm":
            dash.append("Datum/tijdstip aanmaken: "+colltags[q+1])
        if colltags[q]=="Loonaangifte":
            dash.append("Jaar "+ colltags[q+1]+" periode "+colltags[q+2])
        if colltags[q]=="LhNr" and colltags[q+2]=="LhNr":
            dash.append("Loonheffingennr."+ "         "+ colltags[q+1])
        if colltags[q]=="DatAanvTv" and colltags[q+2]=="DatAanvTv":
            dash.append("Datum aanvang tijdvak:"+"   "+colltags[q+1])
        if colltags[q]=="DatEindTv" and colltags[q+2]=="DatEindTv":
            dash.append("Datum einde tijdvak:"+"     "+ colltags[q+1])
        if colltags[q]=="TotLnLbPh" and colltags[q+2]=="TotLnLbPh":
            dash.append("Totaal loon voor LB/PH"+"   "+ "€ " + convertfig(colltags[q+1]))
            

def wntagsmeaning():#deze functie geeft de betekenis van de tags in het individuele deel van de aangifte
    return
            
              


def convertfig(a):
    getal=""
    for letter in a:
        if letter!="0":
            getal+=letter
    return getal
             
def recordwn(a,b):#deze functie vult de gegevens uit de file data een array met de naam wn. Alle individuele letters komen daarbij in de array. Verdere verwerking om van deze letters 'tags' en de content van deze tags te maken vindt plaats met de functie gettagswn().
    global wn
    wn=[]# De lijst wn wordt steeds leeg gemaakt. Verder stapelen van de wn-data vindt plaats in de 2d-array 'werknemers', nadat eerst de waarden per werknemer zijn verzameld in de lijst 'werknemer'.
    for i in range(a,b):
        wn=np.append(wn,data[i])# moet hierna een np.vstack of np.hstack voor het stapelen in een 2d array????
    #for i in range(0,len(wn)):
        #print(wn[i],end=" ")
  
def gettagswn():# deze routine gaat door een array met individuele werknemergegevens (gemaakt met de functie recordwn) en maakt er vervolgens een lijst met tags en de waarden horend bij die tags van. Als er sprake is van een begin en een eindtag, dan vindt ontdubbeling plaats zodanig dat een eventuele waarde altijd volgt op de tag.
    global tagswn
    tagswn=[]#leeg maken van de tags
    content=""
    for i in range(0,len(wn)):
        letter=wn[i]
        if letter!="<" and letter!=">":# de letters worden hier toegevoegd aan de var content totdat de for loop een < of > tegenkomt, dat is nl het teken dat er een nieuwe tag begint met daarin ook evt. waarden
            content+=letter
        elif content!="":
            tagswn.append(content)
            content="" 
    #print(tagswn) #hier worden de verkregen tags per werknemer geprint. Dit zijn dus de gegevens van een individuele werknemer.
    
def checktagswn():#deze functie beoordeelt de tags van de individuele werknemer op ontbreken van tags, zodat later aangevuld kan worden
    gevonden=0
    #lasttagfound=""
    #print("Ik ga vergelijken met de volgende tags:",velden)
    #print("Met deze werknemerdata",tagswn)
    for i in range(0,len(velden)):
        for t in range(i,len(tagswn)):#het begin van t kan niet liggen op een lagere waarde dan i!!!
            if velden[i]==tagswn[t]:
                gevonden=1
                lasttagfound=velden[i]
        if gevonden==0:# als het veld in de standaard velden lijst ontbreekt nadat er in de vorige routine in de volledige lijst (tagswn) is gezocht, dan ontbreekt het betreffende veld er vindt hierna aanvulling in tagswn plaats.
            #print(velden[i],"ontbreekt.")
            #print("Het laatste wel aanwezige veld is:",lasttagfound)
            #print("Ik heb deze tag gevonden op positie :",tagswn.index(lasttagfound))#de tag voorafgaand aan de ontbrekende tag wordt opgezocht in de data van de individuele werknemer op basis van de index in die lijst
            invoeg=tagswn.index(lasttagfound)
            tagswn.insert(invoeg+3,velden[i])
            tagswn.insert(invoeg+4,"None")
            tagswn.insert(invoeg+5,velden[i])
        gevonden=0
        #lasttagfound=""#CHECK of deze var inderdaad leeg gemaakt moet worden en of dat hier moet. Het lijkt overbodig omdat bij het herstarten van de routine steeds een nieuwe 'lasttagfound' gevuld wordt.
    #print("De tagswn lijst voor deze werknemer is nu:",tagswn)

def writetags():#hier wordt de array van veldnamen omgezet in een string die weggeschreven wordt in LHTAGS
    stringveldnamen=""
    for i in range(len(veldnamen)):
        #print((i+1), ": ", end=" ")
        #print(veldnamen[i])
        stringveldnamen=stringveldnamen+" "+veldnamen[i]
    file=open("LHTAGS","w+")
    file.write(stringveldnamen)
    file.close()

def readtags():
    file=open("LHTAGS","r")
    stringveldnamen=file.read()
    file.close()
    global velden
    velden=[]
    velden=stringveldnamen.split() #Deze routine kan gebruikt worden om ter controle de velden ingelezen uit LHTAGS te printen
    #for i in range(0,len(velden)):
        #print((i),end=" ")
        #print(velden[i])
               
def insertdeltags():#deze routine maakt het mogelijk om in file waarin de string van weggeschreven wn-tags zich bevindt, wijzigingen aan te brengen.
    wegschrijfstring=""
    a=""
    while a=="":
        a=input("Wil je tags (i)nvoegen of (v)erwijderen?")
        if a=="i" or a=="I":
            b=int(input("Na welke positie wil je invoegen?"))#noot foutafvangen nog toevoegen
            if b<1 or b>len(velden):
                print("onmogelijk, geef svp positie tussen 1 en ",len(velden))
            else:
                c=str(input("Wat is de naam van de tag die ik moet invoegen? Let goed op spelling en hoofd- en kleine letters!"))
                velden.insert(b,c)
                print("De nieuwe taglist is: ")
                for z in range(0,len(velden)):
                    wegschrijfstring=wegschrijfstring+" "+velden[z] #hier wordt een string gemaakt met spaties tussen de tags, een lijst kan nl zo niet worden weggeschreven.
                    print((z+1),velden[z]) # dit is enkel om de gebruiker te tonen dat er een nieuw lijst is gemaakt
                print(wegschrijfstring)
                file=open("LHTAGS","w+")
                file.write(wegschrijfstring)
                file.close()
        if a=="v" or a=="V":
            v=int(input("De tag op welke positie wil je verwijderen?"))#evt. het afvangen van invoerfouten nog toevoegen
            if v<1 or v>len(velden):
                print("onmogelijk, geef svp positie tussen 1 en ",len(velden))
            else:
                print("Ok, het veld wat je wil verwijderen is dus:",velden[v])
                ant=str(input("Weet je zeker dat je dit veld wil verwijderen (J/N)?"))
                if ant=="J" or ant=="j":
                    velden.pop(v)
                    print("De nieuwe taglist is: ")
                for z in range(0,len(velden)):
                    wegschrijfstring=wegschrijfstring+" "+velden[z] #hier wordt een string gemaakt met spaties tussen de tags, een lijst kan nl zo niet worden weggeschreven.
                    print((z+1),velden[z]) # dit is enkel om de gebruik te tonen dat er een nieuw lijst is gemaakt
                print(wegschrijfstring)
                file=open("LHTAGS","w+")
                file.write(wegschrijfstring)
                file.close()
                                              
def record():
    global werknemers
    global werknemer
    werknemers=np.vstack((werknemers,werknemer))
    werknemer=[]
                   
def meaning(tag):# met deze functie kunnen alle tags worden vervangen door meer begrijpelijke omschrijvingen.
    if tag=="NuMIV":
        return "Nummer Inkomstenverhouding"
    if tag=="DatAanv":
        return "Datum aanvang dienstverband:"
    if tag=="PersNr":
        return "Personeelsnummer:"
    if tag=="SofiNr":
        return "BSN:"
    if tag=="Voorl":
        return "Voorletters:"
    if tag=="SignM":
        return "Achternaam"
    if tag=="Gebdat":
        return "Geboortedatum"
    if tag=="Nat":
        return "Nationaliteit"
    if tag=="Gesl":
        return "Geslacht"
    if tag=="Str":
        return "Straat"
    if tag=="Huisnr":
        return"Huisnr"
    if tag=="LocOms":
        return "Locatie Omschrijving"
    if tag=="HuisnrToev":
        return "Huisnummer toevoeging"
    if tag=="Pc":
        return "Postcode:"
    if tag=="Woonpl":
        return "Woonplaats"
    if tag=="LandCd":
        return "Landcode"
    if tag=="Reg":
        return "Regio:"
    if tag=="IngLbPh":
        return "Ingehouden LB/PH:"
    if tag=="WrdPrGebrAut":
        return "Waarde prive-gebruik auto:"
    else:
        return tag+":"

def zoekbeginwerknemer(a,b):#deze functie geeft alle locaties waar een zoekwoord voorkomt in de file. Met het juiste zoekwoord (<InkomstenverhoudingInitieel>)kunnen hiermee startpunt en eindpunt van de repeterende reeks van werknemergegevens gevonden worden.
    global aantalwn
    if re.search(a,data):
        for m in re.finditer(a,b):
            #print("%d-%d: %s" %(m.start(),m.end(),m.group(0)))
            startpuntwn.append(m.end())#file the enddata in de lijst 'startpuntwn". De enddata betreffen de positie waar het woord <InkomstenverhoudingInitieel> geeindigd is
        aantalwn=len(startpuntwn)#aantal werknemers wordt hier bepaald
        print("Er zijn ",aantalwn,"individuele werknemers verloond.")
        #print(startpuntwn)

def zoekeindwerknemer(c,b):
    if re.search(c,data):
        for m in re.finditer(c,b):
            #print("%d-%d: %s" %(m.start(),m.end(),m.group(0)))
            eindpuntwn.append(m.start())#bij het eindpunt wil je de laatste letter hebben, dat is dus de START van het woord dat je zoekt.
        #print(eindpuntwn)
                
def showvalues():#deze functie zoekt naar waarden in de file tagswn. Dit gebeurt door een weergave te doen hetgeen tussen 2 dezelfde 'tags' staat. Er is voor gekozen de tags niet te definieren (evt zou dit kunnen om nog zekerder te zijn van de inhoud)
    #nummer=0 #nummer nummert de tags. Inmiddels is bekend dat het er waarschijnlijk 76 zijn, waarbij de velden "VoorV" en "HuisNrToev" en "LandCd"  en "CdIncInkVerm" in deze file niet opgenomen worden in gettagswn()
    global veld#veld is de var die bijhoudt of de veldnamen al gegenereerd zijn. Indien veld == 0 dan vindt vulling van de array veldnamen plaats. Aan het eind van deze routine wordt veld op 1 gezet, zodat het slechts 1 maal gebeurt..
    global veldnamen
    global werknemer
    global werknemers
    wnveldnamen=[]#in deze lijst worden alleen de veldnamen per werknemer bewaard. Dit om te kunnen controleren of het aantal veldnamen minimaal voldoet aan 72 stuks en eventueel ontbrekende veldnamen te kunnen toevoegen en vullen. 
    for i in range(0,len(tagswn)-2):#min 2 is nodig omdat een tag kan horen bij een tag 2 verderop..... Dit ter voorkoming list index out of range error..
        if "/"+tagswn[i]==tagswn[i+2] or tagswn[i]==tagswn[i+2]: #als de tag gelijk is aan de tag die er twee na komt, dan moet de inhoud ervoor (dus tag+1) opgehaald worden.    
            wnveldnamen.append(tagswn[i])
            if veld==0:
                veldnamen=np.append(veldnamen,tagswn[i])
            #hier worden de veldnamen in een array gestopt. Punt is dat dit maar 1 keer hoeft te gebeuren en niet voor elke wn-er. De var veld regelt dit.
            #nummer+=1
            #print(nummer,end=" ")
            #print(meaning(tagswn[i]),end=" ")# deze routine vertaalt de tags naar meer begrijpelijke termen. Kan uitgezet worden om de performance te verbeteren. 
            #print(tagswn[i+1])
            werknemer.append(tagswn[i+1])
    #print("-----------------------")# even een streepje zetten tussen de werknemers.
    
    if veld==0:
        werknemers=np.append(werknemers,veldnamen)# vul de array werknemers met de veldnamen als headers. Dit is de eerste rij. De overige werknemers worden toegevoegd als rij in de functie record met vstack (append zou leiden tot verlenging van de array in 1d).De var veld wordt gebruikt omdat in deze routine, waar de werknemerdata telkens worden toegevoegd de veldnamen slechts eenmaal worden toegevoegd en wel aan het begin zodat de header bovenaan staat!
        #if len(veldnamen)>=72:
            #writetags()# verwijzing naar de functie waar de array van veldnamen wordt omgezet in een string die weggeschreven wordt in LHTAGS. Als dit al is gebeurt dan is het niet nodig dat nogmaals te doen (wegens performance beter van niet)
        if len(veldnamen)!=85:
            print("ERROR, aantal veldnamen is niet gelijk aan 85!")
    if len(werknemer)==85:# dit is het aantal tags dat per werknemer aanwezig moet zijn, gebaseerd op het aantal in de standaardtaglist LHTAGS. 
        record()           
    else:
        print("Afwijkend aantal velden gevonden voor werknemer. De gegevens van deze werknemer heb ik niet verwerkt. Het aantal velden bedroeg:", len(werknemer))
        print(werknemer)
        werknemer=[]#leegmaken. Gebeurt normaal in functie record, maar die wordt nu omzeild omdat het aantal velden niet gelijk is aan 85
    
    veld=1# door veld te verhogen wordt bereikt dat niet nogmaals de veldnamen worden uitgelezen als er een nieuwe wntag wordt ingelezen. Tevens wordt voorkomen (zie regels hier direct boven) dat 

        
def show(a):
    if a>=aantalwn:
        a=aantalwn
    for t in range(0,a):
        recordwn(startpuntwn[t],eindpuntwn[t])
        gettagswn()
        checktagswn()
        showvalues()
        #print("Processed werknemernummer",t)
    #print(werknemers)
    #print(werknemers.shape)
        
     
  
def leeftijden(string):
    datum=string.split("-")
    jaar=""
    maand=""
    dag=""
    for i in datum[0]:#deze routine zorgt ervoor dat enkel cijfers tussen 0 en 9 geaccepteerd worden. Eventuele 'vervuiling' in de dataset (ingelezen "[]" ) worden hier verwijderd.
        if ord(i)>=48 and ord(i)<=57:
            jaar+=i
        #print(jaar)
    year=int(jaar)       
    for i in datum[1]:        
        if ord(i)>=48 and ord(i)<=57:
            maand+=i
    month=int(maand)    
    for i in datum[2]:
        if ord(i)>=48 and ord(i)<=57:
            dag+=i
    day=int(dag)
    
    gebdat=datetime.date(year,month,day)
    huidigedatum=datetime.date(2021,1,29)
    time_difference=huidigedatum-gebdat
    age=time_difference.days
    leeftijd=age//365#strikt genomen kan deze functie wel eens een onjuiste leeftijd aangeven! Immers, een jaar is niet altijd 365 dagen..
    return leeftijd
   
    
    
     
def dashboard(zz):
    if zz=="leeftijden":
        global somleeftijden
        somleeftijden=0
        for i in range(1, aantalwn):
            string=str(werknemers[i,7:8])
            leeftijd=(leeftijden(string))
            print(leeftijd)
            somleeftijden+=leeftijd
    print("De gemiddelde leeftijd is ",round(somleeftijden/aantalwn,2))
    if zz=="woonplaatsen":
        return

        
"""
def slicedice():
    startrij=int(input("startrij ? "))
    eindrij=int(input("eindrij ? "))
    startkolom=int(input("startkolom? "))
    eindkolom=int(input("eindkolom? "))
    print(werknemers[startrij:eindrij,startkolom:eindkolom])
"""    

def slicedice():
    rijen=[]
    kolommen=[]
    a=input("Welke rijen? ")
    rijen=a.split()
    b=input("Welke kolommen?" )
    kolommen=b.split()
    for i in range(0,len(rijen)):
        for t in range(0,len(kolommen)):
            print(werknemers[int(rijen[i]):int(rijen[i])+1,int(kolommen[t]):int(kolommen[t])+1],end="")
        print("")
        print("-------------------------")    
    
    
    



inkomstenverhouding={11:" Loon of salaris ambtenaren in de zin van de Ambtenarenwet",13:"Loon of salaris directeuren van een nv/bv, wel verzekerd voor de werknemersverzekeringen",
                     15:" Loon of salaris niet onder te brengen onder 11, 13 of 17",17:" Loon of salaris directeur-grootaandeelhouder van een nv/bv, niet verzekerd voor dewerknemersverzekeringen",
                     18:" Wachtgeld van een overheidsinstelling",22:" Uitkering in het kader van de Algemene Ouderdomswet (AOW)",23:" Oorlogs- en verzetspensioenen",
                     24:" Uitkering in het kader van de Algemene nabestaandenwet (ANW)",31:"Uitkering in het kader van de Ziektewet (ZW) en vrijwillige verzekering Ziektewet",
                     32:" Uitkering in het kader van de Wet op de arbeidsongeschiktheidsverzekering (WAO) en particuliere verzekering ziekte, invaliditeit en ongeval",
                     33:" Uitkering in het kader van de Nieuwe Werkloosheidswet (nWW)",34:"Uitkering in het kader van de Wet inkomensvoorziening oudere en gedeeltelijk arbeidsongeschikte werkloze werknemers (IOAW)",
                     35:"Vervolguitkering in het kader van de Nieuwe Werkloosheidswet (nWW)",36:"Uitkering in het kader van de Wet arbeidsongeschiktheidsverzekering zelfstandigen (Waz)",
                     37: "Wet arbeidsongeschiktheidsvoorziening jonggehandicapten (Wajong)",38: "Samenloop (gelijktijdig of volgtijdelijk) van uitkeringen van Wajong met Waz, WAO/IVA of WGA",
                     39: "Uitkering in het kader van de Regeling inkomensvoorziening volledig arbeidsongeschikten (IVA)",40:"Uitkering in het kader van de Regeling werkhervatting gedeeltelijk arbeidsgeschikten (WGA)",
                     42: "Uitkering in het kader van bijstandsbesluit Zelfstandigen (Bbz)",43: "Uitkering in het kader van de Participatiewet (voorheen WWB)",
                     45: "Uitkering in het kader van de Wet inkomensvoorziening oudere en gedeeltelijk arbeidsongeschikte gewezen zelfstandigen (IOAZ)",
                     46: "Uitkering uit hoofde van de Toeslagenwet",
                     50: "Uitkeringen in het kader van overige sociale verzekeringswetten, hieronder vallen tevens: Ongevallenwet 1921, Land- en tuinbouwongevallenwet 1922 en Zeeongevallenwet 1919 (niet 22, 24, 31 tot en met 45 of 52)",
                     52: "Uitkering in het kader van de Wet inkomensvoorziening oudere werklozen (IOW)",54: "Opname levenslooptegoed door een werknemer die op 1 januari 61 jaar of ouder is",
                     55: "Uitkering in het kader van de Algemene Pensioenwet Politieke Ambtsdragers (APPA)",
                     56: "Ouderdomspensioen dat via de werkgever is opgebouwd of ouderdomspensioen opgebouwd via een verplichte beroepspensioenregeling / bedrijfstakpensioenregeling",
                     57: "Nabestaandenpensioen dat via de werkgever is opgebouwd of nabestaandenpensioen opgebouwd via een verplichte beroepspensioenregeling / bedrijfstakpensioenregeling",
                     58: "Arbeidsongeschiktheidspensioen dat via de werkgever is opgebouwd of arbeidsongeschiktheidspensioen opgebouwd via een verplichte beroepspensioenregeling/bedrijfstakpensioenregeling",
                     59: "Lijfrenten die zijn afgesloten in het kader van een individuele of collectieve arbeidsovereenkomst 60 Lijfrenten die niet zijn afgesloten in het kader van een individuele of collectieve arbeidsovereenkomst",
                     61: "Aanvulling van de werkgever aan een werknemer op een uitkering werknemersverzekeringen, terwijl de dienstbetrekking is beëindigd",
                     62: "Ontslagvergoeding / transitievergoeding",
                     63: "Overige, niet hiervoor aangegeven, pensioenen of samenloop van meerdere pensioenen/lijfrenten of een betaling op grond van een afspraak na einde dienstbetrekking"}
    
  
####PROGRAM EXECUTION #################  
fileread()
zoekbeginwerknemer("<InkomstenverhoudingInitieel>",data)#aanmaken lijst startpuntwn; met daarin de startpunten voor het uitlezen van de individuele werknemerdata in data EN het aantalwerknemers in 'aantalwn'
zoekeindwerknemer("</InkomstenverhoudingInitieel>",data)# aanmaken lijst eindpuntwn; eindpunten voor het uitlezen van de individuele werknemerdata
collective()#deze functie zet in collfile de collectieve gegevens. De bijbehorende lengte van het aantal gegevens is endofcol.
colltagsmeaning()





#insertdeltags()

readtags()
show(177)
dashboard("leeftijden")



"""DEVELOPMENT IDEAS
000000 in werknemerdata vervangen door 0. Idem m.bt. andere waarden. Omzetten naar int of float?
Slicing & dicing
Collective data in handzaam overzicht tonen.
"""


