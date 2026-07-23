from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os, random, hashlib, json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'konkou-septa-xK9mP3!')
CORS(app)
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# ── BANK KESYON — 20 pa kategori/nivo, 3 lang ─────────────────────────────────
# Chak kesyon gen: q_ht, q_fr, q_en, opts_ht, opts_fr, opts_en, ans
QUESTIONS = {
  "geo": {
    "easy": [
      {"q_ht":"Ki kapital peyi Fransè?","q_fr":"Quelle est la capitale de la France?","q_en":"What is the capital of France?","opts_ht":["Pari","Lyon","Masey","Bòdo"],"opts_fr":["Paris","Lyon","Marseille","Bordeaux"],"opts_en":["Paris","Lyon","Marseille","Bordeaux"],"ans":0},
      {"q_ht":"Ki pi gwo osean sou tè a?","q_fr":"Quel est le plus grand océan du monde?","q_en":"What is the largest ocean on Earth?","opts_ht":["Atlantik","Endyen","Pasifik","Arktik"],"opts_fr":["Atlantique","Indien","Pacifique","Arctique"],"opts_en":["Atlantic","Indian","Pacific","Arctic"],"ans":2},
      {"q_ht":"Ki kontinen ki pi gran?","q_fr":"Quel est le plus grand continent?","q_en":"What is the largest continent?","opts_ht":["Afrik","Azì","Ewòp","Amerik"],"opts_fr":["Afrique","Asie","Europe","Amérique"],"opts_en":["Africa","Asia","Europe","America"],"ans":1},
      {"q_ht":"Ki rivyè ki pi long nan mond lan?","q_fr":"Quel est le fleuve le plus long du monde?","q_en":"What is the longest river in the world?","opts_ht":["Amazon","Nil","Mississippi","Yangtsé"],"opts_fr":["Amazone","Nil","Mississippi","Yangtsé"],"opts_en":["Amazon","Nile","Mississippi","Yangtze"],"ans":1},
      {"q_ht":"Ki peyi ki gen pi gwo popilasyon?","q_fr":"Quel pays a la plus grande population?","q_en":"Which country has the largest population?","opts_ht":["Amerik","Zend","Lachin","Ris"],"opts_fr":["États-Unis","Inde","Chine","Russie"],"opts_en":["USA","India","China","Russia"],"ans":2},
      {"q_ht":"Ki mòn ki pi wo nan mond lan?","q_fr":"Quelle est la plus haute montagne du monde?","q_en":"What is the highest mountain in the world?","opts_ht":["K2","Everès","Kilimanjaro","Elbrous"],"opts_fr":["K2","Everest","Kilimandjaro","Elbrouz"],"opts_en":["K2","Everest","Kilimanjaro","Elbrus"],"ans":1},
      {"q_ht":"Ki kapital peyi Brezil?","q_fr":"Quelle est la capitale du Brésil?","q_en":"What is the capital of Brazil?","opts_ht":["Rio de Janeiro","São Paulo","Brasilia","Salvador"],"opts_fr":["Rio de Janeiro","São Paulo","Brasilia","Salvador"],"opts_en":["Rio de Janeiro","São Paulo","Brasilia","Salvador"],"ans":2},
      {"q_ht":"Ki peyi ki pi gran nan mond lan?","q_fr":"Quel est le plus grand pays du monde?","q_en":"What is the largest country in the world?","opts_ht":["Kanada","Etazini","Ris","Lachin"],"opts_fr":["Canada","États-Unis","Russie","Chine"],"opts_en":["Canada","USA","Russia","China"],"ans":2},
      {"q_ht":"Ki peyi Nil travèse?","q_fr":"Quel pays le Nil traverse-t-il?","q_en":"Which country does the Nile flow through?","opts_ht":["Maroc","Ejipt","Libi","Aljerí"],"opts_fr":["Maroc","Égypte","Libye","Algérie"],"opts_en":["Morocco","Egypt","Libya","Algeria"],"ans":1},
      {"q_ht":"Ki kapital peyi Japon?","q_fr":"Quelle est la capitale du Japon?","q_en":"What is the capital of Japan?","opts_ht":["Osaka","Kyoto","Tokyo","Hiroshima"],"opts_fr":["Osaka","Kyoto","Tokyo","Hiroshima"],"opts_en":["Osaka","Kyoto","Tokyo","Hiroshima"],"ans":2},
      {"q_ht":"Ki dezè ki pi gran nan mond lan?","q_fr":"Quel est le plus grand désert du monde?","q_en":"What is the largest desert in the world?","opts_ht":["Sahara","Gobi","Arabie","Antarktik"],"opts_fr":["Sahara","Gobi","Arabie","Antarctique"],"opts_en":["Sahara","Gobi","Arabian","Antarctic"],"ans":3},
      {"q_ht":"Ki peyi ki gen pi plis lak?","q_fr":"Quel pays possède le plus de lacs?","q_en":"Which country has the most lakes?","opts_ht":["Etazini","Ris","Kanada","Finlann"],"opts_fr":["États-Unis","Russie","Canada","Finlande"],"opts_en":["USA","Russia","Canada","Finland"],"ans":2},
      {"q_ht":"Ki kapital peyi Almay?","q_fr":"Quelle est la capitale de l'Allemagne?","q_en":"What is the capital of Germany?","opts_ht":["Munich","Hambourg","Frankfort","Bèlin"],"opts_fr":["Munich","Hambourg","Francfort","Berlin"],"opts_en":["Munich","Hamburg","Frankfurt","Berlin"],"ans":3},
      {"q_ht":"Ki zile ki pi gran nan mond lan?","q_fr":"Quelle est la plus grande île du monde?","q_en":"What is the largest island in the world?","opts_ht":["Borneo","Groenland","Madagaskar","Nouyegini"],"opts_fr":["Bornéo","Groenland","Madagascar","Nouvelle-Guinée"],"opts_en":["Borneo","Greenland","Madagascar","New Guinea"],"ans":1},
      {"q_ht":"Ki kapital Ostralazi?","q_fr":"Quelle est la capitale de l'Australie?","q_en":"What is the capital of Australia?","opts_ht":["Sydney","Melbourne","Canberra","Perth"],"opts_fr":["Sydney","Melbourne","Canberra","Perth"],"opts_en":["Sydney","Melbourne","Canberra","Perth"],"ans":2},
      {"q_ht":"Ki kontinan ki pi piti?","q_fr":"Quel est le plus petit continent?","q_en":"What is the smallest continent?","opts_ht":["Ewòp","Ostralazi","Antarktik","Amerik di Sid"],"opts_fr":["Europe","Australie","Antarctique","Amérique du Sud"],"opts_en":["Europe","Australia","Antarctica","South America"],"ans":1},
      {"q_ht":"Ki peyi ki separe pa Kanal Panama?","q_fr":"Quel pays est traversé par le Canal de Panama?","q_en":"Which country is crossed by the Panama Canal?","opts_ht":["Kosta Rika","Panama","Kolonbi","Meksik"],"opts_fr":["Costa Rica","Panama","Colombie","Mexique"],"opts_en":["Costa Rica","Panama","Colombia","Mexico"],"ans":1},
      {"q_ht":"Ki kapital peyi Kiba?","q_fr":"Quelle est la capitale de Cuba?","q_en":"What is the capital of Cuba?","opts_ht":["Santiago","La Havàn","Varadero","Matanzas"],"opts_fr":["Santiago","La Havane","Varadero","Matanzas"],"opts_en":["Santiago","Havana","Varadero","Matanzas"],"ans":1},
      {"q_ht":"Ki peyi ki rele 'Peyi Solèy Leve'?","q_fr":"Quel pays est appelé 'Pays du Soleil Levant'?","q_en":"Which country is called 'Land of the Rising Sun'?","opts_ht":["Lachin","Korè","Japon","Vyetnam"],"opts_fr":["Chine","Corée","Japon","Vietnam"],"opts_en":["China","Korea","Japan","Vietnam"],"ans":2},
      {"q_ht":"Ki lanmè ki pi gran nan mond lan?","q_fr":"Quelle est la plus grande mer du monde?","q_en":"What is the largest sea in the world?","opts_ht":["Mediterane","Karayib","Arawbi","Filippinen"],"opts_fr":["Méditerranée","Caraïbes","Arabie","Philippines"],"opts_en":["Mediterranean","Caribbean","Arabian","Philippine"],"ans":3},
    ],
    "medium": [
      {"q_ht":"Ki kapital peyi Ostri?","q_fr":"Quelle est la capitale de l'Autriche?","q_en":"What is the capital of Austria?","opts_ht":["Viyen","Bèlin","Zirik","Praj"],"opts_fr":["Vienne","Berlin","Zurich","Prague"],"opts_en":["Vienna","Berlin","Zurich","Prague"],"ans":0},
      {"q_ht":"Ki dlo ki pi fon nan mond lan?","q_fr":"Quel est le lac le plus profond du monde?","q_en":"What is the deepest lake in the world?","opts_ht":["Titikas","Baikal","Kaspyen","Superyè"],"opts_fr":["Titicaca","Baïkal","Caspienne","Supérieur"],"opts_en":["Titicaca","Baikal","Caspian","Superior"],"ans":1},
      {"q_ht":"Ki peyi ki gen pi gwo sifas nan Afrik?","q_fr":"Quel pays a la plus grande superficie en Afrique?","q_en":"Which country has the largest area in Africa?","opts_ht":["Niyeryèl","Aljeri","Kongo","Soudi"],"opts_fr":["Nigéria","Algérie","Congo","Arabie Saoudite"],"opts_en":["Nigeria","Algeria","Congo","Saudi Arabia"],"ans":1},
      {"q_ht":"Ki rivyè ki pi long nan Ewòp?","q_fr":"Quel est le plus long fleuve d'Europe?","q_en":"What is the longest river in Europe?","opts_ht":["Ren","Danib","Volga","Tèmz"],"opts_fr":["Rhin","Danube","Volga","Tamise"],"opts_en":["Rhine","Danube","Volga","Thames"],"ans":2},
      {"q_ht":"Ki kapital peyi Nouyèl Zeland?","q_fr":"Quelle est la capitale de la Nouvelle-Zélande?","q_en":"What is the capital of New Zealand?","opts_ht":["Auckland","Wellington","Christchurch","Dunedin"],"opts_fr":["Auckland","Wellington","Christchurch","Dunedin"],"opts_en":["Auckland","Wellington","Christchurch","Dunedin"],"ans":1},
      {"q_ht":"Ki peyi ki bay sou Marediteranel ak Atlantik?","q_fr":"Quel pays borde à la fois la Méditerranée et l'Atlantique?","q_en":"Which country borders both the Mediterranean and Atlantic?","opts_ht":["Pòtigal","Maroc","Lèspay","Itali"],"opts_fr":["Portugal","Maroc","Espagne","Italie"],"opts_en":["Portugal","Morocco","Spain","Italy"],"ans":2},
      {"q_ht":"Ki kapital peyi Ejip?","q_fr":"Quelle est la capitale de l'Égypte?","q_en":"What is the capital of Egypt?","opts_ht":["Aleksandri","Kayo","Luxor","Aswan"],"opts_fr":["Alexandrie","Le Caire","Louxor","Assouan"],"opts_en":["Alexandria","Cairo","Luxor","Aswan"],"ans":1},
      {"q_ht":"Ki mòn ki separe Ewòp ak Azì nan Risi?","q_fr":"Quelle chaîne de montagnes sépare l'Europe de l'Asie en Russie?","q_en":"Which mountain range separates Europe from Asia in Russia?","opts_ht":["Koka","Alp","Ouralz","Karpat"],"opts_fr":["Caucase","Alpes","Oural","Carpates"],"opts_en":["Caucasus","Alps","Urals","Carpathians"],"ans":2},
      {"q_ht":"Ki peyi ki gen pi plis abitant nan Afrik?","q_fr":"Quel pays africain a le plus d'habitants?","q_en":"Which African country has the most inhabitants?","opts_ht":["Ejipt","Etiyopi","Niyeryèl","Afrik di Sid"],"opts_fr":["Égypte","Éthiopie","Nigéria","Afrique du Sud"],"opts_en":["Egypt","Ethiopia","Nigeria","South Africa"],"ans":2},
      {"q_ht":"Ki kapital peyi Kanadà?","q_fr":"Quelle est la capitale du Canada?","q_en":"What is the capital of Canada?","opts_ht":["Toronto","Montreal","Ottawa","Vancouver"],"opts_fr":["Toronto","Montréal","Ottawa","Vancouver"],"opts_en":["Toronto","Montreal","Ottawa","Vancouver"],"ans":2},
      {"q_ht":"Ki dlo ki pi gran nan mond lan pa sifas?","q_fr":"Quel est le plus grand lac du monde par superficie?","q_en":"What is the largest lake in the world by surface area?","opts_ht":["Superyè","Baikal","Kaspyen","Michigan"],"opts_fr":["Supérieur","Baïkal","Caspienne","Michigan"],"opts_en":["Superior","Baikal","Caspian","Michigan"],"ans":2},
      {"q_ht":"Ki kapital peyi Indonezi?","q_fr":"Quelle est la capitale de l'Indonésie?","q_en":"What is the capital of Indonesia?","opts_ht":["Surabaya","Bandung","Jakarta","Medan"],"opts_fr":["Surabaya","Bandung","Jakarta","Medan"],"opts_en":["Surabaya","Bandung","Jakarta","Medan"],"ans":2},
      {"q_ht":"Ki peyi ki gen pi plis zile?","q_fr":"Quel pays possède le plus d'îles?","q_en":"Which country has the most islands?","opts_ht":["Filpin","Indonezi","Kanada","Swèd"],"opts_fr":["Philippines","Indonésie","Canada","Suède"],"opts_en":["Philippines","Indonesia","Canada","Sweden"],"ans":3},
      {"q_ht":"Ki mòn ki nan Amerik di Sid ki pi wo?","q_fr":"Quelle est la plus haute montagne d'Amérique du Sud?","q_en":"What is the highest mountain in South America?","opts_ht":["Chimborazo","Cotopaxi","Aconcagua","Huascarán"],"opts_fr":["Chimborazo","Cotopaxi","Aconcagua","Huascarán"],"opts_en":["Chimborazo","Cotopaxi","Aconcagua","Huascarán"],"ans":2},
      {"q_ht":"Ki kapital peyi Pòtigal?","q_fr":"Quelle est la capitale du Portugal?","q_en":"What is the capital of Portugal?","opts_ht":["Porto","Lisbonn","Faro","Braga"],"opts_fr":["Porto","Lisbonne","Faro","Braga"],"opts_en":["Porto","Lisbon","Faro","Braga"],"ans":1},
      {"q_ht":"Ki peyi ki pi pre Ayiti?","q_fr":"Quel pays est le plus proche d'Haïti?","q_en":"Which country is closest to Haiti?","opts_ht":["Kiba","Repiblik Dominikèn","Jamayik","Porto Riko"],"opts_fr":["Cuba","République Dominicaine","Jamaïque","Porto Rico"],"opts_en":["Cuba","Dominican Republic","Jamaica","Puerto Rico"],"ans":1},
      {"q_ht":"Ki kapital peyi Pèrou?","q_fr":"Quelle est la capitale du Pérou?","q_en":"What is the capital of Peru?","opts_ht":["Cusco","Arequipa","Lima","Trujillo"],"opts_fr":["Cusco","Arequipa","Lima","Trujillo"],"opts_en":["Cusco","Arequipa","Lima","Trujillo"],"ans":2},
      {"q_ht":"Ki peyi ki pi gran nan Ewòp?","q_fr":"Quel est le plus grand pays d'Europe?","q_en":"What is the largest country in Europe?","opts_ht":["Frannce","Almay","Ris","Ikrèn"],"opts_fr":["France","Allemagne","Russie","Ukraine"],"opts_en":["France","Germany","Russia","Ukraine"],"ans":2},
      {"q_ht":"Ki kapital peyi Venezyela?","q_fr":"Quelle est la capitale du Venezuela?","q_en":"What is the capital of Venezuela?","opts_ht":["Maracaibo","Valencia","Caracas","Barquisimeto"],"opts_fr":["Maracaibo","Valencia","Caracas","Barquisimeto"],"opts_en":["Maracaibo","Valencia","Caracas","Barquisimeto"],"ans":2},
      {"q_ht":"Ki pwen ki pi ba nan mond lan?","q_fr":"Quel est le point le plus bas du monde?","q_en":"What is the lowest point on Earth?","opts_ht":["Lanmè Mò","Lanmè Kaspi","Lac Assal","Lanmè Rouj"],"opts_fr":["Mer Morte","Mer Caspienne","Lac Assal","Mer Rouge"],"opts_en":["Dead Sea","Caspian Sea","Lake Assal","Red Sea"],"ans":0},
    ],
    "hard": [
      {"q_ht":"Ki kapital peyi Kazikastan?","q_fr":"Quelle est la capitale du Kazakhstan?","q_en":"What is the capital of Kazakhstan?","opts_ht":["Almaati","Astana","Bishkek","Tashkent"],"opts_fr":["Almaty","Astana","Bichkek","Tachkent"],"opts_en":["Almaty","Astana","Bishkek","Tashkent"],"ans":1},
      {"q_ht":"Ki kapital peyi Bhutan?","q_fr":"Quelle est la capitale du Bhoutan?","q_en":"What is the capital of Bhutan?","opts_ht":["Thimphou","Kathmandou","Dhaka","Colombo"],"opts_fr":["Thimphou","Katmandou","Dacca","Colombo"],"opts_en":["Thimphu","Kathmandu","Dhaka","Colombo"],"ans":0},
      {"q_ht":"Ki peyi ki gen pi piti sifas nan Azì?","q_fr":"Quel pays d'Asie a la plus petite superficie?","q_en":"Which Asian country has the smallest area?","opts_ht":["Singapou","Maldiv","Bahrèn","Brounèy"],"opts_fr":["Singapour","Maldives","Bahreïn","Brunei"],"opts_en":["Singapore","Maldives","Bahrain","Brunei"],"ans":1},
      {"q_ht":"Ki peyi ki rele 'Toît du Monde'?","q_fr":"Quel pays est surnommé 'Toit du Monde'?","q_en":"Which country is nicknamed 'Roof of the World'?","opts_ht":["Nepal","Tibet","Bhutan","Afganistan"],"opts_fr":["Népal","Tibet","Bhoutan","Afghanistan"],"opts_en":["Nepal","Tibet","Bhutan","Afghanistan"],"ans":1},
      {"q_ht":"Ki kapital peyi Mongoli?","q_fr":"Quelle est la capitale de la Mongolie?","q_en":"What is the capital of Mongolia?","opts_ht":["Ulan Bator","Darkhan","Erdenet","Choibalsan"],"opts_fr":["Oulan-Bator","Darkhan","Erdenet","Tchoïbalsan"],"opts_en":["Ulaanbaatar","Darkhan","Erdenet","Choibalsan"],"ans":0},
      {"q_ht":"Ki tèt dlo ki pi wo nan mond lan?","q_fr":"Quelle est la chute d'eau la plus haute du monde?","q_en":"What is the highest waterfall in the world?","opts_ht":["Niagara","Victoria","Angel","Iguazu"],"opts_fr":["Niagara","Victoria","Angel","Iguazu"],"opts_en":["Niagara","Victoria","Angel","Iguazu"],"ans":2},
      {"q_ht":"Ki peyi ki gen pi plis fwontyè nan Ewòp?","q_fr":"Quel pays européen a le plus de frontières?","q_en":"Which European country has the most borders?","opts_ht":["Frannce","Almay","Ris","Otrich"],"opts_fr":["France","Allemagne","Russie","Autriche"],"opts_en":["France","Germany","Russia","Austria"],"ans":1},
      {"q_ht":"Ki kapital peyi Tanzani?","q_fr":"Quelle est la capitale de la Tanzanie?","q_en":"What is the capital of Tanzania?","opts_ht":["Dar es Salam","Dodoma","Zanzibar","Mwanza"],"opts_fr":["Dar es Salam","Dodoma","Zanzibar","Mwanza"],"opts_en":["Dar es Salaam","Dodoma","Zanzibar","Mwanza"],"ans":1},
      {"q_ht":"Ki peyi ki gen pi plis lang ofisyèl?","q_fr":"Quel pays a le plus de langues officielles?","q_en":"Which country has the most official languages?","opts_ht":["Swis","Belj","Afrik di Sid","Bòliyi"],"opts_fr":["Suisse","Belgique","Afrique du Sud","Bolivie"],"opts_en":["Switzerland","Belgium","South Africa","Bolivia"],"ans":2},
      {"q_ht":"Ki kapital peyi Eritre?","q_fr":"Quelle est la capitale de l'Érythrée?","q_en":"What is the capital of Eritrea?","opts_ht":["Massawa","Asmara","Keren","Assab"],"opts_fr":["Massawa","Asmara","Keren","Assab"],"opts_en":["Massawa","Asmara","Keren","Assab"],"ans":1},
      {"q_ht":"Ki peyi ki sou de kontinan?","q_fr":"Quel pays se trouve sur deux continents?","q_en":"Which country spans two continents?","opts_ht":["Ris","Tiki","Ejip","Kazakstan"],"opts_fr":["Russie","Turquie","Égypte","Kazakhstan"],"opts_en":["Russia","Turkey","Egypt","Kazakhstan"],"ans":1},
      {"q_ht":"Ki lanmè ki antoure Islann?","q_fr":"Quelle mer entoure l'Islande?","q_en":"What sea surrounds Iceland?","opts_ht":["Atlantik Nò","Arktik","Nò","Baltik"],"opts_fr":["Atlantique Nord","Arctique","du Nord","Baltique"],"opts_en":["North Atlantic","Arctic","North Sea","Baltic"],"ans":0},
      {"q_ht":"Ki peyi ki rele 'Peyi Mil Kolin'?","q_fr":"Quel pays est surnommé 'Pays des Mille Collines'?","q_en":"Which country is called 'Land of a Thousand Hills'?","opts_ht":["Burundi","Uganda","Rwanada","Tanzani"],"opts_fr":["Burundi","Ouganda","Rwanda","Tanzanie"],"opts_en":["Burundi","Uganda","Rwanda","Tanzania"],"ans":2},
      {"q_ht":"Ki peyi ki pi piti nan mond lan?","q_fr":"Quel est le plus petit pays du monde?","q_en":"What is the smallest country in the world?","opts_ht":["Monaco","San Marino","Vatikan","Lichtenstein"],"opts_fr":["Monaco","Saint-Marin","Vatican","Liechtenstein"],"opts_en":["Monaco","San Marino","Vatican","Liechtenstein"],"ans":2},
      {"q_ht":"Ki oseyan ki antoure Antarktik?","q_fr":"Quel océan entoure l'Antarctique?","q_en":"Which ocean surrounds Antarctica?","opts_ht":["Pasifik","Atlantik","Sid","Endyen"],"opts_fr":["Pacifique","Atlantique","Austral","Indien"],"opts_en":["Pacific","Atlantic","Southern","Indian"],"ans":2},
      {"q_ht":"Ki peyi ki gen pi gwo lakou nan mond lan?","q_fr":"Quel pays possède la plus grande forêt du monde?","q_en":"Which country has the world's largest forest?","opts_ht":["Brezil","Kanada","Ris","Zaire"],"opts_fr":["Brésil","Canada","Russie","Zaïre"],"opts_en":["Brazil","Canada","Russia","Zaire"],"ans":2},
      {"q_ht":"Ki kapital peyi Fiji?","q_fr":"Quelle est la capitale des Fidji?","q_en":"What is the capital of Fiji?","opts_ht":["Nadi","Lautoka","Suva","Labasa"],"opts_fr":["Nadi","Lautoka","Suva","Labasa"],"opts_en":["Nadi","Lautoka","Suva","Labasa"],"ans":2},
      {"q_ht":"Ki peyi ki gen pi plis volkan aktif?","q_fr":"Quel pays possède le plus de volcans actifs?","q_en":"Which country has the most active volcanoes?","opts_ht":["Japon","Indonezi","Islann","Etazini"],"opts_fr":["Japon","Indonésie","Islande","États-Unis"],"opts_en":["Japan","Indonesia","Iceland","USA"],"ans":1},
      {"q_ht":"Ki pwen ki pi ba nan Afrik?","q_fr":"Quel est le point le plus bas d'Afrique?","q_en":"What is the lowest point in Africa?","opts_ht":["Lac Assal","Lanmè Mò","Lac Turkana","Lac Chad"],"opts_fr":["Lac Assal","Mer Morte","Lac Turkana","Lac Tchad"],"opts_en":["Lake Assal","Dead Sea","Lake Turkana","Lake Chad"],"ans":0},
      {"q_ht":"Ki kapital peyi Maldiv?","q_fr":"Quelle est la capitale des Maldives?","q_en":"What is the capital of the Maldives?","opts_ht":["Male","Addu","Hulhumale","Fuvahmulah"],"opts_fr":["Malé","Addu","Hulhumalé","Fuvahmulah"],"opts_en":["Male","Addu","Hulhumale","Fuvahmulah"],"ans":0},
    ],
  },
  "haiti": {
    "easy": [
      {"q_ht":"Ki ane batay Bwa Kayiman an te fèt?","q_fr":"En quelle année s'est déroulée la cérémonie du Bois Caïman?","q_en":"In what year did the Bois Caïman ceremony take place?","opts_ht":["1789","1791","1793","1795"],"opts_fr":["1789","1791","1793","1795"],"opts_en":["1789","1791","1793","1795"],"ans":1},
      {"q_ht":"Ki kapital Ayiti?","q_fr":"Quelle est la capitale d'Haïti?","q_en":"What is the capital of Haiti?","opts_ht":["Kap-Ayisyen","Pòtoprens","Jakmel","Okay"],"opts_fr":["Cap-Haïtien","Port-au-Prince","Jacmel","Cayes"],"opts_en":["Cap-Haitian","Port-au-Prince","Jacmel","Les Cayes"],"ans":1},
      {"q_ht":"Ki lang ofisyèl Ayiti yo?","q_fr":"Quelles sont les langues officielles d'Haïti?","q_en":"What are the official languages of Haiti?","opts_ht":["Kreyòl sèlman","Fransè sèlman","Kreyòl ak Fransè","Anglè ak Fransè"],"opts_fr":["Créole seulement","Français seulement","Créole et Français","Anglais et Français"],"opts_en":["Creole only","French only","Creole and French","English and French"],"ans":2},
      {"q_ht":"Ki moun ki premye prezidan Ayiti?","q_fr":"Qui fut le premier président d'Haïti?","q_en":"Who was the first president of Haiti?","opts_ht":["Dessalines","Toussaint","Christophe","Pétion"],"opts_fr":["Dessalines","Toussaint","Christophe","Pétion"],"opts_en":["Dessalines","Toussaint","Christophe","Pétion"],"ans":0},
      {"q_ht":"Ki koulè drapo Ayiti a?","q_fr":"Quelles sont les couleurs du drapeau haïtien?","q_en":"What are the colors of the Haitian flag?","opts_ht":["Wouj, ble, blan","Ble ak wouj","Nwa ak wouj","Vèt ak wouj"],"opts_fr":["Rouge, bleu, blanc","Bleu et rouge","Noir et rouge","Vert et rouge"],"opts_en":["Red, blue, white","Blue and red","Black and red","Green and red"],"ans":1},
      {"q_ht":"Ki ane Ayiti te deklare endepandans li?","q_fr":"En quelle année Haïti a-t-elle déclaré son indépendance?","q_en":"In what year did Haiti declare independence?","opts_ht":["1789","1804","1810","1820"],"opts_fr":["1789","1804","1810","1820"],"opts_en":["1789","1804","1810","1820"],"ans":1},
      {"q_ht":"Ki densite peyi Ayiti a?","q_fr":"Quelle est la superficie d'Haïti?","q_en":"What is the area of Haiti?","opts_ht":["17 500 km²","27 750 km²","35 000 km²","42 000 km²"],"opts_fr":["17 500 km²","27 750 km²","35 000 km²","42 000 km²"],"opts_en":["17,500 km²","27,750 km²","35,000 km²","42,000 km²"],"ans":1},
      {"q_ht":"Ki mòn ki pi wo nan Ayiti?","q_fr":"Quelle est la plus haute montagne d'Haïti?","q_en":"What is the highest mountain in Haiti?","opts_ht":["Mòn Nwa","Pic la Selle","Mòn Kabrit","Mòn Pèlerin"],"opts_fr":["Morne Noire","Pic la Selle","Morne Cabrit","Morne Pèlerin"],"opts_en":["Morne Noire","Pic la Selle","Morne Cabrit","Morne Pèlerin"],"ans":1},
      {"q_ht":"Ki lak ki pi gran nan Ayiti?","q_fr":"Quel est le plus grand lac d'Haïti?","q_en":"What is the largest lake in Haiti?","opts_ht":["Lag Azuèy","Lag Pèligre","Etang Saumâtre","Lag Miragwàn"],"opts_fr":["Étang de l'Est","Lac Péligre","Étang Saumâtre","Étang de Miragoâne"],"opts_en":["Eastern Lagoon","Péligre Lake","Saumatre Lake","Miragoâne Lake"],"ans":2},
      {"q_ht":"Ki plenn ki pi gran nan Ayiti?","q_fr":"Quelle est la plus grande plaine d'Haïti?","q_en":"What is the largest plain in Haiti?","opts_ht":["Plèn di Nò","Plèn Latibonit","Plèn Kil de Sak","Plèn Okay"],"opts_fr":["Plaine du Nord","Plaine de l'Artibonite","Cul-de-Sac","Plaine des Cayes"],"opts_en":["Northern Plain","Artibonite Plain","Cul-de-Sac Plain","Les Cayes Plain"],"ans":1},
      {"q_ht":"Ki peyi Ayiti pataje zile Ispanyola a avèk li?","q_fr":"Quel pays partage l'île d'Hispaniola avec Haïti?","q_en":"Which country shares the island of Hispaniola with Haiti?","opts_ht":["Kiba","Jamayik","Repiblik Dominikèn","Porto Riko"],"opts_fr":["Cuba","Jamaïque","République Dominicaine","Porto Rico"],"opts_en":["Cuba","Jamaica","Dominican Republic","Puerto Rico"],"ans":2},
      {"q_ht":"Ki rivyè ki pi long nan Ayiti?","q_fr":"Quel est le fleuve le plus long d'Haïti?","q_en":"What is the longest river in Haiti?","opts_ht":["Rivyè Pèdènales","Rivyè Artibonit","Rivyè Grise","Rivyè Blanche"],"opts_fr":["Rivière Pédernales","Rivière Artibonite","Rivière Grise","Rivière Blanche"],"opts_en":["Pedernales River","Artibonite River","Grise River","Blanche River"],"ans":1},
      {"q_ht":"Ki moun ki te kondui revolisyon Ayisyen an?","q_fr":"Qui a conduit la révolution haïtienne?","q_en":"Who led the Haitian Revolution?","opts_ht":["Pétion","Toussaint Louverture","Dessalines","Christophe"],"opts_fr":["Pétion","Toussaint Louverture","Dessalines","Christophe"],"opts_en":["Pétion","Toussaint Louverture","Dessalines","Christophe"],"ans":1},
      {"q_ht":"Ki dat endepandans Ayiti a?","q_fr":"Quelle est la date d'indépendance d'Haïti?","q_en":"What is Haiti's independence date?","opts_ht":["1ye janvye 1804","4 fevriye 1804","18 novanm 1803","12 oktòb 1804"],"opts_fr":["1er janvier 1804","4 février 1804","18 novembre 1803","12 octobre 1804"],"opts_en":["January 1, 1804","February 4, 1804","November 18, 1803","October 12, 1804"],"ans":0},
      {"q_ht":"Ki depatman Ayiti ki pi gran?","q_fr":"Quel est le plus grand département d'Haïti?","q_en":"What is the largest department of Haiti?","opts_ht":["Nò","Sid","Latibonit","Santral"],"opts_fr":["Nord","Sud","Artibonite","Centre"],"opts_en":["North","South","Artibonite","Center"],"ans":2},
      {"q_ht":"Konbyen depatman Ayiti genyen?","q_fr":"Combien de départements possède Haïti?","q_en":"How many departments does Haiti have?","opts_ht":["8","9","10","11"],"opts_fr":["8","9","10","11"],"opts_en":["8","9","10","11"],"ans":2},
      {"q_ht":"Ki moun ki te pent drapo Ayiti a?","q_fr":"Qui a cousu le drapeau haïtien?","q_en":"Who sewed the Haitian flag?","opts_ht":["Marie-Claire Heureuse","Catherine Flon","Sanite Bélair","Victoria Montou"],"opts_fr":["Marie-Claire Heureuse","Catherine Flon","Sanite Bélair","Victoria Montou"],"opts_en":["Marie-Claire Heureuse","Catherine Flon","Sanite Bélair","Victoria Montou"],"ans":1},
      {"q_ht":"Ki vil ki dezyèm pi gran nan Ayiti?","q_fr":"Quelle est la deuxième plus grande ville d'Haïti?","q_en":"What is the second largest city in Haiti?","opts_ht":["Jakmel","Okay","Kap-Ayisyen","Gonayiv"],"opts_fr":["Jacmel","Cayes","Cap-Haïtien","Gonaïves"],"opts_en":["Jacmel","Les Cayes","Cap-Haitian","Gonaives"],"ans":2},
      {"q_ht":"Ki dat drapo Ayiti a?","q_fr":"Quelle est la date du drapeau haïtien?","q_en":"What is Haiti's flag day?","opts_ht":["14 me","18 me","22 me","28 me"],"opts_fr":["14 mai","18 mai","22 mai","28 mai"],"opts_en":["May 14","May 18","May 22","May 28"],"ans":1},
      {"q_ht":"Ki premye repiblik nwa lib nan istwa?","q_fr":"Quelle fut la première république noire libre de l'histoire?","q_en":"Which was the first free Black republic in history?","opts_ht":["Liberya","Ayiti","Etiyopi","Jamayik"],"opts_fr":["Libéria","Haïti","Éthiopie","Jamaïque"],"opts_en":["Liberia","Haiti","Ethiopia","Jamaica"],"ans":1},
    ],
    "medium": [
      {"q_ht":"Ki moun ki kondui seremoni Bwa Kayiman an?","q_fr":"Qui a conduit la cérémonie du Bois Caïman?","q_en":"Who led the Bois Caïman ceremony?","opts_ht":["Boukman","Toussaint","Biassou","Jean-François"],"opts_fr":["Boukman","Toussaint","Biassou","Jean-François"],"opts_en":["Boukman","Toussaint","Biassou","Jean-François"],"ans":0},
      {"q_ht":"Ki batay ki deside endepandans Ayiti?","q_fr":"Quelle bataille a décidé de l'indépendance d'Haïti?","q_en":"Which battle decided Haiti's independence?","opts_ht":["Batay Vetiyè","Batay Ravin-a-Couleuvre","Batay Lakrèt-a-Pierrot","Batay Bwa Kayiman"],"opts_fr":["Bataille de Vertières","Bataille Ravine-à-Couleuvre","Bataille de la Crête-à-Pierrot","Cérémonie du Bois Caïman"],"opts_en":["Battle of Vertières","Battle of Ravine-à-Couleuvre","Battle of Crête-à-Pierrot","Battle of Bois Caïman"],"ans":0},
      {"q_ht":"Ki ane tranblemantè 2010 la te fèt?","q_fr":"Quelle était la date du séisme de 2010 en Haïti?","q_en":"What was the date of the 2010 Haiti earthquake?","opts_ht":["12 janvye 2010","10 janvye 2010","15 janvye 2010","20 janvye 2010"],"opts_fr":["12 janvier 2010","10 janvier 2010","15 janvier 2010","20 janvier 2010"],"opts_en":["January 12, 2010","January 10, 2010","January 15, 2010","January 20, 2010"],"ans":0},
      {"q_ht":"Ki moun ki ekri 'Gouverneurs de la Rosée'?","q_fr":"Qui a écrit 'Gouverneurs de la Rosée'?","q_en":"Who wrote 'Masters of the Dew'?","opts_ht":["Duraciné Vaval","Jacques Roumain","Jean Price-Mars","Oswald Durand"],"opts_fr":["Duraciné Vaval","Jacques Roumain","Jean Price-Mars","Oswald Durand"],"opts_en":["Duraciné Vaval","Jacques Roumain","Jean Price-Mars","Oswald Durand"],"ans":1},
      {"q_ht":"Ki ane konstitisyon 1987 la te vote?","q_fr":"En quelle date la constitution de 1987 a-t-elle été votée?","q_en":"When was the 1987 Haitian constitution voted on?","opts_ht":["29 mas 1987","29 fevriye 1987","10 janvye 1987","18 septanm 1987"],"opts_fr":["29 mars 1987","29 février 1987","10 janvier 1987","18 septembre 1987"],"opts_en":["March 29, 1987","February 29, 1987","January 10, 1987","September 18, 1987"],"ans":0},
      {"q_ht":"Ki okipasyon ki te kòmanse 1915 an Ayiti?","q_fr":"Quelle occupation a débuté en 1915 en Haïti?","q_en":"What occupation began in Haiti in 1915?","opts_ht":["Frannce","Angletè","Etazini","Lèspay"],"opts_fr":["France","Angleterre","États-Unis","Espagne"],"opts_en":["France","England","United States","Spain"],"ans":2},
      {"q_ht":"Ki prezidan ki te kreye lame Dayiti a?","q_fr":"Quel président a créé l'armée d'Haïti?","q_en":"Which president created the Haitian army?","opts_ht":["Pétion","Dessalines","Christophe","Toussaint"],"opts_fr":["Pétion","Dessalines","Christophe","Toussaint"],"opts_en":["Pétion","Dessalines","Christophe","Toussaint"],"ans":1},
      {"q_ht":"Ki moun ki te ekri 'Ainsi parla l'Oncle'?","q_fr":"Qui a écrit 'Ainsi parla l'Oncle'?","q_en":"Who wrote 'So Spoke the Uncle'?","opts_ht":["Jacques Roumain","Oswald Durand","Jean Price-Mars","Dantès Bellegarde"],"opts_fr":["Jacques Roumain","Oswald Durand","Jean Price-Mars","Dantès Bellegarde"],"opts_en":["Jacques Roumain","Oswald Durand","Jean Price-Mars","Dantès Bellegarde"],"ans":2},
      {"q_ht":"Ki fòteres istorik ki nan Nò Ayiti?","q_fr":"Quelle forteresse historique se trouve dans le Nord d'Haïti?","q_en":"Which historic fortress is in Northern Haiti?","opts_ht":["Fò Jakmel","Fò Liberté","Sitadèl Laferyè","Fò Dimanche"],"opts_fr":["Fort Jacmel","Fort Liberté","Citadelle Laferrière","Fort Dimanche"],"opts_en":["Fort Jacmel","Fort Liberté","Citadelle Laferrière","Fort Dimanche"],"ans":2},
      {"q_ht":"Ki ane Ayiti te rejwenn OEA?","q_fr":"En quelle année Haïti a-t-elle rejoint l'OEA?","q_en":"In what year did Haiti join the OAS?","opts_ht":["1948","1950","1951","1955"],"opts_fr":["1948","1950","1951","1955"],"opts_en":["1948","1950","1951","1955"],"ans":0},
      {"q_ht":"Ki grann rivyè ki travèse Pòtoprens?","q_fr":"Quel grand cours d'eau traverse Port-au-Prince?","q_en":"Which major river runs through Port-au-Prince?","opts_ht":["Rivyè Artibonit","Rivyè Grise","Rivyè Blanche","Rivyè Péligre"],"opts_fr":["Rivière Artibonite","Rivière Grise","Rivière Blanche","Rivière Péligre"],"opts_en":["Artibonite River","Grise River","Blanche River","Péligre River"],"ans":1},
      {"q_ht":"Ki palè prezidansyèl Ayiti ki detwi nan 2010?","q_fr":"Quel palais présidentiel haïtien a été détruit en 2010?","q_en":"Which Haitian presidential palace was destroyed in 2010?","opts_ht":["Palè San Souci","Palè Nasyonal","Palè Lakay","Palè Labastille"],"opts_fr":["Palais Sans Souci","Palais National","Palais Lakay","Palais Labastille"],"opts_en":["Sans Souci Palace","National Palace","Lakay Palace","Labastille Palace"],"ans":1},
      {"q_ht":"Ki moun ki te fonde vil Jakmel?","q_fr":"Qui a fondé la ville de Jacmel?","q_en":"Who founded the city of Jacmel?","opts_ht":["Christophe","Pétion","Dessalines","de Graff"],"opts_fr":["Christophe","Pétion","Dessalines","de Graff"],"opts_en":["Christophe","Pétion","Dessalines","de Graff"],"ans":3},
      {"q_ht":"Ki ane Ayiti te vin manm ONU?","q_fr":"En quelle année Haïti est-elle devenue membre de l'ONU?","q_en":"In what year did Haiti become a UN member?","opts_ht":["1943","1945","1947","1950"],"opts_fr":["1943","1945","1947","1950"],"opts_en":["1943","1945","1947","1950"],"ans":1},
      {"q_ht":"Ki moun ki te kreye drapo Ayiti a ofisyèlman?","q_fr":"Qui a officiellement créé le drapeau haïtien?","q_en":"Who officially created the Haitian flag?","opts_ht":["Dessalines","Pétion","Christophe","Toussaint"],"opts_fr":["Dessalines","Pétion","Christophe","Toussaint"],"opts_en":["Dessalines","Pétion","Christophe","Toussaint"],"ans":0},
      {"q_ht":"Ki moun ki ekri pwèm 'Choucoune'?","q_fr":"Qui a écrit le poème 'Choucoune'?","q_en":"Who wrote the poem 'Choucoune'?","opts_ht":["Jacques Roumain","Oswald Durand","Damoclès Vieux","Tertulien Guilbaud"],"opts_fr":["Jacques Roumain","Oswald Durand","Damoclès Vieux","Tertulien Guilbaud"],"opts_en":["Jacques Roumain","Oswald Durand","Damoclès Vieux","Tertulien Guilbaud"],"ans":1},
      {"q_ht":"Ki epòk peryòd kolonyal Ayiti a te rele?","q_fr":"Comment s'appelait Haïti à l'époque coloniale?","q_en":"What was Haiti called during the colonial period?","opts_ht":["Kiba","Ispanyola","Sen Domeng","Lakayiti"],"opts_fr":["Cuba","Hispaniola","Saint-Domingue","Haïti"],"opts_en":["Cuba","Hispaniola","Saint-Domingue","Hayti"],"ans":2},
      {"q_ht":"Ki moun ki te kreye Repiblik Nò a nan Ayiti?","q_fr":"Qui a créé la République du Nord en Haïti?","q_en":"Who created the Kingdom of Northern Haiti?","opts_ht":["Pétion","Dessalines","Christophe","Toussaint"],"opts_fr":["Pétion","Dessalines","Christophe","Toussaint"],"opts_en":["Pétion","Dessalines","Christophe","Toussaint"],"ans":2},
      {"q_ht":"Ki moun ki te pran pouvwa apre Dessalines?","q_fr":"Qui a pris le pouvoir après Dessalines?","q_en":"Who took power after Dessalines?","opts_ht":["Pétion sèlman","Christophe sèlman","Pétion ak Christophe divize peyi a","Toussaint"],"opts_fr":["Pétion seulement","Christophe seulement","Pétion et Christophe divisèrent le pays","Toussaint"],"opts_en":["Pétion only","Christophe only","Pétion and Christophe split the country","Toussaint"],"ans":2},
      {"q_ht":"Ki ane Ayiti te peye ranson bay Frannce?","q_fr":"Pendant quelle période Haïti a-t-elle payé sa rançon à la France?","q_en":"During what period did Haiti pay reparations to France?","opts_ht":["1804-1838","1825-1947","1810-1900","1838-1915"],"opts_fr":["1804-1838","1825-1947","1810-1900","1838-1915"],"opts_en":["1804-1838","1825-1947","1810-1900","1838-1915"],"ans":1},
    ],
    "hard": [
      {"q_ht":"Ki gouvènman ki siyen trete Ryswick la?","q_fr":"Quel gouvernement a signé le traité de Ryswick?","q_en":"Which government signed the Treaty of Ryswick?","opts_ht":["Frannce ak Ris","Frannce ak Lèspay","Frannce ak Angletè","Frannce ak Pòtigal"],"opts_fr":["France et Russie","France et Espagne","France et Angleterre","France et Portugal"],"opts_en":["France and Russia","France and Spain","France and England","France and Portugal"],"ans":1},
      {"q_ht":"Ki moun ki te fonde Pòtoprens?","q_fr":"Qui a fondé Port-au-Prince?","q_en":"Who founded Port-au-Prince?","opts_ht":["Dessalines","de Fayet","Pétion","Christophe"],"opts_fr":["Dessalines","de Fayet","Pétion","Christophe"],"opts_en":["Dessalines","de Fayet","Pétion","Christophe"],"ans":1},
      {"q_ht":"Ki ane Ayiti te rekonèt ofisyèlman pa Etazini?","q_fr":"En quelle année les États-Unis ont-ils officiellement reconnu Haïti?","q_en":"In what year did the United States officially recognize Haiti?","opts_ht":["1804","1825","1862","1915"],"opts_fr":["1804","1825","1862","1915"],"opts_en":["1804","1825","1862","1915"],"ans":2},
      {"q_ht":"Ki premye konstitisyon Ayiti a te adopte ki ane?","q_fr":"En quelle année la première constitution d'Haïti a-t-elle été adoptée?","q_en":"In what year was Haiti's first constitution adopted?","opts_ht":["1801","1804","1806","1816"],"opts_fr":["1801","1804","1806","1816"],"opts_en":["1801","1804","1806","1816"],"ans":0},
      {"q_ht":"Ki moun ki te ekri pwèm nasyonal Ayiti a 'La Dessalinienne'?","q_fr":"Qui a composé l'hymne national haïtien 'La Dessalinienne'?","q_en":"Who composed Haiti's national anthem 'La Dessalinienne'?","opts_ht":["Justin Lhérisson","Oswald Durand","Nicolas Geffrard","Cénatus Jeanty"],"opts_fr":["Justin Lhérisson","Oswald Durand","Nicolas Geffrard","Cénatus Jeanty"],"opts_en":["Justin Lhérisson","Oswald Durand","Nicolas Geffrard","Cénatus Jeanty"],"ans":0},
      {"q_ht":"Ki moun ki te mete mizik 'La Dessalinienne' a?","q_fr":"Qui a mis en musique 'La Dessalinienne'?","q_en":"Who set 'La Dessalinienne' to music?","opts_ht":["Justin Lhérisson","Oswald Durand","Nicolas Geffrard","Cénatus Jeanty"],"opts_fr":["Justin Lhérisson","Oswald Durand","Nicolas Geffrard","Cénatus Jeanty"],"opts_en":["Justin Lhérisson","Oswald Durand","Nicolas Geffrard","Cénatus Jeanty"],"ans":3},
      {"q_ht":"Ki moun ki te dirije gouvènman pwovizwa apre tranblemantè 1842 la?","q_fr":"Qui dirigeait le gouvernement provisoire après le séisme de 1842?","q_en":"Who led the provisional government after the 1842 earthquake?","opts_ht":["Boyer","Rivière-Hérard","Guerrier","Soulouque"],"opts_fr":["Boyer","Rivière-Hérard","Guerrier","Soulouque"],"opts_en":["Boyer","Rivière-Hérard","Guerrier","Soulouque"],"ans":1},
      {"q_ht":"Ki premye fanm ki te gouvène Ayiti a?","q_fr":"Quelle fut la première femme à gouverner Haïti?","q_en":"Who was the first woman to govern Haiti?","opts_ht":["Ertha Pascal-Trouillot","Marie-Claire Heureuse","Catherine Flon","Sanite Bélair"],"opts_fr":["Ertha Pascal-Trouillot","Marie-Claire Heureuse","Catherine Flon","Sanite Bélair"],"opts_en":["Ertha Pascal-Trouillot","Marie-Claire Heureuse","Catherine Flon","Sanite Bélair"],"ans":0},
      {"q_ht":"Ki ane Ayiti te achte Lwizyan bay Frannce anvan Etazini?","q_fr":"En quelle année la France a-t-elle vendu la Louisiane aux États-Unis?","q_en":"In what year did France sell Louisiana to the United States?","opts_ht":["1800","1801","1803","1805"],"opts_fr":["1800","1801","1803","1805"],"opts_en":["1800","1801","1803","1805"],"ans":2},
      {"q_ht":"Ki moun ki te fonde mouvman noirisme ann Ayiti?","q_fr":"Qui a fondé le mouvement noiriste en Haïti?","q_en":"Who founded the noirisme movement in Haiti?","opts_ht":["Duvalier","Price-Mars","Estimé","Magloire"],"opts_fr":["Duvalier","Price-Mars","Estimé","Magloire"],"opts_en":["Duvalier","Price-Mars","Estimé","Magloire"],"ans":1},
      {"q_ht":"Ki ane Ayiti te fonde sosyete literary 'Les Amis des Lettres'?","q_fr":"En quelle année la société littéraire 'Les Amis des Lettres' a-t-elle été fondée?","q_en":"In what year was the literary society 'Les Amis des Lettres' founded?","opts_ht":["1836","1840","1845","1852"],"opts_fr":["1836","1840","1845","1852"],"opts_en":["1836","1840","1845","1852"],"ans":0},
      {"q_ht":"Ki moun ki te dirije revolisyon Sen Domeng anvan Toussaint?","q_fr":"Qui dirigeait la révolution de Saint-Domingue avant Toussaint?","q_en":"Who led the Saint-Domingue revolution before Toussaint?","opts_ht":["Boukman","Biassou","Jean-François","Mackandal"],"opts_fr":["Boukman","Biassou","Jean-François","Mackandal"],"opts_en":["Boukman","Biassou","Jean-François","Mackandal"],"ans":0},
      {"q_ht":"Ki ane Ayiti te vin premye peyi nan emisifè lwès ki te abolì esklavaj?","q_fr":"En quelle année Haïti est-elle devenue le premier pays de l'hémisphère occidental à abolir l'esclavage?","q_en":"In what year did Haiti become the first Western Hemisphere country to abolish slavery?","opts_ht":["1793","1801","1804","1807"],"opts_fr":["1793","1801","1804","1807"],"opts_en":["1793","1801","1804","1807"],"ans":2},
      {"q_ht":"Ki moun ki te administre Ayiti pandan okipasyon ameriken an?","q_fr":"Qui administrait Haïti pendant l'occupation américaine?","q_en":"Who administered Haiti during the American occupation?","opts_ht":["Smedley Butler","John Russell","Alexander Williams","Henry Caperton"],"opts_fr":["Smedley Butler","John Russell","Alexander Williams","Henry Caperton"],"opts_en":["Smedley Butler","John Russell","Alexander Williams","Henry Caperton"],"ans":1},
      {"q_ht":"Ki moun ki te ekri 'La Prise de l'Amba-Tcha'?","q_fr":"Qui a écrit 'La Prise de l'Amba-Tcha'?","q_en":"Who wrote 'La Prise de l'Amba-Tcha'?","opts_ht":["Etzer Vilaire","Oswald Durand","Antoine Innocent","Fernand Hibbert"],"opts_fr":["Etzer Vilaire","Oswald Durand","Antoine Innocent","Fernand Hibbert"],"opts_en":["Etzer Vilaire","Oswald Durand","Antoine Innocent","Fernand Hibbert"],"ans":2},
      {"q_ht":"Ki koulè inifòm lame Ayiti a pandan batay Vetiyè?","q_fr":"Quelle était la couleur de l'uniforme de l'armée haïtienne lors de la bataille de Vertières?","q_en":"What color were Haitian army uniforms at the Battle of Vertières?","opts_ht":["Wouj ak nwa","Ble ak blan","Vèt ak jòn","Blan ak nwa"],"opts_fr":["Rouge et noir","Bleu et blanc","Vert et jaune","Blanc et noir"],"opts_en":["Red and black","Blue and white","Green and yellow","White and black"],"ans":0},
      {"q_ht":"Ki moun ki te ekri 'Mémoire sur l'esclavage'?","q_fr":"Qui a écrit 'Mémoire sur l'esclavage'?","q_en":"Who wrote 'Memoir on Slavery'?","opts_ht":["Toussaint Louverture","Jean-Baptiste Belley","Julien Raimond","Vincent Ogé"],"opts_fr":["Toussaint Louverture","Jean-Baptiste Belley","Julien Raimond","Vincent Ogé"],"opts_en":["Toussaint Louverture","Jean-Baptiste Belley","Julien Raimond","Vincent Ogé"],"ans":2},
      {"q_ht":"Ki pwovens ki te premye pwoklame revolisyon 1791 la?","q_fr":"Quelle province a la première proclamé la révolution de 1791?","q_en":"Which province first proclaimed the 1791 revolution?","opts_ht":["Sid","Lwès","Nò","Latibonit"],"opts_fr":["Sud","Ouest","Nord","Artibonite"],"opts_en":["South","West","North","Artibonite"],"ans":2},
      {"q_ht":"Ki moun ki te ede Dessalines epi ki te trayi l apre?","q_fr":"Qui a aidé Dessalines puis l'a trahi?","q_en":"Who helped Dessalines and then betrayed him?","opts_ht":["Christophe","Pétion","Geffrard","Bonnet"],"opts_fr":["Christophe","Pétion","Geffrard","Bonnet"],"opts_en":["Christophe","Pétion","Geffrard","Bonnet"],"ans":1},
      {"q_ht":"Ki premye prezidan Ayiti ki te eli demokratikman?","q_fr":"Quel fut le premier président haïtien élu démocratiquement?","q_en":"Who was the first democratically elected president of Haiti?","opts_ht":["Jean-Bertrand Aristide","Leslie Manigat","Henri Namphy","Prosper Avril"],"opts_fr":["Jean-Bertrand Aristide","Leslie Manigat","Henri Namphy","Prosper Avril"],"opts_en":["Jean-Bertrand Aristide","Leslie Manigat","Henri Namphy","Prosper Avril"],"ans":0},
    ],
  },
  "sci": {
    "easy": [
      {"q_ht":"Ki planèt ki pi pre solèy la?","q_fr":"Quelle planète est la plus proche du Soleil?","q_en":"Which planet is closest to the Sun?","opts_ht":["Venis","Tè","Mas","Mèki"],"opts_fr":["Vénus","Terre","Mars","Mercure"],"opts_en":["Venus","Earth","Mars","Mercury"],"ans":3},
      {"q_ht":"Ki elemant chimik ki gen senbòl 'O'?","q_fr":"Quel élément chimique a le symbole 'O'?","q_en":"Which chemical element has the symbol 'O'?","opts_ht":["Ò","Oksijèn","Osmiyòm","Òganik"],"opts_fr":["Or","Oxygène","Osmium","Organique"],"opts_en":["Gold","Oxygen","Osmium","Organic"],"ans":1},
      {"q_ht":"Ki vitès limyè a nan vid?","q_fr":"Quelle est la vitesse de la lumière dans le vide?","q_en":"What is the speed of light in a vacuum?","opts_ht":["100 000 km/s","300 000 km/s","150 000 km/s","500 000 km/s"],"opts_fr":["100 000 km/s","300 000 km/s","150 000 km/s","500 000 km/s"],"opts_en":["100,000 km/s","300,000 km/s","150,000 km/s","500,000 km/s"],"ans":1},
      {"q_ht":"Konbyen zo ki nan kò yon moun granmoun?","q_fr":"Combien d'os possède un adulte humain?","q_en":"How many bones does an adult human have?","opts_ht":["196","206","216","226"],"opts_fr":["196","206","216","226"],"opts_en":["196","206","216","226"],"ans":1},
      {"q_ht":"Ki gaz ki pi abondan nan atmosfè Tè a?","q_fr":"Quel gaz est le plus abondant dans l'atmosphère terrestre?","q_en":"Which gas is most abundant in Earth's atmosphere?","opts_ht":["Oksijèn","Kabonik","Azòt","Ijidwojèn"],"opts_fr":["Oxygène","Dioxyde de carbone","Azote","Hydrogène"],"opts_en":["Oxygen","Carbon dioxide","Nitrogen","Hydrogen"],"ans":2},
      {"q_ht":"Ki senbòl chimik dlo a?","q_fr":"Quel est le symbole chimique de l'eau?","q_en":"What is the chemical symbol for water?","opts_ht":["HO","H2O","H2O2","OH"],"opts_fr":["HO","H2O","H2O2","OH"],"opts_en":["HO","H2O","H2O2","OH"],"ans":1},
      {"q_ht":"Ki planèt ki gen pwopo annèl?","q_fr":"Quelle planète possède des anneaux célèbres?","q_en":"Which planet has famous rings?","opts_ht":["Jipitè","Inirèn","Satin","Neptin"],"opts_fr":["Jupiter","Uranus","Saturne","Neptune"],"opts_en":["Jupiter","Uranus","Saturn","Neptune"],"ans":2},
      {"q_ht":"Ki ògan ki ponpe san nan kò moun?","q_fr":"Quel organe pompe le sang dans le corps humain?","q_en":"Which organ pumps blood in the human body?","opts_ht":["Poumon","Rèn","Fwa","Kè"],"opts_fr":["Poumon","Rein","Foie","Coeur"],"opts_en":["Lung","Kidney","Liver","Heart"],"ans":3},
      {"q_ht":"Ki metal ki pi lejè?","q_fr":"Quel est le métal le plus léger?","q_en":"What is the lightest metal?","opts_ht":["Aliminyòm","Fè","Litiòm","Titaniyòm"],"opts_fr":["Aluminium","Fer","Lithium","Titane"],"opts_en":["Aluminum","Iron","Lithium","Titanium"],"ans":2},
      {"q_ht":"Ki planèt ki pi gwo nan sistèm solèy la?","q_fr":"Quelle est la plus grande planète du système solaire?","q_en":"What is the largest planet in the solar system?","opts_ht":["Satin","Jipitè","Inirèn","Neptin"],"opts_fr":["Saturne","Jupiter","Uranus","Neptune"],"opts_en":["Saturn","Jupiter","Uranus","Neptune"],"ans":1},
      {"q_ht":"Ki pati kò moun ki pote oksijèn?","q_fr":"Quelle partie du corps humain transporte l'oxygène?","q_en":"Which part of the human body carries oxygen?","opts_ht":["Plakèt","Plasma","Globil wouj","Globil blan"],"opts_fr":["Plaquettes","Plasma","Globules rouges","Globules blancs"],"opts_en":["Platelets","Plasma","Red blood cells","White blood cells"],"ans":2},
      {"q_ht":"Ki senbòl fè a?","q_fr":"Quel est le symbole chimique du fer?","q_en":"What is the chemical symbol for iron?","opts_ht":["Fe","Ir","In","Fr"],"opts_fr":["Fe","Ir","In","Fr"],"opts_en":["Fe","Ir","In","Fr"],"ans":0},
      {"q_ht":"Ki vitamin solèy bay nou?","q_fr":"Quelle vitamine le soleil nous apporte-t-il?","q_en":"Which vitamin does sunlight provide?","opts_ht":["Vitamin A","Vitamin B","Vitamin C","Vitamin D"],"opts_fr":["Vitamine A","Vitamine B","Vitamine C","Vitamine D"],"opts_en":["Vitamin A","Vitamin B","Vitamin C","Vitamin D"],"ans":3},
      {"q_ht":"Konbyen planèt ki nan sistèm solèy la?","q_fr":"Combien de planètes compte le système solaire?","q_en":"How many planets are in the solar system?","opts_ht":["7","8","9","10"],"opts_fr":["7","8","9","10"],"opts_en":["7","8","9","10"],"ans":1},
      {"q_ht":"Ki temperatura dlo bouyi a nan nivo lanmè?","q_fr":"À quelle température l'eau bout-elle au niveau de la mer?","q_en":"At what temperature does water boil at sea level?","opts_ht":["90°C","95°C","100°C","105°C"],"opts_fr":["90°C","95°C","100°C","105°C"],"opts_en":["90°C","95°C","100°C","105°C"],"ans":2},
      {"q_ht":"Ki pati zel ki pote klorofil?","q_fr":"Quelle partie de la plante contient la chlorophylle?","q_en":"Which part of a plant contains chlorophyll?","opts_ht":["Rasin","Tij","Fèy","Flè"],"opts_fr":["Racine","Tige","Feuille","Fleur"],"opts_en":["Root","Stem","Leaf","Flower"],"ans":2},
      {"q_ht":"Ki fòs ki kenbe planèt yo nan òbit?","q_fr":"Quelle force maintient les planètes en orbite?","q_en":"What force keeps planets in orbit?","opts_ht":["Elektrisite","Magnetis","Gravitasyon","Fyèl"],"opts_fr":["Électricité","Magnétisme","Gravitation","Friction"],"opts_en":["Electricity","Magnetism","Gravity","Friction"],"ans":2},
      {"q_ht":"Ki koulè ki gen pi kout longè don nan spektr vizib la?","q_fr":"Quelle couleur a la plus courte longueur d'onde dans le spectre visible?","q_en":"Which color has the shortest wavelength in the visible spectrum?","opts_ht":["Wouj","Jòn","Vèt","Vyolè"],"opts_fr":["Rouge","Jaune","Vert","Violet"],"opts_en":["Red","Yellow","Green","Violet"],"ans":3},
      {"q_ht":"Ki selil ki pa gen nwayo?","q_fr":"Quel type de cellule n'a pas de noyau?","q_en":"Which type of cell has no nucleus?","opts_ht":["Selil vegetal","Selil animal","Globil wouj","Baktèri"],"opts_fr":["Cellule végétale","Cellule animale","Globule rouge","Bactérie"],"opts_en":["Plant cell","Animal cell","Red blood cell","Bacteria"],"ans":2},
      {"q_ht":"Ki fòmil kimik sèl tab la?","q_fr":"Quelle est la formule chimique du sel de table?","q_en":"What is the chemical formula of table salt?","opts_ht":["NaCl","KCl","MgCl2","CaCl2"],"opts_fr":["NaCl","KCl","MgCl2","CaCl2"],"opts_en":["NaCl","KCl","MgCl2","CaCl2"],"ans":0},
    ],
    "medium": [
      {"q_ht":"Ki atom ki pi piti nan tablo peryodik la?","q_fr":"Quel est le plus petit atome du tableau périodique?","q_en":"What is the smallest atom in the periodic table?","opts_ht":["Elyòm","Ijidwojèn","Litiòm","Beryòm"],"opts_fr":["Hélium","Hydrogène","Lithium","Béryllium"],"opts_en":["Helium","Hydrogen","Lithium","Beryllium"],"ans":1},
      {"q_ht":"Ki ògan ki filtre san nan kò moun?","q_fr":"Quel organe filtre le sang dans le corps humain?","q_en":"Which organ filters blood in the human body?","opts_ht":["Poumon","Rèn","Fwa","Kè"],"opts_fr":["Poumon","Rein","Foie","Coeur"],"opts_en":["Lung","Kidney","Liver","Heart"],"ans":1},
      {"q_ht":"Ki siyifikasyon sigle ADN?","q_fr":"Que signifie l'acronyme ADN?","q_en":"What does DNA stand for?","opts_ht":["Asid Deoksyribonukleyik","Asid Nitrik","Azòt Diazòt Nasyonal","Asid Dinukleik"],"opts_fr":["Acide Désoxyribonucléique","Acide Nitrique","Azote Diazote National","Acide Dinucléique"],"opts_en":["Deoxyribonucleic Acid","Nitric Acid","Diazote Nitrogen","Dinucleic Acid"],"ans":0},
      {"q_ht":"Ki teori ki esplike evolisyon espès yo?","q_fr":"Quelle théorie explique l'évolution des espèces?","q_en":"Which theory explains the evolution of species?","opts_ht":["Newton","Darwin","Einstein","Pasteur"],"opts_fr":["Newton","Darwin","Einstein","Pasteur"],"opts_en":["Newton","Darwin","Einstein","Pasteur"],"ans":1},
      {"q_ht":"Ki pati selil la ki pwodui énerji?","q_fr":"Quelle partie de la cellule produit de l'énergie?","q_en":"Which part of the cell produces energy?","opts_ht":["Nwayo","Rilozòm","Mitokondri","Manbràn"],"opts_fr":["Noyau","Ribosome","Mitochondrie","Membrane"],"opts_en":["Nucleus","Ribosome","Mitochondria","Membrane"],"ans":2},
      {"q_ht":"Ki prensip ki di matye pa kreye ni detwi?","q_fr":"Quel principe dit que la matière ne se crée ni ne se détruit?","q_en":"Which principle states that matter is neither created nor destroyed?","opts_ht":["Newton","Lavoisier","Einstein","Boyle"],"opts_fr":["Newton","Lavoisier","Einstein","Boyle"],"opts_en":["Newton","Lavoisier","Einstein","Boyle"],"ans":1},
      {"q_ht":"Ki kalite rayonnman solèy ki ka koze kansè po?","q_fr":"Quel type de rayonnement solaire peut causer le cancer de la peau?","q_en":"What type of solar radiation can cause skin cancer?","opts_ht":["Infrawòj","Vizib","Iltravyolè","Rayòn X"],"opts_fr":["Infrarouge","Visible","Ultraviolet","Rayons X"],"opts_en":["Infrared","Visible","Ultraviolet","X-rays"],"ans":2},
      {"q_ht":"Ki pati nan zye ki kontwole kantite limyè?","q_fr":"Quelle partie de l'œil contrôle la quantité de lumière?","q_en":"Which part of the eye controls the amount of light?","opts_ht":["Rentin","Kòne","Iris","Kristalen"],"opts_fr":["Rétine","Cornée","Iris","Cristallin"],"opts_en":["Retina","Cornea","Iris","Lens"],"ans":2},
      {"q_ht":"Ki nòm pou transfòmasyon likid an gaz?","q_fr":"Quel est le nom du passage d'un liquide à l'état gazeux?","q_en":"What is the name for the transformation of liquid to gas?","opts_ht":["Kondansasyon","Evaporasyon","Solidifikasyon","Sublimation"],"opts_fr":["Condensation","Évaporation","Solidification","Sublimation"],"opts_en":["Condensation","Evaporation","Solidification","Sublimation"],"ans":1},
      {"q_ht":"Ki tip bakt ki ka fè fotossentèz?","q_fr":"Quel type de bactérie peut effectuer la photosynthèse?","q_en":"Which type of bacteria can perform photosynthesis?","opts_ht":["E. coli","Cyanobactèri","Salmonèl","Stapylokok"],"opts_fr":["E. coli","Cyanobactérie","Salmonelle","Staphylocoque"],"opts_en":["E. coli","Cyanobacteria","Salmonella","Staphylococcus"],"ans":1},
      {"q_ht":"Ki fòs ki deplase elektwon nan yon sikwi?","q_fr":"Quelle force déplace les électrons dans un circuit?","q_en":"What force moves electrons in a circuit?","opts_ht":["Magnetis","Tanperati","Tansyon elektrik","Presyon"],"opts_fr":["Magnétisme","Température","Tension électrique","Pression"],"opts_en":["Magnetism","Temperature","Voltage","Pressure"],"ans":2},
      {"q_ht":"Ki pati nan san ki konbat enfeksyon?","q_fr":"Quelle partie du sang combat les infections?","q_en":"Which part of the blood fights infections?","opts_ht":["Plakèt","Globil wouj","Plasma","Globil blan"],"opts_fr":["Plaquettes","Globules rouges","Plasma","Globules blancs"],"opts_en":["Platelets","Red blood cells","Plasma","White blood cells"],"ans":3},
      {"q_ht":"Ki pati nan atòm ki pote chaj negatif?","q_fr":"Quelle partie de l'atome porte une charge négative?","q_en":"Which part of the atom carries a negative charge?","opts_ht":["Pwotòn","Neytwon","Elektwon","Nwayo"],"opts_fr":["Proton","Neutron","Électron","Noyau"],"opts_en":["Proton","Neutron","Electron","Nucleus"],"ans":2},
      {"q_ht":"Ki lwa ki dekri relasyon ant mas ak akselerasyon?","q_fr":"Quelle loi décrit la relation entre masse et accélération?","q_en":"Which law describes the relationship between mass and acceleration?","opts_ht":["Lwa Newton 1","Lwa Newton 2","Lwa Newton 3","Lwa Boyle"],"opts_fr":["Loi de Newton 1","Loi de Newton 2","Loi de Newton 3","Loi de Boyle"],"opts_en":["Newton's 1st Law","Newton's 2nd Law","Newton's 3rd Law","Boyle's Law"],"ans":1},
      {"q_ht":"Ki pati nan zel ki fè fotossentèz?","q_fr":"Quelle partie de la plante réalise la photosynthèse?","q_en":"Which part of the plant performs photosynthesis?","opts_ht":["Kloroplas","Mitokondri","Nwayo","Vakwòl"],"opts_fr":["Chloroplaste","Mitochondrie","Noyau","Vacuole"],"opts_en":["Chloroplast","Mitochondria","Nucleus","Vacuole"],"ans":0},
      {"q_ht":"Ki sou-atòm ki genyen nan nwayo selil la?","q_fr":"Quelles particules se trouvent dans le noyau atomique?","q_en":"Which subatomic particles are found in the atomic nucleus?","opts_ht":["Elektwon sèlman","Pwotòn sèlman","Pwotòn ak neytwon","Elektwon ak pwotòn"],"opts_fr":["Électrons seulement","Protons seulement","Protons et neutrons","Électrons et protons"],"opts_en":["Electrons only","Protons only","Protons and neutrons","Electrons and protons"],"ans":2},
      {"q_ht":"Ki jwenn lè yo melanje asid ak baz?","q_fr":"Qu'obtient-on en mélangeant un acide et une base?","q_en":"What is formed when an acid and base are mixed?","opts_ht":["Oksid","Sèl ak dlo","Gaz","Mineral"],"opts_fr":["Oxyde","Sel et eau","Gaz","Minéral"],"opts_en":["Oxide","Salt and water","Gas","Mineral"],"ans":1},
      {"q_ht":"Ki pati kò moun ki kontwole tout fonksyon li?","q_fr":"Quelle partie du corps humain contrôle toutes ses fonctions?","q_en":"Which part of the human body controls all its functions?","opts_ht":["Kè","Poumon","Sèvo","Fwa"],"opts_fr":["Coeur","Poumon","Cerveau","Foie"],"opts_en":["Heart","Lung","Brain","Liver"],"ans":2},
      {"q_ht":"Ki longè don limyè wòz la?","q_fr":"Quelle est la longueur d'onde de la lumière rouge?","q_en":"What is the wavelength of red light?","opts_ht":["~400 nm","~500 nm","~600 nm","~700 nm"],"opts_fr":["~400 nm","~500 nm","~600 nm","~700 nm"],"opts_en":["~400 nm","~500 nm","~600 nm","~700 nm"],"ans":3},
      {"q_ht":"Ki pati selil ki kontwole sa ki antre ak sòti?","q_fr":"Quelle partie de la cellule contrôle ce qui entre et sort?","q_en":"Which part of the cell controls what enters and exits?","opts_ht":["Nwayo","Manbràn plasmatik","Mitokondri","Kloroplas"],"opts_fr":["Noyau","Membrane plasmique","Mitochondrie","Chloroplaste"],"opts_en":["Nucleus","Plasma membrane","Mitochondria","Chloroplast"],"ans":1},
    ],
    "hard": [
      {"q_ht":"Ki pati selil la ki kontwole ereditè?","q_fr":"Quelle partie de la cellule contrôle l'hérédité?","q_en":"Which part of the cell controls heredity?","opts_ht":["Mitokondri","Rilozòm","Nwayo","Manbràn"],"opts_fr":["Mitochondrie","Ribosome","Noyau","Membrane"],"opts_en":["Mitochondria","Ribosome","Nucleus","Membrane"],"ans":2},
      {"q_ht":"Ki valè konstan Plank la?","q_fr":"Quelle est la valeur de la constante de Planck?","q_en":"What is the value of Planck's constant?","opts_ht":["6.63×10⁻³⁴ J·s","9.11×10⁻³¹ kg","1.38×10⁻²³ J/K","3×10⁸ m/s"],"opts_fr":["6.63×10⁻³⁴ J·s","9.11×10⁻³¹ kg","1.38×10⁻²³ J/K","3×10⁸ m/s"],"opts_en":["6.63×10⁻³⁴ J·s","9.11×10⁻³¹ kg","1.38×10⁻²³ J/K","3×10⁸ m/s"],"ans":0},
      {"q_ht":"Ki pwosesis ki pwodui énerji nan solèy la?","q_fr":"Quel processus produit de l'énergie dans le Soleil?","q_en":"What process produces energy in the Sun?","opts_ht":["Fizyon nikleyè","Fizyon chimik","Fizyon niklèer","Kombiston"],"opts_fr":["Fusion nucléaire","Fission chimique","Fission nucléaire","Combustion"],"opts_en":["Nuclear fusion","Chemical fission","Nuclear fission","Combustion"],"ans":0},
      {"q_ht":"Ki nòm pou yon patikil ki gen mas men pa chaj?","q_fr":"Quel est le nom d'une particule ayant une masse mais pas de charge?","q_en":"What is a particle that has mass but no charge called?","opts_ht":["Pwotòn","Elektwon","Neytwon","Foton"],"opts_fr":["Proton","Électron","Neutron","Photon"],"opts_en":["Proton","Electron","Neutron","Photon"],"ans":2},
      {"q_ht":"Ki enzim ki kase pòlisakarid nan bouch?","q_fr":"Quelle enzyme décompose les polysaccharides dans la bouche?","q_en":"Which enzyme breaks down polysaccharides in the mouth?","opts_ht":["Pepsin","Amylaz","Lipaz","Trips"],"opts_fr":["Pepsine","Amylase","Lipase","Trypsine"],"opts_en":["Pepsin","Amylase","Lipase","Trypsin"],"ans":1},
      {"q_ht":"Ki prensip ensetitid Heisenberg la di?","q_fr":"Que dit le principe d'incertitude d'Heisenberg?","q_en":"What does Heisenberg's uncertainty principle state?","opts_ht":["Enèji konsève","Pa ka konnen egzakteman pozisyon ak vitès an menm tan","Limyè gen vitès konstan","Tout materyal fèt ak atòm"],"opts_fr":["L'énergie se conserve","On ne peut connaître exactement position et vitesse simultanément","La lumière a une vitesse constante","Toute matière est faite d'atomes"],"opts_en":["Energy is conserved","Cannot know exact position and velocity simultaneously","Light has constant speed","All matter is made of atoms"],"ans":1},
      {"q_ht":"Ki ekwasyon Einstein ki montre relasyon mas ak énerji?","q_fr":"Quelle équation d'Einstein montre la relation entre masse et énergie?","q_en":"Which Einstein equation shows the relationship between mass and energy?","opts_ht":["F=ma","E=mc²","PV=nRT","ΔE=hf"],"opts_fr":["F=ma","E=mc²","PV=nRT","ΔE=hf"],"opts_en":["F=ma","E=mc²","PV=nRT","ΔE=hf"],"ans":1},
      {"q_ht":"Ki nòm pou eta matye kote atòm yo separe an ion?","q_fr":"Quel est le nom de l'état de la matière où les atomes sont séparés en ions?","q_en":"What is the state of matter where atoms are separated into ions?","opts_ht":["Solid","Likid","Gaz","Plasma"],"opts_fr":["Solide","Liquide","Gaz","Plasma"],"opts_en":["Solid","Liquid","Gas","Plasma"],"ans":3},
      {"q_ht":"Ki pati nan sèvo ki kontwole ekilibr?","q_fr":"Quelle partie du cerveau contrôle l'équilibre?","q_en":"Which part of the brain controls balance?","opts_ht":["Serebra","Bèlwèl","Sèvèlèt","Pon"],"opts_fr":["Cerveau","Bulbe rachidien","Cervelet","Pont"],"opts_en":["Cerebrum","Medulla","Cerebellum","Pons"],"ans":2},
      {"q_ht":"Ki nòm pou transfòmasyon yon solid dirèkteman an gaz?","q_fr":"Comment appelle-t-on le passage direct d'un solide à l'état gazeux?","q_en":"What is the direct transformation of a solid to gas called?","opts_ht":["Evaporasyon","Kondansasyon","Siblimasyion","Fizyon"],"opts_fr":["Évaporation","Condensation","Sublimation","Fusion"],"opts_en":["Evaporation","Condensation","Sublimation","Fusion"],"ans":2},
      {"q_ht":"Ki nòm pou kantite patikil nan 1 mòl?","q_fr":"Quel est le nom du nombre de particules dans 1 mole?","q_en":"What is the number of particles in 1 mole called?","opts_ht":["Nòm Avogadro","Nòm Boltzmann","Nòm Faraday","Nòm Planck"],"opts_fr":["Nombre d'Avogadro","Constante de Boltzmann","Constante de Faraday","Constante de Planck"],"opts_en":["Avogadro's number","Boltzmann constant","Faraday constant","Planck's constant"],"ans":0},
      {"q_ht":"Ki tip ADN ki ranmase nan nwayo selil?","q_fr":"Quel type d'ADN est condensé dans le noyau cellulaire?","q_en":"What type of DNA is condensed in the cell nucleus?","opts_ht":["ARN","Kromatin","Plasmid","Ribozòm"],"opts_fr":["ARN","Chromatine","Plasmide","Ribosome"],"opts_en":["RNA","Chromatin","Plasmid","Ribosome"],"ans":1},
      {"q_ht":"Ki fòs ki kenbe nwayo atòm la ansanm?","q_fr":"Quelle force maintient le noyau atomique ensemble?","q_en":"What force holds the atomic nucleus together?","opts_ht":["Gravitasyon","Elektwomanyetis","Fòs nikleyè fò","Fòs nikleyè fèb"],"opts_fr":["Gravitation","Électromagnétisme","Force nucléaire forte","Force nucléaire faible"],"opts_en":["Gravity","Electromagnetism","Strong nuclear force","Weak nuclear force"],"ans":2},
      {"q_ht":"Ki tip vaksyen ki itilize pwoteyin viral?","q_fr":"Quel type de vaccin utilise des protéines virales?","q_en":"Which type of vaccine uses viral proteins?","opts_ht":["Vaksyen vivant afèbli","Vaksyen inaktive","Vaksyen sou-inite","Vaksyen ARNm"],"opts_fr":["Vaccin vivant atténué","Vaccin inactivé","Vaccin sous-unité","Vaccin ARNm"],"opts_en":["Live attenuated vaccine","Inactivated vaccine","Subunit vaccine","mRNA vaccine"],"ans":2},
      {"q_ht":"Ki nòm pou kantite matye ki degrade an mwatye?","q_fr":"Quel est le nom de la durée pour que la moitié d'une substance se dégrade?","q_en":"What is the time for half of a substance to decay called?","opts_ht":["Peryòd","Demi-vi","Entegrasyon","Dezentegrasyon"],"opts_fr":["Période","Demi-vie","Intégration","Désintégration"],"opts_en":["Period","Half-life","Integration","Disintegration"],"ans":1},
      {"q_ht":"Ki prensip termodinamik ki di énerji pa ka kreye ni detwi?","q_fr":"Quel principe de thermodynamique dit que l'énergie ne se crée ni ne se détruit?","q_en":"Which thermodynamic principle states energy cannot be created or destroyed?","opts_ht":["0yèm prensip","1ye prensip","2yèm prensip","3yèm prensip"],"opts_fr":["0ème principe","1er principe","2ème principe","3ème principe"],"opts_en":["0th law","1st law","2nd law","3rd law"],"ans":1},
      {"q_ht":"Ki pati kromatòsom ki pwoteje ekstremite yo?","q_fr":"Quelle partie du chromosome protège ses extrémités?","q_en":"Which part of the chromosome protects its ends?","opts_ht":["Sentromè","Telomè","Kinetokò","Kromatid"],"opts_fr":["Centromère","Télomère","Kinétochore","Chromatide"],"opts_en":["Centromere","Telomere","Kinetochore","Chromatid"],"ans":1},
      {"q_ht":"Ki tip ondilasyon ki pa bezwen mwayen pou pwopaje?","q_fr":"Quel type d'onde ne nécessite pas de milieu pour se propager?","q_en":"Which type of wave does not need a medium to propagate?","opts_ht":["Sismik","Sonò","Elektwomanyetik","Mekanik"],"opts_fr":["Sismique","Sonore","Électromagnétique","Mécanique"],"opts_en":["Seismic","Sound","Electromagnetic","Mechanical"],"ans":2},
      {"q_ht":"Ki nòm pou kantite pwotòn nan nwayo yon atòm?","q_fr":"Quel est le nom du nombre de protons dans le noyau d'un atome?","q_en":"What is the number of protons in an atom's nucleus called?","opts_ht":["Nòm mas","Nòm atomik","Nòm Avogadro","Valans"],"opts_fr":["Nombre de masse","Numéro atomique","Nombre d'Avogadro","Valence"],"opts_en":["Mass number","Atomic number","Avogadro's number","Valence"],"ans":1},
      {"q_ht":"Ki pati nan tèt ki pwodui ormòn kwoisan?","q_fr":"Quelle partie du cerveau produit l'hormone de croissance?","q_en":"Which part of the brain produces growth hormone?","opts_ht":["Epifiz","Ipotagalamus","Ipofiz","Talamus"],"opts_fr":["Épiphyse","Hypothalamus","Hypophyse","Thalamus"],"opts_en":["Pineal gland","Hypothalamus","Pituitary gland","Thalamus"],"ans":2},
    ],
  },
  "math": {
    "easy": [
      {"q_ht":"Ki valè pi (π)?","q_fr":"Quelle est la valeur de pi (π)?","q_en":"What is the value of pi (π)?","opts_ht":["2.14","3.14","4.14","3.41"],"opts_fr":["2.14","3.14","4.14","3.41"],"opts_en":["2.14","3.14","4.14","3.41"],"ans":1},
      {"q_ht":"Konbyen kote ki nan yon triyang?","q_fr":"Combien de côtés possède un triangle?","q_en":"How many sides does a triangle have?","opts_ht":["2","3","4","5"],"opts_fr":["2","3","4","5"],"opts_en":["2","3","4","5"],"ans":1},
      {"q_ht":"Ki rezilta 12 × 12?","q_fr":"Quel est le résultat de 12 × 12?","q_en":"What is 12 × 12?","opts_ht":["124","144","132","148"],"opts_fr":["124","144","132","148"],"opts_en":["124","144","132","148"],"ans":1},
      {"q_ht":"Konbyen fè 1000 milisegond?","q_fr":"Combien font 1000 millisecondes?","q_en":"How much is 1000 milliseconds?","opts_ht":["1 segond","1 minit","1 è","1 jou"],"opts_fr":["1 seconde","1 minute","1 heure","1 jour"],"opts_en":["1 second","1 minute","1 hour","1 day"],"ans":0},
      {"q_ht":"Ki nòm kare pafè 16?","q_fr":"Quelle est la racine carrée de 16?","q_en":"What is the square root of 16?","opts_ht":["2","3","4","5"],"opts_fr":["2","3","4","5"],"opts_en":["2","3","4","5"],"ans":2},
      {"q_ht":"Konbyen fè 15% de 200?","q_fr":"Combien font 15% de 200?","q_en":"What is 15% of 200?","opts_ht":["20","25","30","35"],"opts_fr":["20","25","30","35"],"opts_en":["20","25","30","35"],"ans":2},
      {"q_ht":"Ki pwopriyete ki di a+b = b+a?","q_fr":"Quelle propriété dit que a+b = b+a?","q_en":"Which property states that a+b = b+a?","opts_ht":["Asosyatif","Distribitif","Komitativ","Idantite"],"opts_fr":["Associative","Distributive","Commutative","Identité"],"opts_en":["Associative","Distributive","Commutative","Identity"],"ans":2},
      {"q_ht":"Ki rezilta 7 × 8?","q_fr":"Quel est le résultat de 7 × 8?","q_en":"What is 7 × 8?","opts_ht":["48","54","56","64"],"opts_fr":["48","54","56","64"],"opts_en":["48","54","56","64"],"ans":2},
      {"q_ht":"Konbyen fè 3/4 + 1/4?","q_fr":"Combien font 3/4 + 1/4?","q_en":"What is 3/4 + 1/4?","opts_ht":["1/2","3/8","1","4/8"],"opts_fr":["1/2","3/8","1","4/8"],"opts_en":["1/2","3/8","1","4/8"],"ans":2},
      {"q_ht":"Ki angle ki nan yon kare?","q_fr":"Quel est l'angle dans un carré?","q_en":"What is the angle in a square?","opts_ht":["45°","60°","90°","120°"],"opts_fr":["45°","60°","90°","120°"],"opts_en":["45°","60°","90°","120°"],"ans":2},
      {"q_ht":"Ki nòm nòm ki ka divize sèlman pa 1 ak li menm?","q_fr":"Quel est le nom d'un nombre divisible uniquement par 1 et lui-même?","q_en":"What is a number divisible only by 1 and itself called?","opts_ht":["Nòm pè","Nòm enpè","Nòm premye","Nòm konpozit"],"opts_fr":["Nombre pair","Nombre impair","Nombre premier","Nombre composé"],"opts_en":["Even number","Odd number","Prime number","Composite number"],"ans":2},
      {"q_ht":"Ki rezilta 100 ÷ 4?","q_fr":"Quel est le résultat de 100 ÷ 4?","q_en":"What is 100 ÷ 4?","opts_ht":["20","25","30","40"],"opts_fr":["20","25","30","40"],"opts_en":["20","25","30","40"],"ans":1},
      {"q_ht":"Ki fòmi pou sifas yon kare?","q_fr":"Quelle est la formule de la surface d'un carré?","q_en":"What is the formula for the area of a square?","opts_ht":["2×kote","kote²","4×kote","kote/2"],"opts_fr":["2×côté","côté²","4×côté","côté/2"],"opts_en":["2×side","side²","4×side","side/2"],"ans":1},
      {"q_ht":"Konbyen kote ki nan yon sèk?","q_fr":"Combien de côtés possède un cercle?","q_en":"How many sides does a circle have?","opts_ht":["0","1","2","Enfini"],"opts_fr":["0","1","2","Infini"],"opts_en":["0","1","2","Infinite"],"ans":3},
      {"q_ht":"Ki nòm pou twa fwa yon nòm?","q_fr":"Quel est le nom du triple d'un nombre?","q_en":"What is three times a number called?","opts_ht":["Doub","Trip","Katris","Kenkip"],"opts_fr":["Double","Triple","Quadruple","Quintuple"],"opts_en":["Double","Triple","Quadruple","Quintuple"],"ans":1},
      {"q_ht":"Ki rezilta 2⁵?","q_fr":"Quel est le résultat de 2⁵?","q_en":"What is 2⁵?","opts_ht":["16","32","64","128"],"opts_fr":["16","32","64","128"],"opts_en":["16","32","64","128"],"ans":1},
      {"q_ht":"Konbyen fè 25% de 80?","q_fr":"Combien font 25% de 80?","q_en":"What is 25% of 80?","opts_ht":["15","20","25","30"],"opts_fr":["15","20","25","30"],"opts_en":["15","20","25","30"],"ans":1},
      {"q_ht":"Ki rezilta √144?","q_fr":"Quel est le résultat de √144?","q_en":"What is √144?","opts_ht":["10","11","12","13"],"opts_fr":["10","11","12","13"],"opts_en":["10","11","12","13"],"ans":2},
      {"q_ht":"Konbyen fè 1 km an mèt?","q_fr":"Combien font 1 km en mètres?","q_en":"How many meters are in 1 km?","opts_ht":["100","500","1000","10000"],"opts_fr":["100","500","1000","10000"],"opts_en":["100","500","1000","10000"],"ans":2},
      {"q_ht":"Ki rezilta 9²?","q_fr":"Quel est le résultat de 9²?","q_en":"What is 9²?","opts_ht":["18","72","81","99"],"opts_fr":["18","72","81","99"],"opts_en":["18","72","81","99"],"ans":2},
    ],
    "medium": [
      {"q_ht":"Ki se lwa Pitagò a?","q_fr":"Quelle est la loi de Pythagore?","q_en":"What is the Pythagorean theorem?","opts_ht":["a+b=c","a²+b²=c²","a×b=c²","a²-b²=c"],"opts_fr":["a+b=c","a²+b²=c²","a×b=c²","a²-b²=c"],"opts_en":["a+b=c","a²+b²=c²","a×b=c²","a²-b²=c"],"ans":1},
      {"q_ht":"Ki rezilta 7! (sèt faktoryèl)?","q_fr":"Quel est le résultat de 7! (factorielle 7)?","q_en":"What is 7! (seven factorial)?","opts_ht":["720","1440","5040","2520"],"opts_fr":["720","1440","5040","2520"],"opts_en":["720","1440","5040","2520"],"ans":2},
      {"q_ht":"Ki formil perimèt sèk la?","q_fr":"Quelle est la formule du périmètre d'un cercle?","q_en":"What is the formula for the circumference of a circle?","opts_ht":["πr²","2πr","πd²","4πr"],"opts_fr":["πr²","2πr","πd²","4πr"],"opts_en":["πr²","2πr","πd²","4πr"],"ans":1},
      {"q_ht":"Ki valè log₁₀(100)?","q_fr":"Quelle est la valeur de log₁₀(100)?","q_en":"What is the value of log₁₀(100)?","opts_ht":["1","2","10","100"],"opts_fr":["1","2","10","100"],"opts_en":["1","2","10","100"],"ans":1},
      {"q_ht":"Ki formil sifas yon sèk?","q_fr":"Quelle est la formule de la surface d'un cercle?","q_en":"What is the formula for the area of a circle?","opts_ht":["2πr","πr²","πd","4πr²"],"opts_fr":["2πr","πr²","πd","4πr²"],"opts_en":["2πr","πr²","πd","4πr²"],"ans":1},
      {"q_ht":"Konbyen diagonale yon pentagon genyen?","q_fr":"Combien de diagonales possède un pentagone?","q_en":"How many diagonals does a pentagon have?","opts_ht":["3","4","5","6"],"opts_fr":["3","4","5","6"],"opts_en":["3","4","5","6"],"ans":2},
      {"q_ht":"Ki sòm angle enteryè yon triyang?","q_fr":"Quelle est la somme des angles intérieurs d'un triangle?","q_en":"What is the sum of interior angles of a triangle?","opts_ht":["90°","180°","270°","360°"],"opts_fr":["90°","180°","270°","360°"],"opts_en":["90°","180°","270°","360°"],"ans":1},
      {"q_ht":"Ki rezilta (x+3)(x-3)?","q_fr":"Quel est le résultat de (x+3)(x-3)?","q_en":"What is the result of (x+3)(x-3)?","opts_ht":["x²+9","x²-9","x²-6x+9","x²+6x-9"],"opts_fr":["x²+9","x²-9","x²-6x+9","x²+6x-9"],"opts_en":["x²+9","x²-9","x²-6x+9","x²+6x-9"],"ans":1},
      {"q_ht":"Ki nòm pou mwayen yon seri nòm?","q_fr":"Quel est le nom de la moyenne d'une série de nombres?","q_en":"What is the average of a series of numbers called?","opts_ht":["Medyan","Mòd","Mwayèn","Etandard"],"opts_fr":["Médiane","Mode","Moyenne","Écart-type"],"opts_en":["Median","Mode","Mean","Standard deviation"],"ans":2},
      {"q_ht":"Ki valè sin(90°)?","q_fr":"Quelle est la valeur de sin(90°)?","q_en":"What is the value of sin(90°)?","opts_ht":["0","0.5","1","√2/2"],"opts_fr":["0","0.5","1","√2/2"],"opts_en":["0","0.5","1","√2/2"],"ans":2},
      {"q_ht":"Konbyen fè 3² + 4²?","q_fr":"Combien font 3² + 4²?","q_en":"What is 3² + 4²?","opts_ht":["20","25","30","49"],"opts_fr":["20","25","30","49"],"opts_en":["20","25","30","49"],"ans":1},
      {"q_ht":"Ki formil volim yon kib?","q_fr":"Quelle est la formule du volume d'un cube?","q_en":"What is the formula for the volume of a cube?","opts_ht":["a²","a³","3a²","6a²"],"opts_fr":["a²","a³","3a²","6a²"],"opts_en":["a²","a³","3a²","6a²"],"ans":1},
      {"q_ht":"Ki valè cos(0°)?","q_fr":"Quelle est la valeur de cos(0°)?","q_en":"What is the value of cos(0°)?","opts_ht":["0","0.5","1","√3/2"],"opts_fr":["0","0.5","1","√3/2"],"opts_en":["0","0.5","1","√3/2"],"ans":2},
      {"q_ht":"Ki rezilta 2³ × 2²?","q_fr":"Quel est le résultat de 2³ × 2²?","q_en":"What is 2³ × 2²?","opts_ht":["2⁵","2⁶","4⁵","16"],"opts_fr":["2⁵","2⁶","4⁵","16"],"opts_en":["2⁵","2⁶","4⁵","16"],"ans":0},
      {"q_ht":"Ki nòm pou valè pwobabilite ant 0 ak 1?","q_fr":"Quel est le domaine de valeurs d'une probabilité?","q_en":"What is the range of values for probability?","opts_ht":["0 a ∞","−1 a 1","0 a 1","−∞ a ∞"],"opts_fr":["0 à ∞","−1 à 1","0 à 1","−∞ à ∞"],"opts_en":["0 to ∞","−1 to 1","0 to 1","−∞ to ∞"],"ans":2},
      {"q_ht":"Ki rezilta √(2²+2²)?","q_fr":"Quel est le résultat de √(2²+2²)?","q_en":"What is √(2²+2²)?","opts_ht":["2","2√2","4","√8"],"opts_fr":["2","2√2","4","√8"],"opts_en":["2","2√2","4","√8"],"ans":1},
      {"q_ht":"Ki fòmil pou kalkile enterè senp?","q_fr":"Quelle est la formule pour calculer l'intérêt simple?","q_en":"What is the formula for simple interest?","opts_ht":["I=P+r+t","I=P×r×t","I=P/r/t","I=(P×r)/t"],"opts_fr":["I=P+r+t","I=P×r×t","I=P/r/t","I=(P×r)/t"],"opts_en":["I=P+r+t","I=P×r×t","I=P/r/t","I=(P×r)/t"],"ans":1},
      {"q_ht":"Konbyen kote ki nan yon ègzagon?","q_fr":"Combien de côtés possède un hexagone?","q_en":"How many sides does a hexagon have?","opts_ht":["4","5","6","7"],"opts_fr":["4","5","6","7"],"opts_en":["4","5","6","7"],"ans":2},
      {"q_ht":"Ki valè tan(45°)?","q_fr":"Quelle est la valeur de tan(45°)?","q_en":"What is the value of tan(45°)?","opts_ht":["0","0.5","1","√3"],"opts_fr":["0","0.5","1","√3"],"opts_en":["0","0.5","1","√3"],"ans":2},
      {"q_ht":"Ki sòm angle enteryè yon kare?","q_fr":"Quelle est la somme des angles intérieurs d'un carré?","q_en":"What is the sum of interior angles of a square?","opts_ht":["180°","270°","360°","540°"],"opts_fr":["180°","270°","360°","540°"],"opts_en":["180°","270°","360°","540°"],"ans":2},
    ],
    "hard": [
      {"q_ht":"Ki sa yo rele yon matris ki transpose li menm?","q_fr":"Comment appelle-t-on une matrice égale à sa transposée?","q_en":"What is a matrix equal to its transpose called?","opts_ht":["Matris diagonale","Matris simètrik","Matris invers","Matris idantite"],"opts_fr":["Matrice diagonale","Matrice symétrique","Matrice inverse","Matrice identité"],"opts_en":["Diagonal matrix","Symmetric matrix","Inverse matrix","Identity matrix"],"ans":1},
      {"q_ht":"Ki nòm pou diferansyasyon y = xⁿ?","q_fr":"Quelle est la dérivée de y = xⁿ?","q_en":"What is the derivative of y = xⁿ?","opts_ht":["n·xⁿ","n·xⁿ⁻¹","xⁿ⁺¹/(n+1)","n/x"],"opts_fr":["n·xⁿ","n·xⁿ⁻¹","xⁿ⁺¹/(n+1)","n/x"],"opts_en":["n·xⁿ","n·xⁿ⁻¹","xⁿ⁺¹/(n+1)","n/x"],"ans":1},
      {"q_ht":"Ki rezilta e^(iπ) + 1?","q_fr":"Quel est le résultat de e^(iπ) + 1?","q_en":"What is e^(iπ) + 1?","opts_ht":["1","2i","0","-1"],"opts_fr":["1","2i","0","-1"],"opts_en":["1","2i","0","-1"],"ans":2},
      {"q_ht":"Ki formil volim yon sfè?","q_fr":"Quelle est la formule du volume d'une sphère?","q_en":"What is the formula for the volume of a sphere?","opts_ht":["4πr²","(4/3)πr³","πr²h","2πr³"],"opts_fr":["4πr²","(4/3)πr³","πr²h","2πr³"],"opts_en":["4πr²","(4/3)πr³","πr²h","2πr³"],"ans":1},
      {"q_ht":"Ki nòm pou yon seri kote chak tèm se pwodui tèm anvan ak yon rezon?","q_fr":"Quel est le nom d'une suite où chaque terme est le produit du précédent par une raison?","q_en":"What is a sequence where each term is the product of the previous by a ratio called?","opts_ht":["Aritmetik","Jewometrik","Fibonaci","Amilik"],"opts_fr":["Arithmétique","Géométrique","Fibonacci","Harmonique"],"opts_en":["Arithmetic","Geometric","Fibonacci","Harmonic"],"ans":1},
      {"q_ht":"Ki valè limite de sin(x)/x lè x→0?","q_fr":"Quelle est la limite de sin(x)/x quand x→0?","q_en":"What is the limit of sin(x)/x as x→0?","opts_ht":["0","1","∞","Indefini"],"opts_fr":["0","1","∞","Indéfini"],"opts_en":["0","1","∞","Undefined"],"ans":1},
      {"q_ht":"Ki nòm pou yon matris ki determinan li se 0?","q_fr":"Comment appelle-t-on une matrice dont le déterminant est 0?","q_en":"What is a matrix with determinant 0 called?","opts_ht":["Matris idantite","Matris sengilye","Matris diagonale","Matris simetrik"],"opts_fr":["Matrice identité","Matrice singulière","Matrice diagonale","Matrice symétrique"],"opts_en":["Identity matrix","Singular matrix","Diagonal matrix","Symmetric matrix"],"ans":1},
      {"q_ht":"Ki integrale ∫x² dx?","q_fr":"Quelle est l'intégrale de ∫x² dx?","q_en":"What is the integral of ∫x² dx?","opts_ht":["x³","x³/3 + C","2x","x²/2 + C"],"opts_fr":["x³","x³/3 + C","2x","x²/2 + C"],"opts_en":["x³","x³/3 + C","2x","x²/2 + C"],"ans":1},
      {"q_ht":"Ki teorem ki di yon fòm konvèks gen sòm angle = (n-2)×180°?","q_fr":"Quel théorème dit que la somme des angles d'un polygone convexe est (n-2)×180°?","q_en":"Which theorem states the sum of angles of a convex polygon is (n-2)×180°?","opts_ht":["Teorem Thalès","Teorem Pitagò","Teorem angle polonom","Teorem Euler"],"opts_fr":["Théorème de Thalès","Théorème de Pythagore","Théorème des angles d'un polygone","Théorème d'Euler"],"opts_en":["Thales' theorem","Pythagorean theorem","Polygon angle theorem","Euler's theorem"],"ans":2},
      {"q_ht":"Ki valè i² kote i = √(-1)?","q_fr":"Quelle est la valeur de i² où i = √(-1)?","q_en":"What is the value of i² where i = √(-1)?","opts_ht":["1","i","-1","-i"],"opts_fr":["1","i","-1","-i"],"opts_en":["1","i","-1","-i"],"ans":2},
      {"q_ht":"Ki nòm pou transfòmasyon f(x) = f(-x)?","q_fr":"Comment appelle-t-on une fonction telle que f(x) = f(-x)?","q_en":"What is a function where f(x) = f(-x) called?","opts_ht":["Fonksyon enpè","Fonksyon pè","Fonksyon bijektif","Fonksyon lineyè"],"opts_fr":["Fonction impaire","Fonction paire","Fonction bijective","Fonction linéaire"],"opts_en":["Odd function","Even function","Bijective function","Linear function"],"ans":1},
      {"q_ht":"Ki prensip matematik ki fonde teorèm enkonplètid Gödel?","q_fr":"Quel principe mathématique fonde le théorème d'incomplétude de Gödel?","q_en":"Which mathematical principle underpins Gödel's incompleteness theorem?","opts_ht":["Lojik fòmèl","Otorefrens","Enfini","Axiomatik"],"opts_fr":["Logique formelle","Auto-référence","Infini","Axiomatique"],"opts_en":["Formal logic","Self-reference","Infinity","Axiomatic"],"ans":1},
      {"q_ht":"Ki nòm pou yon espas vektoryèl ki fèmen sou adisyon ak multiplikasyon?","q_fr":"Quel est le nom d'un espace vectoriel fermé sous l'addition et la multiplication?","q_en":"What is a vector space closed under addition and multiplication called?","opts_ht":["Gwoup","Anèl","Ko","Espace Hilbert"],"opts_fr":["Groupe","Anneau","Corps","Espace de Hilbert"],"opts_en":["Group","Ring","Field","Hilbert space"],"ans":2},
      {"q_ht":"Ki teorem ki konekte diferansyasyon ak entegrasyon?","q_fr":"Quel théorème relie la différentiation et l'intégration?","q_en":"Which theorem connects differentiation and integration?","opts_ht":["Teorem Binom","Teorem fondamantal kalkil","Teorem Bayes","Teorem Fèma"],"opts_fr":["Théorème binomial","Théorème fondamental du calcul","Théorème de Bayes","Théorème de Fermat"],"opts_en":["Binomial theorem","Fundamental theorem of calculus","Bayes' theorem","Fermat's theorem"],"ans":1},
      {"q_ht":"Ki valè 0! (faktoryèl zewo)?","q_fr":"Quelle est la valeur de 0! (factorielle zéro)?","q_en":"What is the value of 0! (zero factorial)?","opts_ht":["0","1","Indefini","∞"],"opts_fr":["0","1","Indéfini","∞"],"opts_en":["0","1","Undefined","∞"],"ans":1},
      {"q_ht":"Ki nòm pou yon seri enfini ki sòm konvèj?","q_fr":"Comment appelle-t-on une série infinie dont la somme converge?","q_en":"What is an infinite series whose sum converges called?","opts_ht":["Seri divergan","Seri konvèjan","Seri geomatrik","Seri Taylor"],"opts_fr":["Série divergente","Série convergente","Série géométrique","Série de Taylor"],"opts_en":["Divergent series","Convergent series","Geometric series","Taylor series"],"ans":1},
      {"q_ht":"Ki nòm pou yon aplikasyon ki enjektif ak sijektif?","q_fr":"Quel est le nom d'une application à la fois injective et surjective?","q_en":"What is a function that is both injective and surjective called?","opts_ht":["Fonksyon pè","Fonksyon bijektif","Fonksyon lineyè","Fonksyon konstan"],"opts_fr":["Fonction paire","Fonction bijective","Fonction linéaire","Fonction constante"],"opts_en":["Even function","Bijective function","Linear function","Constant function"],"ans":1},
      {"q_ht":"Ki nòm pou distribisyon ki simetrik sou mwayen li?","q_fr":"Quel est le nom d'une distribution symétrique autour de sa moyenne?","q_en":"What is a distribution symmetric around its mean called?","opts_ht":["Distribisyon Poisson","Distribisyon nòmal","Distribisyon eksponansyèl","Distribisyon binomial"],"opts_fr":["Distribution de Poisson","Distribution normale","Distribution exponentielle","Distribution binomiale"],"opts_en":["Poisson distribution","Normal distribution","Exponential distribution","Binomial distribution"],"ans":1},
      {"q_ht":"Ki nòm pou yon transfòmasyon ki kenbe distans?","q_fr":"Quel est le nom d'une transformation qui conserve les distances?","q_en":"What is a transformation that preserves distances called?","opts_ht":["Ometri","Izometri","Similite","Projeksyon"],"opts_fr":["Homothétie","Isométrie","Similitude","Projection"],"opts_en":["Homothety","Isometry","Similarity","Projection"],"ans":1},
      {"q_ht":"Ki valè ∑(1/2ⁿ) pou n=1 a ∞?","q_fr":"Quelle est la valeur de ∑(1/2ⁿ) pour n=1 à ∞?","q_en":"What is the value of ∑(1/2ⁿ) for n=1 to ∞?","opts_ht":["1/2","1","2","∞"],"opts_fr":["1/2","1","2","∞"],"opts_en":["1/2","1","2","∞"],"ans":1},
    ],
  },
}

# Ajoute lòt kategori enpòtan yo tou (sport, tech, art, food, animals, hist) ak kesyon 3 lang
# Pou espas, itilize menm striktir a — ann kòmanse ak 5 kategori adisyonèl
QUESTIONS["sport"] = {
  "easy": [
    {"q_ht":"Konbyen jwè nan yon ekip foutbòl?","q_fr":"Combien de joueurs dans une équipe de football?","q_en":"How many players in a football team?","opts_ht":["9","10","11","12"],"opts_fr":["9","10","11","12"],"opts_en":["9","10","11","12"],"ans":2},
    {"q_ht":"Ki peyi ki òganize Koup Divin FIFA 2022?","q_fr":"Quel pays a organisé la Coupe du Monde FIFA 2022?","q_en":"Which country hosted the FIFA World Cup 2022?","opts_ht":["Risi","Emira Arab","Katar","Arabikasayidi"],"opts_fr":["Russie","Émirats Arabes Unis","Qatar","Arabie Saoudite"],"opts_en":["Russia","UAE","Qatar","Saudi Arabia"],"ans":2},
    {"q_ht":"Ki distans yon kous maraton?","q_fr":"Quelle est la distance d'un marathon?","q_en":"What is the distance of a marathon?","opts_ht":["21 km","42.195 km","40 km","50 km"],"opts_fr":["21 km","42.195 km","40 km","50 km"],"opts_en":["21 km","42.195 km","40 km","50 km"],"ans":1},
    {"q_ht":"Ki ekip foutbòl ki rele 'Les Bleus'?","q_fr":"Quelle équipe de football est surnommée 'Les Bleus'?","q_en":"Which football team is called 'Les Bleus'?","opts_ht":["Bèljik","Pòtigal","Frannce","Lèspay"],"opts_fr":["Belgique","Portugal","France","Espagne"],"opts_en":["Belgium","Portugal","France","Spain"],"ans":2},
    {"q_ht":"Nan ki espò yo itilize yon raket ak yon balòn jòn?","q_fr":"Dans quel sport utilise-t-on une raquette et une balle jaune?","q_en":"In which sport is a racket and yellow ball used?","opts_ht":["Badminton","Squash","Tenis","Ping-pong"],"opts_fr":["Badminton","Squash","Tennis","Ping-pong"],"opts_en":["Badminton","Squash","Tennis","Ping-pong"],"ans":2},
    {"q_ht":"Ki espò Usain Bolt pratike?","q_fr":"Quel sport pratique Usain Bolt?","q_en":"What sport does Usain Bolt practice?","opts_ht":["Naje","Kouri","Sote","Jète"],"opts_fr":["Natation","Athlétisme","Saut","Lancer"],"opts_en":["Swimming","Sprint","Jump","Throw"],"ans":1},
    {"q_ht":"Nan ki peyi yo pratike Sumo?","q_fr":"Dans quel pays pratique-t-on le sumo?","q_en":"In which country is sumo practiced?","opts_ht":["Lachin","Korè","Japon","Vyetnam"],"opts_fr":["Chine","Corée","Japon","Vietnam"],"opts_en":["China","Korea","Japan","Vietnam"],"ans":2},
    {"q_ht":"Ki peyi ki gen pi plis tit Koup Divin?","q_fr":"Quel pays a le plus de titres de Coupe du Monde?","q_en":"Which country has the most World Cup titles?","opts_ht":["Aljemàn","Itali","Brezil","Frannce"],"opts_fr":["Allemagne","Italie","Brésil","France"],"opts_en":["Germany","Italy","Brazil","France"],"ans":2},
    {"q_ht":"Konbyen jwè nan yon ekip baskètbòl?","q_fr":"Combien de joueurs dans une équipe de basketball?","q_en":"How many players in a basketball team?","opts_ht":["4","5","6","7"],"opts_fr":["4","5","6","7"],"opts_en":["4","5","6","7"],"ans":1},
    {"q_ht":"Ki espò ki jwe nan Wimbledon?","q_fr":"Quel sport se joue à Wimbledon?","q_en":"Which sport is played at Wimbledon?","opts_ht":["Foutbòl","Golf","Tenis","Krikèt"],"opts_fr":["Football","Golf","Tennis","Cricket"],"opts_en":["Football","Golf","Tennis","Cricket"],"ans":2},
    {"q_ht":"Ki nòm pou yon gòl nan foutbòl ameriken?","q_fr":"Comment s'appelle un but au football américain?","q_en":"What is a goal called in American football?","opts_ht":["Gòl","Touchdown","Score","Point"],"opts_fr":["But","Touchdown","Score","Point"],"opts_en":["Goal","Touchdown","Score","Point"],"ans":1},
    {"q_ht":"Konbyen mèt pi nan yon piscin konpetisyon?","q_fr":"Combien de mètres mesure une piscine de compétition?","q_en":"How many meters long is a competition pool?","opts_ht":["25m","50m","75m","100m"],"opts_fr":["25m","50m","75m","100m"],"opts_en":["25m","50m","75m","100m"],"ans":1},
    {"q_ht":"Ki trofè yo bay pi bon jwè Mondyal FIFA?","q_fr":"Quel trophée récompense le meilleur joueur FIFA?","q_en":"What trophy is given to the best FIFA player?","opts_ht":["Bawon dò","Balon dò","Trofè dò","Bòt dò"],"opts_fr":["Baron d'or","Ballon d'or","Trophée d'or","Botte d'or"],"opts_en":["Golden Baron","Golden Ball","Golden Trophy","Golden Boot"],"ans":1},
    {"q_ht":"Nan ki vil yo jwe Super Bowl?","q_fr":"Dans quelle ville se joue le Super Bowl?","q_en":"In which city is the Super Bowl played?","opts_ht":["Toujou menm kote","Chanje chak ane","New York","Los Angeles"],"opts_fr":["Toujours au même endroit","Change chaque année","New York","Los Angeles"],"opts_en":["Always same place","Changes each year","New York","Los Angeles"],"ans":1},
    {"q_ht":"Ki ekip foutbòl espay ki pi popilè?","q_fr":"Quelle équipe de football espagnole est la plus populaire?","q_en":"Which Spanish football team is most popular?","opts_ht":["Barcelona","Real Madrid","Atletico Madrid","Valencia"],"opts_fr":["Barcelone","Real Madrid","Atletico Madrid","Valence"],"opts_en":["Barcelona","Real Madrid","Atletico Madrid","Valencia"],"ans":1},
    {"q_ht":"Ki nòm pou rekòlte yon balòn golf nan twou a?","q_fr":"Comment appelle-t-on le fait d'empocher la balle de golf dans le trou?","q_en":"What is it called when a golf ball goes in the hole?","opts_ht":["Strike","Hole-in-one","Birdie","Eagle"],"opts_fr":["Strike","Trou en un","Birdie","Eagle"],"opts_en":["Strike","Hole-in-one","Birdie","Eagle"],"ans":1},
    {"q_ht":"Ki rekò mond Usain Bolt nan 100m?","q_fr":"Quel est le record du monde d'Usain Bolt au 100m?","q_en":"What is Usain Bolt's world record in the 100m?","opts_ht":["9.58s","9.69s","9.72s","9.81s"],"opts_fr":["9.58s","9.69s","9.72s","9.81s"],"opts_en":["9.58s","9.69s","9.72s","9.81s"],"ans":0},
    {"q_ht":"Ki ane Olimpik modèn premye fèt?","q_fr":"En quelle année les Jeux olympiques modernes ont-ils débuté?","q_en":"In what year did the modern Olympics first take place?","opts_ht":["1892","1896","1900","1904"],"opts_fr":["1892","1896","1900","1904"],"opts_en":["1892","1896","1900","1904"],"ans":1},
    {"q_ht":"Ki peyi ki envante baskètbòl?","q_fr":"Quel pays a inventé le basketball?","q_en":"Which country invented basketball?","opts_ht":["Etazini","Kanada","Angletè","Frannce"],"opts_fr":["États-Unis","Canada","Angleterre","France"],"opts_en":["USA","Canada","England","France"],"ans":0},
    {"q_ht":"Ki nòm pou yon kout frapò nan bòks ki frape advasè nan figi?","q_fr":"Comment appelle-t-on un coup de poing en boxe frappant le visage de l'adversaire?","q_en":"What is a punch in boxing that hits the opponent's face called?","opts_ht":["Kros","Jab","Apèkèt","Kout bwa"],"opts_fr":["Crochet","Jab","Uppercut","Cross"],"opts_en":["Hook","Jab","Uppercut","Cross"],"ans":1},
  ],
  "medium": [
    {"q_ht":"Ki moun ki genyen pi plis tit Wimbledon masculin?","q_fr":"Qui a remporté le plus de titres à Wimbledon en simple messieurs?","q_en":"Who has won the most Wimbledon men's singles titles?","opts_ht":["Federer","Djokovic","Nadal","Sampras"],"opts_fr":["Federer","Djokovic","Nadal","Sampras"],"opts_en":["Federer","Djokovic","Nadal","Sampras"],"ans":1},
    {"q_ht":"Konbyen sèt pou genyen yon match Grand Chèlèm masculin?","q_fr":"Combien de sets faut-il gagner pour remporter un Grand Chelem masculin?","q_en":"How many sets to win a men's Grand Slam match?","opts_ht":["2","3","4","5"],"opts_fr":["2","3","4","5"],"opts_en":["2","3","4","5"],"ans":1},
    {"q_ht":"Ki ekip ki genyen pi plis Champions League?","q_fr":"Quelle équipe a remporté le plus de Ligues des Champions?","q_en":"Which team has won the most Champions League titles?","opts_ht":["Barcelona","Bayern Munich","Real Madrid","Liverpool"],"opts_fr":["Barcelone","Bayern Munich","Real Madrid","Liverpool"],"opts_en":["Barcelona","Bayern Munich","Real Madrid","Liverpool"],"ans":2},
    {"q_ht":"Ki nòm pou yon pwen nan tenis kote sèvis la pa touche kò advasè?","q_fr":"Comment appelle-t-on un service de tennis qui n'est pas retourné?","q_en":"What is a tennis serve that is not returned called?","opts_ht":["Fòt","As","Lèt","Sèvis"],"opts_fr":["Faute","As","Let","Service"],"opts_en":["Fault","Ace","Let","Serve"],"ans":1},
    {"q_ht":"Ki espò ki gen kat peryòd 15 minit?","q_fr":"Quel sport comporte quatre périodes de 15 minutes?","q_en":"Which sport has four 15-minute periods?","opts_ht":["Foutbòl","Baskètbòl","Foutbòl ameriken","Okèy"],"opts_fr":["Football","Basketball","Football américain","Hockey"],"opts_en":["Football","Basketball","American football","Hockey"],"ans":2},
    {"q_ht":"Ki moun ki rele 'King James' nan baskètbòl?","q_fr":"Qui est surnommé 'King James' au basketball?","q_en":"Who is nicknamed 'King James' in basketball?","opts_ht":["Kobe Bryant","Michael Jordan","LeBron James","Shaquille O'Neal"],"opts_fr":["Kobe Bryant","Michael Jordan","LeBron James","Shaquille O'Neal"],"opts_en":["Kobe Bryant","Michael Jordan","LeBron James","Shaquille O'Neal"],"ans":2},
    {"q_ht":"Ki distans yon kous semi-maraton?","q_fr":"Quelle est la distance d'un semi-marathon?","q_en":"What is the distance of a half marathon?","opts_ht":["10 km","15 km","21.097 km","30 km"],"opts_fr":["10 km","15 km","21.097 km","30 km"],"opts_en":["10 km","15 km","21.097 km","30 km"],"ans":2},
    {"q_ht":"Ki ekip ki te fè yo yo rele 'Dream Team' nan 1992?","q_fr":"Quelle équipe était surnommée 'Dream Team' en 1992?","q_en":"Which team was called the 'Dream Team' in 1992?","opts_ht":["Chicago Bulls","USA baskètbòl","Boston Celtics","LA Lakers"],"opts_fr":["Chicago Bulls","Équipe USA basketball","Boston Celtics","LA Lakers"],"opts_en":["Chicago Bulls","USA basketball team","Boston Celtics","LA Lakers"],"ans":1},
    {"q_ht":"Ki moun ki gen plis meday Olimpik nan istwa?","q_fr":"Qui possède le plus de médailles olympiques dans l'histoire?","q_en":"Who has the most Olympic medals in history?","opts_ht":["Carl Lewis","Usain Bolt","Michael Phelps","Mark Spitz"],"opts_fr":["Carl Lewis","Usain Bolt","Michael Phelps","Mark Spitz"],"opts_en":["Carl Lewis","Usain Bolt","Michael Phelps","Mark Spitz"],"ans":2},
    {"q_ht":"Ki ane FIFA te kreye?","q_fr":"En quelle année la FIFA a-t-elle été créée?","q_en":"In what year was FIFA founded?","opts_ht":["1900","1904","1910","1920"],"opts_fr":["1900","1904","1910","1920"],"opts_en":["1900","1904","1910","1920"],"ans":1},
    {"q_ht":"Ki nòm pou sistèm nan golf kote chak trou gen yon nòm pou zèklè?","q_fr":"Comment appelle-t-on le score de référence par trou au golf?","q_en":"What is the reference score per hole in golf called?","opts_ht":["Eagle","Birdie","Par","Bogey"],"opts_fr":["Eagle","Birdie","Par","Bogey"],"opts_en":["Eagle","Birdie","Par","Bogey"],"ans":2},
    {"q_ht":"Ki moun ki te kreye espò lacros?","q_fr":"Qui a inventé la crosse?","q_en":"Who invented lacrosse?","opts_ht":["Angle","Pèp endijèn Amerik Nò","Frannce","Kanada"],"opts_fr":["Anglais","Peuples autochtones d'Amérique du Nord","Français","Canadiens"],"opts_en":["English","Indigenous North Americans","French","Canadians"],"ans":1},
    {"q_ht":"Ki peyi ki envante ròbi?","q_fr":"Quel pays a inventé le rugby?","q_en":"Which country invented rugby?","opts_ht":["Frannce","Angletè","Ostrali","Ekòs"],"opts_fr":["France","Angleterre","Australie","Écosse"],"opts_en":["France","England","Australia","Scotland"],"ans":1},
    {"q_ht":"Ki ekip foutbòl ki rele 'Die Mannschaft'?","q_fr":"Quelle équipe de football est surnommée 'Die Mannschaft'?","q_en":"Which football team is nicknamed 'Die Mannschaft'?","opts_ht":["Otrich","Swis","Almay","Oland"],"opts_fr":["Autriche","Suisse","Allemagne","Pays-Bas"],"opts_en":["Austria","Switzerland","Germany","Netherlands"],"ans":2},
    {"q_ht":"Ki moun ki gen pi plis tit Grand Chèlèm nan tenis maskilin?","q_fr":"Qui possède le plus de titres du Grand Chelem en tennis masculin?","q_en":"Who has the most Grand Slam titles in men's tennis?","opts_ht":["Federer","Djokovic","Nadal","Sampras"],"opts_fr":["Federer","Djokovic","Nadal","Sampras"],"opts_en":["Federer","Djokovic","Nadal","Sampras"],"ans":1},
    {"q_ht":"Ki espò Simone Biles pratike?","q_fr":"Quel sport pratique Simone Biles?","q_en":"What sport does Simone Biles practice?","opts_ht":["Naje","Jimnastik","Atletis","Paten"],"opts_fr":["Natation","Gymnastique","Athlétisme","Patinage"],"opts_en":["Swimming","Gymnastics","Athletics","Skating"],"ans":1},
    {"q_ht":"Ki nòm pou yon kout frapò nan bòks ki frape advasè nan machwa?","q_fr":"Comment appelle-t-on un coup de poing en boxe touchant la mâchoire adverse?","q_en":"What is a punch targeting the opponent's jaw in boxing called?","opts_ht":["Jab","Kros","Apèkèt","Kout bwa"],"opts_fr":["Jab","Crochet","Uppercut","Cross"],"opts_en":["Jab","Hook","Uppercut","Cross"],"ans":1},
    {"q_ht":"Ki peyi ki gen pi plis meday nan istwa Olimpik?","q_fr":"Quel pays a remporté le plus de médailles dans l'histoire des Jeux olympiques?","q_en":"Which country has won the most medals in Olympic history?","opts_ht":["Risi","Almay","Lachin","Etazini"],"opts_fr":["Russie","Allemagne","Chine","États-Unis"],"opts_en":["Russia","Germany","China","USA"],"ans":3},
    {"q_ht":"Ki nòm ekip nasyonal foutbòl Brezil la?","q_fr":"Quel est le surnom de l'équipe nationale de football du Brésil?","q_en":"What is the nickname of Brazil's national football team?","opts_ht":["Kanarin","Seleksyon","Samba","Auriverde"],"opts_fr":["Canari","Seleção","Samba","Auriverde"],"opts_en":["Canary","Seleção","Samba","Auriverde"],"ans":1},
    {"q_ht":"Ki espò ki gen 'slam dunk'?","q_fr":"Dans quel sport réalise-t-on un 'slam dunk'?","q_en":"In which sport is a 'slam dunk' performed?","opts_ht":["Foutbòl","Baskètbòl","Vòlibòl","Tenisbòl"],"opts_fr":["Football","Basketball","Volleyball","Tennisball"],"opts_en":["Football","Basketball","Volleyball","Tennisball"],"ans":1},
  ],
  "hard": [
    {"q_ht":"Ki espò 'Jai-alai' soti?","q_fr":"De quel pays est originaire le 'Jai-alai'?","q_en":"Which country does 'Jai-alai' originate from?","opts_ht":["Lèspay","Meksik","Pèyi Bask","Kiba"],"opts_fr":["Espagne","Mexique","Pays Basque","Cuba"],"opts_en":["Spain","Mexico","Basque Country","Cuba"],"ans":2},
    {"q_ht":"Ki moun ki te ba F1 tit mondyal pou premye fwa nan istwa?","q_fr":"Qui a remporté le premier titre mondial de Formule 1?","q_en":"Who won the first Formula 1 world title?","opts_ht":["Fangio","Senna","Schumacher","Lauda"],"opts_fr":["Fangio","Senna","Schumacher","Lauda"],"opts_en":["Fangio","Senna","Schumacher","Lauda"],"ans":0},
    {"q_ht":"Ki ane bòks te vin espò Olimpik pou fanm?","q_fr":"En quelle année la boxe est-elle devenue un sport olympique féminin?","q_en":"In what year did women's boxing become an Olympic sport?","opts_ht":["2004","2008","2012","2016"],"opts_fr":["2004","2008","2012","2016"],"opts_en":["2004","2008","2012","2016"],"ans":2},
    {"q_ht":"Ki rekò mond nan sòt wotè?","q_fr":"Quel est le record du monde du saut en hauteur?","q_en":"What is the world record in the high jump?","opts_ht":["2.35m","2.40m","2.45m","2.50m"],"opts_fr":["2.35m","2.40m","2.45m","2.50m"],"opts_en":["2.35m","2.40m","2.45m","2.50m"],"ans":2},
    {"q_ht":"Ki peyi ki te envante bòlling?","q_fr":"Quel pays a inventé le bowling?","q_en":"Which country invented bowling?","opts_ht":["Etazini","Almay","Angletè","Oland"],"opts_fr":["États-Unis","Allemagne","Angleterre","Pays-Bas"],"opts_en":["USA","Germany","England","Netherlands"],"ans":1},
    {"q_ht":"Ki nòm teknik nan golf kote jwè a fè mwens ke par nan yon trou?","q_fr":"Comment appelle-t-on le fait de faire moins que le par sur un trou au golf?","q_en":"What is scoring below par on a golf hole called?","opts_ht":["Eagle","Birdie","Bogey","Double bogey"],"opts_fr":["Eagle","Birdie","Bogey","Double bogey"],"opts_en":["Eagle","Birdie","Bogey","Double bogey"],"ans":1},
    {"q_ht":"Ki moun ki genyen pi plis meday nan yon sèl Jwèt Olimpik?","q_fr":"Qui a remporté le plus de médailles lors d'une seule édition des Jeux olympiques?","q_en":"Who won the most medals in a single Olympic Games?","opts_ht":["Mark Spitz","Michael Phelps","Larisa Latynina","Carl Lewis"],"opts_fr":["Mark Spitz","Michael Phelps","Larisa Latynina","Carl Lewis"],"opts_en":["Mark Spitz","Michael Phelps","Larisa Latynina","Carl Lewis"],"ans":1},
    {"q_ht":"Ki ekip ki te genyen premye Koup Divin FIFA 1930?","q_fr":"Quelle équipe a remporté la première Coupe du Monde FIFA en 1930?","q_en":"Which team won the first FIFA World Cup in 1930?","opts_ht":["Brezil","Aljantèn","Irigwèy","Frannce"],"opts_fr":["Brésil","Argentine","Uruguay","France"],"opts_en":["Brazil","Argentina","Uruguay","France"],"ans":2},
    {"q_ht":"Ki pwen Olimpik ki pi wo nan istwa jimnastik?","q_fr":"Quel est le score olympique le plus élevé dans l'histoire de la gymnastique?","q_en":"What is the highest Olympic score in gymnastics history?","opts_ht":["9.9","10.0","9.95","9.8"],"opts_fr":["9.9","10.0","9.95","9.8"],"opts_en":["9.9","10.0","9.95","9.8"],"ans":1},
    {"q_ht":"Ki moun ki te envante jimnastik modèn?","q_fr":"Qui a inventé la gymnastique moderne?","q_en":"Who invented modern gymnastics?","opts_ht":["Friedrich Ludwig Jahn","Pierre de Coubertin","Nadia Comaneci","Bela Karolyi"],"opts_fr":["Friedrich Ludwig Jahn","Pierre de Coubertin","Nadia Comaneci","Bela Karolyi"],"opts_en":["Friedrich Ludwig Jahn","Pierre de Coubertin","Nadia Comaneci","Bela Karolyi"],"ans":0},
    {"q_ht":"Ki vitès balòn nan tenis kote sèvis ki pi rapid nan istwa?","q_fr":"Quelle est la vitesse du service de tennis le plus rapide de l'histoire?","q_en":"What is the speed of the fastest tennis serve in history?","opts_ht":["220 km/h","230 km/h","247 km/h","260 km/h"],"opts_fr":["220 km/h","230 km/h","247 km/h","260 km/h"],"opts_en":["220 km/h","230 km/h","247 km/h","260 km/h"],"ans":2},
    {"q_ht":"Ki moun ki te genyen pi plis Tour de France?","q_fr":"Qui a remporté le plus de Tours de France?","q_en":"Who has won the most Tour de France titles?","opts_ht":["Lance Armstrong","Chris Froome","Eddy Merckx","Bernard Hinault"],"opts_fr":["Lance Armstrong","Chris Froome","Eddy Merckx","Bernard Hinault"],"opts_en":["Lance Armstrong","Chris Froome","Eddy Merckx","Bernard Hinault"],"ans":2},
    {"q_ht":"Ki espò ki gen yon ekip 'All Blacks'?","q_fr":"Quel sport possède une équipe appelée 'All Blacks'?","q_en":"Which sport has a team called 'All Blacks'?","opts_ht":["Foutbòl","Ròbi","Krikèt","Naje"],"opts_fr":["Football","Rugby","Cricket","Natation"],"opts_en":["Football","Rugby","Cricket","Swimming"],"ans":1},
    {"q_ht":"Ki moun ki gen pi plis gòl nan istwa foutbòl mondyal?","q_fr":"Qui a marqué le plus de buts dans l'histoire du football mondial?","q_en":"Who has scored the most goals in world football history?","opts_ht":["Messi","Ronaldo","Pele","Maradona"],"opts_fr":["Messi","Ronaldo","Pelé","Maradona"],"opts_en":["Messi","Ronaldo","Pele","Maradona"],"ans":1},
    {"q_ht":"Ki ane baskètbòl te ajoute nan Jwèt Olimpik?","q_fr":"En quelle année le basketball a-t-il été ajouté aux Jeux olympiques?","q_en":"In what year was basketball added to the Olympic Games?","opts_ht":["1932","1936","1948","1952"],"opts_fr":["1932","1936","1948","1952"],"opts_en":["1932","1936","1948","1952"],"ans":1},
    {"q_ht":"Ki rekò mond nan 400m plat?","q_fr":"Quel est le record du monde du 400m plat?","q_en":"What is the 400m flat world record?","opts_ht":["43.00s","43.03s","43.18s","43.50s"],"opts_fr":["43.00s","43.03s","43.18s","43.50s"],"opts_en":["43.00s","43.03s","43.18s","43.50s"],"ans":1},
    {"q_ht":"Ki peyi ki envante krikèt?","q_fr":"Quel pays a inventé le cricket?","q_en":"Which country invented cricket?","opts_ht":["Ostrali","Zend","Angletè","Pakistan"],"opts_fr":["Australie","Inde","Angleterre","Pakistan"],"opts_en":["Australia","India","England","Pakistan"],"ans":2},
    {"q_ht":"Ki nòm pou yon kout nan eskirim ki fèt avèk epè?","q_fr":"Comment appelle-t-on une touche à l'escrime avec une épée?","q_en":"What is a hit in fencing with a sword called?","opts_ht":["Toush","Pon","Para","Atak"],"opts_fr":["Touche","Botte","Parade","Attaque"],"opts_en":["Touché","Thrust","Parry","Attack"],"ans":0},
    {"q_ht":"Ki espò ki gen 'slam' nan tenis detab?","q_fr":"Quel sport possède un 'Grand Chelem' comme au tennis de table?","q_en":"Which sport has a 'Grand Slam' like table tennis?","opts_ht":["Tenis detab","Badminton","Squash","Padèl"],"opts_fr":["Tennis de table","Badminton","Squash","Padel"],"opts_en":["Table tennis","Badminton","Squash","Padel"],"ans":0},
    {"q_ht":"Ki vitès bal nan bòlling pou yon frapè pwofesyonèl?","q_fr":"Quelle est la vitesse d'une boule de bowling pour un joueur professionnel?","q_en":"What speed do professional bowlers throw the ball?","opts_ht":["15-18 mph","18-22 mph","22-28 mph","28-35 mph"],"opts_fr":["15-18 mph","18-22 mph","22-28 mph","28-35 mph"],"opts_en":["15-18 mph","18-22 mph","22-28 mph","28-35 mph"],"ans":2},
    {"q_ht":"Ki espò 'pelota' popilè?","q_fr":"Dans quel pays le 'pelota' est-il populaire?","q_en":"In which country is 'pelota' popular?","opts_ht":["Lèspay","Meksik","Pèyi Bask","Kiba"],"opts_fr":["Espagne","Mexique","Pays Basque","Cuba"],"opts_en":["Spain","Mexico","Basque Country","Cuba"],"ans":2},
  ],
}

# Pou tech, art, food, animals — itilize kesyon orijinal yo ak estrikti 3 lang
# (Tradui kle yo pou asire fonksyonman)
def _q3(ht, fr, en, oht, ofr, oen, a):
    return {"q_ht":ht,"q_fr":fr,"q_en":en,"opts_ht":oht,"opts_fr":ofr,"opts_en":oen,"ans":a}

QUESTIONS["tech"] = {
  "easy": [
    _q3("Ki konpayi ki devlope iPhone a?","Quelle entreprise a développé l'iPhone?","Which company developed the iPhone?",["Samsung","Apple","Google","Microsoft"],["Samsung","Apple","Google","Microsoft"],["Samsung","Apple","Google","Microsoft"],1),
    _q3("Ki siyifikasyon 'CPU'?","Que signifie 'CPU'?","What does 'CPU' stand for?",["Central Processing Unit","Computer Power Unit","Core Program Utility","Central Program User"],["Central Processing Unit","Computer Power Unit","Core Program Utility","Central Program User"],["Central Processing Unit","Computer Power Unit","Core Program Utility","Central Program User"],0),
    _q3("Ki rezo sosyal Mark Zuckerberg fonde?","Quel réseau social Mark Zuckerberg a-t-il fondé?","Which social network did Mark Zuckerberg found?",["Twitter","Instagram","Facebook","TikTok"],["Twitter","Instagram","Facebook","TikTok"],["Twitter","Instagram","Facebook","TikTok"],2),
    _q3("Ki motè rechèch ki pi popilè?","Quel moteur de recherche est le plus populaire?","Which search engine is most popular?",["Bing","Yahoo","Google","DuckDuckGo"],["Bing","Yahoo","Google","DuckDuckGo"],["Bing","Yahoo","Google","DuckDuckGo"],2),
    _q3("Ki siyifikasyon 'AI'?","Que signifie 'IA'?","What does 'AI' stand for?",["Automated Internet","Artificial Intelligence","Advanced Integration","Applied Innovation"],["Internet Automatisé","Intelligence Artificielle","Intégration Avancée","Innovation Appliquée"],["Automated Internet","Artificial Intelligence","Advanced Integration","Applied Innovation"],1),
    _q3("Ki siyifikasyon 'WWW'?","Que signifie 'WWW'?","What does 'WWW' stand for?",["World Wide Web","World Work Web","Wide World Web","Web World Wide"],["World Wide Web","World Work Web","Wide World Web","Web World Wide"],["World Wide Web","World Work Web","Wide World Web","Web World Wide"],0),
    _q3("Ki konpayi ki fè Windows?","Quelle entreprise fabrique Windows?","Which company makes Windows?",["Apple","Google","Microsoft","IBM"],["Apple","Google","Microsoft","IBM"],["Apple","Google","Microsoft","IBM"],2),
    _q3("Ki lang pwogramason Python kreye pa ki moun?","Qui a créé le langage Python?","Who created the Python programming language?",["Linus Torvalds","Guido van Rossum","James Gosling","Dennis Ritchie"],["Linus Torvalds","Guido van Rossum","James Gosling","Dennis Ritchie"],["Linus Torvalds","Guido van Rossum","James Gosling","Dennis Ritchie"],1),
    _q3("Ki pwotokòl yo itilize pou voye imèl?","Quel protocole est utilisé pour envoyer des emails?","Which protocol is used to send emails?",["FTP","HTTP","SMTP","SSH"],["FTP","HTTP","SMTP","SSH"],["FTP","HTTP","SMTP","SSH"],2),
    _q3("Ki siyifikasyon 'USB'?","Que signifie 'USB'?","What does 'USB' stand for?",["Universal Serial Bus","Unified System Bus","Universal Sync Block","United Serial Base"],["Universal Serial Bus","Unified System Bus","Universal Sync Block","United Serial Base"],["Universal Serial Bus","Unified System Bus","Universal Sync Block","United Serial Base"],0),
    _q3("Ki konpayi ki fabrike chip M1 ak M2?","Quelle entreprise fabrique les puces M1 et M2?","Which company makes M1 and M2 chips?",["Intel","AMD","Qualcomm","Apple"],["Intel","AMD","Qualcomm","Apple"],["Intel","AMD","Qualcomm","Apple"],3),
    _q3("Ki siyifikasyon 'RAM'?","Que signifie 'RAM'?","What does 'RAM' stand for?",["Random Access Memory","Read Access Memory","Rapid Access Memory","Real Access Memory"],["Random Access Memory","Read Access Memory","Rapid Access Memory","Real Access Memory"],["Random Access Memory","Read Access Memory","Rapid Access Memory","Real Access Memory"],0),
    _q3("Ki siyifikasyon 'DNS'?","Que signifie 'DNS'?","What does 'DNS' stand for?",["Digital Network System","Domain Name System","Data Node Service","Dynamic Net Stack"],["Digital Network System","Domain Name System","Data Node Service","Dynamic Net Stack"],["Digital Network System","Domain Name System","Data Node Service","Dynamic Net Stack"],1),
    _q3("Ki algoritm yo itilize nan Bitcoin?","Quel algorithme est utilisé dans Bitcoin?","Which algorithm is used in Bitcoin?",["RSA","SHA-256","AES","MD5"],["RSA","SHA-256","AES","MD5"],["RSA","SHA-256","AES","MD5"],1),
    _q3("Ki valè ki stoke nan yon bit?","Quelle valeur est stockée dans un bit?","What value is stored in a bit?",["0 a 255","0 oubyen 1","-128 a 127","0 a 1023"],["0 à 255","0 ou 1","-128 à 127","0 à 1023"],["0 to 255","0 or 1","-128 to 127","0 to 1023"],1),
    _q3("Ki pwotokòl sekirize kominikasyon sou entènèt?","Quel protocole sécurise les communications internet?","Which protocol secures internet communications?",["HTTP","FTP","TLS/SSL","UDP"],["HTTP","FTP","TLS/SSL","UDP"],["HTTP","FTP","TLS/SSL","UDP"],2),
    _q3("Ki lang yo itilize pou kreye paj web?","Quel langage est utilisé pour créer des pages web?","Which language is used to create web pages?",["Python","Java","HTML","C++"],["Python","Java","HTML","C++"],["Python","Java","HTML","C++"],2),
    _q3("Ki sistèm operasyon Apple itilize sou iPhone?","Quel système d'exploitation Apple utilise sur iPhone?","Which OS does Apple use on iPhone?",["Android","Windows","iOS","Linux"],["Android","Windows","iOS","Linux"],["Android","Windows","iOS","Linux"],2),
    _q3("Ki lang pwogramason Google kreye?","Quel langage de programmation Google a-t-il créé?","Which programming language did Google create?",["Swift","Go","Kotlin","Rust"],["Swift","Go","Kotlin","Rust"],["Swift","Go","Kotlin","Rust"],1),
    _q3("Ki siyifikasyon 'GPU'?","Que signifie 'GPU'?","What does 'GPU' stand for?",["General Processing Unit","Graphics Processing Unit","Global Program Unit","Grid Processing Utility"],["General Processing Unit","Graphics Processing Unit","Global Program Unit","Grid Processing Utility"],["General Processing Unit","Graphics Processing Unit","Global Program Unit","Grid Processing Utility"],1),
  ],
  "medium": [
    _q3("Ki nòm pou yon pwogram malonèt ki ka koze dega?","Quel est le nom d'un programme malveillant?","What is a malicious program called?",["Lojisyèl","Malveyans","Antivirus","Firewall"],["Logiciel","Malware","Antivirus","Pare-feu"],["Software","Malware","Antivirus","Firewall"],1),
    _q3("Ki siyifikasyon 'API'?","Que signifie 'API'?","What does 'API' stand for?",["Application Program Interface","Advanced Program Integrator","Automated Process Interface","Application Protocol Integration"],["Application Program Interface","Advanced Program Integrator","Automated Process Interface","Application Protocol Integration"],["Application Program Interface","Advanced Program Integrator","Automated Process Interface","Application Protocol Integration"],0),
    _q3("Ki lang yo itilize pou Android ofisyèlman?","Quel langage est officiellement utilisé pour Android?","Which language is officially used for Android?",["Swift","Kotlin/Java","C#","Python"],["Swift","Kotlin/Java","C#","Python"],["Swift","Kotlin/Java","C#","Python"],1),
    _q3("Ki sistèm fichye Windows itilize?","Quel système de fichiers Windows utilise-t-il?","Which file system does Windows use?",["ext4","NTFS","APFS","FAT16"],["ext4","NTFS","APFS","FAT16"],["ext4","NTFS","APFS","FAT16"],1),
    _q3("Ki konpayi ki kreye Linux?","Quelle personne a créé Linux?","Who created Linux?",["Bill Gates","Steve Jobs","Linus Torvalds","Dennis Ritchie"],["Bill Gates","Steve Jobs","Linus Torvalds","Dennis Ritchie"],["Bill Gates","Steve Jobs","Linus Torvalds","Dennis Ritchie"],2),
    _q3("Ki siyifikasyon 'VPN'?","Que signifie 'VPN'?","What does 'VPN' stand for?",["Virtual Private Network","Very Private Node","Virtual Public Network","Verified Private Node"],["Virtual Private Network","Very Private Node","Virtual Public Network","Verified Private Node"],["Virtual Private Network","Very Private Node","Virtual Public Network","Verified Private Node"],0),
    _q3("Ki modèl AI OpenAI ki pi popilè?","Quel modèle IA d'OpenAI est le plus populaire?","Which OpenAI AI model is most popular?",["BERT","GPT","DALL-E","Whisper"],["BERT","GPT","DALL-E","Whisper"],["BERT","GPT","DALL-E","Whisper"],1),
    _q3("Ki baz done ki pi popilè nan mond lan?","Quelle base de données est la plus populaire au monde?","Which database is most popular worldwide?",["MongoDB","PostgreSQL","MySQL","SQLite"],["MongoDB","PostgreSQL","MySQL","SQLite"],["MongoDB","PostgreSQL","MySQL","SQLite"],2),
    _q3("Ki teknik yo itilize pou pwoteje done sou entènèt?","Quelle technique protège les données sur internet?","Which technique protects data on the internet?",["Komprèsyon","Chifrisman","Bakup","Indeksasyon"],["Compression","Chiffrement","Sauvegarde","Indexation"],["Compression","Encryption","Backup","Indexing"],1),
    _q3("Ki siyifikasyon 'SSD'?","Que signifie 'SSD'?","What does 'SSD' stand for?",["Super Speed Drive","Solid State Drive","System Storage Device","Secure Storage Disk"],["Super Speed Drive","Solid State Drive","System Storage Device","Secure Storage Disk"],["Super Speed Drive","Solid State Drive","System Storage Device","Secure Storage Disk"],1),
    _q3("Ki lang pwogramason ki pi popilè pou done syans?","Quel langage de programmation est le plus populaire pour la science des données?","Which programming language is most popular for data science?",["Java","C++","Python","Ruby"],["Java","C++","Python","Ruby"],["Java","C++","Python","Ruby"],2),
    _q3("Ki pwotokòl yo itilize pou transfè fichye?","Quel protocole est utilisé pour le transfert de fichiers?","Which protocol is used for file transfer?",["HTTP","SMTP","FTP","DNS"],["HTTP","SMTP","FTP","DNS"],["HTTP","SMTP","FTP","DNS"],2),
    _q3("Ki siyifikasyon 'HTML'?","Que signifie 'HTML'?","What does 'HTML' stand for?",["HyperText Markup Language","High Tech Modern Language","HyperText Modern Links","High Transfer Markup Language"],["HyperText Markup Language","High Tech Modern Language","HyperText Modern Links","High Transfer Markup Language"],["HyperText Markup Language","High Tech Modern Language","HyperText Modern Links","High Transfer Markup Language"],0),
    _q3("Ki konpayi ki kreye Java?","Quelle entreprise a créé Java?","Which company created Java?",["Microsoft","Apple","Sun Microsystems","IBM"],["Microsoft","Apple","Sun Microsystems","IBM"],["Microsoft","Apple","Sun Microsystems","IBM"],2),
    _q3("Ki tip rezò ki konekte òdinatè nan menm batiman?","Quel type de réseau connecte des ordinateurs dans un même bâtiment?","Which network type connects computers in the same building?",["WAN","MAN","LAN","PAN"],["WAN","MAN","LAN","PAN"],["WAN","MAN","LAN","PAN"],2),
    _q3("Ki siyifikasyon 'IoT'?","Que signifie 'IoT'?","What does 'IoT' stand for?",["Internet of Technology","Internet of Things","Integrated Online Technology","Intelligent Object Transfer"],["Internet of Technology","Internet des objets","Integrated Online Technology","Intelligent Object Transfer"],["Internet of Technology","Internet of Things","Integrated Online Technology","Intelligent Object Transfer"],1),
    _q3("Ki lang yo itilize pou iOS app?","Quel langage est utilisé pour les apps iOS?","Which language is used for iOS apps?",["Java","Kotlin","Swift","C#"],["Java","Kotlin","Swift","C#"],["Java","Kotlin","Swift","C#"],2),
    _q3("Ki siyifikasyon 'URL'?","Que signifie 'URL'?","What does 'URL' stand for?",["Universal Resource Link","Uniform Resource Locator","United Reference Location","Universal Record Linker"],["Universal Resource Link","Uniform Resource Locator","United Reference Location","Universal Record Linker"],["Universal Resource Link","Uniform Resource Locator","United Reference Location","Universal Record Linker"],1),
    _q3("Ki moun ki te envante touche web la?","Qui a inventé le World Wide Web?","Who invented the World Wide Web?",["Steve Jobs","Bill Gates","Tim Berners-Lee","Mark Zuckerberg"],["Steve Jobs","Bill Gates","Tim Berners-Lee","Mark Zuckerberg"],["Steve Jobs","Bill Gates","Tim Berners-Lee","Mark Zuckerberg"],2),
    _q3("Ki siyifikasyon 'OS'?","Que signifie 'OS'?","What does 'OS' stand for?",["Online Service","Operating System","Output Storage","Optical Scanner"],["Online Service","Système d'exploitation","Output Storage","Optical Scanner"],["Online Service","Operating System","Output Storage","Optical Scanner"],1),
  ],
  "hard": [
    _q3("Ki siyifikasyon 'TCP/IP'?","Que signifie 'TCP/IP'?","What does 'TCP/IP' stand for?",["Transfer Control Protocol/Internet Protocol","Transmission Control Protocol/Internet Protocol","Transfer Computing Protocol/Integrated Protocol","Terminal Control Protocol/Internet Protocol"],["Transfer Control Protocol/Internet Protocol","Transmission Control Protocol/Internet Protocol","Transfer Computing Protocol/Integrated Protocol","Terminal Control Protocol/Internet Protocol"],["Transfer Control Protocol/Internet Protocol","Transmission Control Protocol/Internet Protocol","Transfer Computing Protocol/Integrated Protocol","Terminal Control Protocol/Internet Protocol"],1),
    _q3("Ki kompleksite Big-O pou rechèch binè?","Quelle est la complexité Big-O d'une recherche binaire?","What is the Big-O complexity of binary search?",["O(n)","O(log n)","O(n²)","O(1)"],["O(n)","O(log n)","O(n²)","O(1)"],["O(n)","O(log n)","O(n²)","O(1)"],1),
    _q3("Ki diferans ant pwogrès senkwon ak asenkwon?","Quelle est la différence entre processus synchrone et asynchrone?","What is the difference between synchronous and asynchronous processes?",["Youn pi rapid","Senkwon tann, asenkwon pa tann","Youn manje plis mémwè","Pa gen diferans"],["L'un est plus rapide","Synchrone attend, asynchrone n'attend pas","L'un consomme plus de mémoire","Pas de différence"],["One is faster","Synchronous waits, asynchronous doesn't","One uses more memory","No difference"],1),
    _q3("Ki konsèp OOP ki kache detay enfòmasyon?","Quel concept OOP cache les détails d'implémentation?","Which OOP concept hides implementation details?",["Eritaj","Polimofism","Enkapsulasyon","Absiraksyon"],["Héritage","Polymorphisme","Encapsulation","Abstraction"],["Inheritance","Polymorphism","Encapsulation","Abstraction"],2),
    _q3("Ki nòm pou yon atak kote yon moun kaptire konvèsasyon?","Quel est le nom d'une attaque où quelqu'un intercepte une conversation?","What is an attack where someone intercepts communication called?",["Phishing","Man-in-the-middle","DDoS","SQL injection"],["Phishing","Man-in-the-middle","DDoS","Injection SQL"],["Phishing","Man-in-the-middle","DDoS","SQL injection"],1),
    _q3("Ki diferans ant SQL ak NoSQL?","Quelle est la différence entre SQL et NoSQL?","What is the difference between SQL and NoSQL?",["SQL pi rapid","SQL relasyon, NoSQL pa relasyon","NoSQL pi vye","Pa gen diferans"],["SQL plus rapide","SQL relationnel, NoSQL non-relationnel","NoSQL plus ancien","Pas de différence"],["SQL is faster","SQL relational, NoSQL non-relational","NoSQL is older","No difference"],1),
    _q3("Ki nòm pou algoritm ki soti nan netwè neyiral biyolojik?","Quel est le nom des algorithmes inspirés des réseaux neuronaux biologiques?","What are algorithms inspired by biological neural networks called?",["Algoritm jenetik","Rezo neyiral artifisyèl","Aleatwa fò","Rechèch lokal"],["Algorithmes génétiques","Réseaux de neurones artificiels","Force brute","Recherche locale"],["Genetic algorithms","Artificial neural networks","Brute force","Local search"],1),
    _q3("Ki nòm pou metòd devlopman lojisyèl ki itilize sprint?","Quel est le nom de la méthode de développement logiciel utilisant des sprints?","What is the software development method using sprints called?",["Waterfall","Agile/Scrum","DevOps","Lean"],["Cascade","Agile/Scrum","DevOps","Lean"],["Waterfall","Agile/Scrum","DevOps","Lean"],1),
    _q3("Ki siyifikasyon 'HTTPS'?","Que signifie 'HTTPS'?","What does 'HTTPS' stand for?",["HyperText Transfer Protocol Secured","HyperText Transfer Protocol Secure","High Transfer Protocol Secured","HyperText Transport Protocol Secure"],["HyperText Transfer Protocol Sécurisé","HyperText Transfer Protocol Secure","High Transfer Protocol Sécurisé","HyperText Transport Protocol Secure"],["HyperText Transfer Protocol Secured","HyperText Transfer Protocol Secure","High Transfer Protocol Secured","HyperText Transport Protocol Secure"],1),
    _q3("Ki nòm pou teknik ki pèmèt yon òdinatè vityèl imite yon plizyè?","Quel est le nom de la technique permettant à un ordinateur d'émuler plusieurs?","What is the technique allowing one computer to emulate multiple machines called?",["Kontènerizasyon","Vityalizasyon","Kloud konpitinng","Distribisyon"],["Conteneurisation","Virtualisation","Cloud computing","Distribution"],["Containerization","Virtualization","Cloud computing","Distribution"],1),
    _q3("Ki diferans ant stack ak queue?","Quelle est la différence entre une pile et une file?","What is the difference between a stack and a queue?",["Stack FIFO, Queue LIFO","Stack LIFO, Queue FIFO","Menm bagay","Stack plis rapid"],["Pile FIFO, File LIFO","Pile LIFO, File FIFO","Même chose","Pile plus rapide"],["Stack FIFO, Queue LIFO","Stack LIFO, Queue FIFO","Same thing","Stack is faster"],1),
    _q3("Ki nòm pou yon atak kote yo inonde yon sèvè ak demann?","Quel est le nom d'une attaque qui inonde un serveur de requêtes?","What is an attack that floods a server with requests called?",["Phishing","SQL injection","DDoS","Man-in-the-middle"],["Phishing","Injection SQL","DDoS","Man-in-the-middle"],["Phishing","SQL injection","DDoS","Man-in-the-middle"],2),
    _q3("Ki siyifikasyon 'REST' nan devlopman web?","Que signifie 'REST' dans le développement web?","What does 'REST' mean in web development?",["Real-time Exchange Standard Technology","Representational State Transfer","Remote Execution System Technology","Reliable Exchange Service Transfer"],["Real-time Exchange Standard Technology","Representational State Transfer","Remote Execution System Technology","Reliable Exchange Service Transfer"],["Real-time Exchange Standard Technology","Representational State Transfer","Remote Execution System Technology","Reliable Exchange Service Transfer"],1),
    _q3("Ki nòm pou konsèp nan blockchain kote chak blòk konekte ak anvan?","Quel est le concept de blockchain où chaque bloc est lié au précédent?","What is the blockchain concept where each block links to the previous?",["Mining","Hachaj","Chèn blòk","Konsensus"],["Mining","Hachage","Chaîne de blocs","Consensus"],["Mining","Hashing","Chain of blocks","Consensus"],1),
    _q3("Ki siyifikasyon 'CI/CD'?","Que signifie 'CI/CD'?","What does 'CI/CD' stand for?",["Code Integration/Code Delivery","Continuous Integration/Continuous Delivery","Coded Interface/Coded Deployment","Control Integration/Control Delivery"],["Code Integration/Code Delivery","Intégration Continue/Livraison Continue","Coded Interface/Coded Deployment","Control Integration/Control Delivery"],["Code Integration/Code Delivery","Continuous Integration/Continuous Delivery","Coded Interface/Coded Deployment","Control Integration/Control Delivery"],1),
    _q3("Ki diferans ant kriptografi simetrik ak asimetrik?","Quelle est la différence entre cryptographie symétrique et asymétrique?","What is the difference between symmetric and asymmetric cryptography?",["Vitès","Simetrik 1 kle, asimetrik 2 kle","Sekirite","Tout diferan"],["Vitesse","Symétrique 1 clé, asymétrique 2 clés","Sécurité","Tout différent"],["Speed","Symmetric 1 key, asymmetric 2 keys","Security","All different"],1),
    _q3("Ki konsèp pwogramason kote yon fonksyon rele tèt li?","Quel concept de programmation où une fonction s'appelle elle-même?","Which programming concept involves a function calling itself?",["Itèrasyon","Rekursyon","Enkapsulasyon","Eritaj"],["Itération","Récursion","Encapsulation","Héritage"],["Iteration","Recursion","Encapsulation","Inheritance"],1),
    _q3("Ki siyifikasyon 'SSH'?","Que signifie 'SSH'?","What does 'SSH' stand for?",["Secure Shell","Super Safe Host","Secured System Hosting","Standard Shell Host"],["Secure Shell","Super Safe Host","Secured System Hosting","Standard Shell Host"],["Secure Shell","Super Safe Host","Secured System Hosting","Standard Shell Host"],0),
    _q3("Ki nòm pou travay yon modèl AI sou done nouvo?","Quel est le nom de l'inférence d'un modèle IA sur de nouvelles données?","What is running an AI model on new data called?",["Fòmasyon","Eferans","Evaliasyon","Validasyon"],["Entraînement","Inférence","Évaluation","Validation"],["Training","Inference","Evaluation","Validation"],1),
    _q3("Ki diferans ant HTTP ak HTTPS?","Quelle est la différence entre HTTP et HTTPS?","What is the difference between HTTP and HTTPS?",["Vitès","HTTPS sekirize, HTTP pa sekirize","Vilèn koulè","Pa gen diferans"],["Vitesse","HTTPS sécurisé, HTTP non sécurisé","Design","Pas de différence"],["Speed","HTTPS is secure, HTTP is not","Color","No difference"],1),
  ],
}

# ── DB HELPERS ────────────────────────────────────────────────────────────────
def get_db():
    url = DATABASE_URL
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS scores (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL,
        category TEXT NOT NULL, difficulty TEXT NOT NULL, lang TEXT DEFAULT 'ht',
        correct INTEGER NOT NULL, wrong INTEGER NOT NULL,
        time_elapsed INTEGER NOT NULL, played_at TEXT NOT NULL)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY, category TEXT NOT NULL, difficulty TEXT NOT NULL,
        lang TEXT DEFAULT 'ht', name TEXT NOT NULL, q_indices TEXT NOT NULL,
        current INTEGER DEFAULT 0, score INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0, wrong INTEGER DEFAULT 0,
        created_at TEXT NOT NULL)''')
    conn.commit(); cur.close(); conn.close()

def make_token():
    return hashlib.sha256(os.urandom(32)).hexdigest()[:32]

def strip_ans(q, lang='ht'):
    qk = f'q_{lang}' if f'q_{lang}' in q else 'q_ht'
    ok = f'opts_{lang}' if f'opts_{lang}' in q else 'opts_ht'
    return {"q": q[qk], "opts": q[ok]}

# ── ROUTES ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    data = request.get_json() or {}
    cat  = data.get('category','')
    diff = data.get('difficulty','easy')
    lang = data.get('lang','ht')
    name = data.get('name','').strip()[:30]

    if not name:
        return jsonify({'error':'Non obligatwa'}), 400
    if cat not in QUESTIONS or diff not in QUESTIONS.get(cat,{}):
        return jsonify({'error':'Kategori invalid'}), 400

    pool    = QUESTIONS[cat][diff]
    # Chak jwè jwenn kesyon diferan — shuffle epi chwazi 20 (oswa tout si mwens de 20)
    indices = list(range(len(pool)))
    random.shuffle(indices)
    indices = indices[:min(20, len(pool))]
    token   = make_token()

    conn = get_db(); cur = conn.cursor()
    cur.execute('''INSERT INTO sessions
        (token,category,difficulty,lang,name,q_indices,current,score,correct,wrong,created_at)
        VALUES(%s,%s,%s,%s,%s,%s,0,0,0,0,%s)''',
        (token,cat,diff,lang,name,','.join(map(str,indices)),datetime.utcnow().isoformat()))
    conn.commit(); cur.close(); conn.close()

    return jsonify({
        'token': token, 'total': len(indices),
        'question': strip_ans(pool[indices[0]], lang), 'q_num': 1
    })

@app.route('/api/answer', methods=['POST'])
def submit_answer():
    data  = request.get_json() or {}
    token = data.get('token','')
    ans_i = data.get('answer')
    timed = data.get('timed_out', False)  # Si timer fini

    conn = get_db(); cur = conn.cursor()
    cur.execute('SELECT * FROM sessions WHERE token=%s',(token,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({'error':'Sesyon invalid'}), 400

    cat,diff,lang = row['category'], row['difficulty'], row.get('lang','ht')
    indices   = list(map(int, row['q_indices'].split(',')))
    cur_i     = row['current']
    score     = row['score']
    correct_c = row['correct']
    wrong_c   = row['wrong']
    total     = len(indices)

    pool  = QUESTIONS[cat][diff]
    cur_q = pool[indices[cur_i]]
    correct = cur_q['ans']
    ok    = (not timed) and (ans_i == correct)
    pts   = {'hard':3,'medium':2,'easy':1}.get(diff,1) if ok else 0

    score += pts
    if ok: correct_c += 1
    else:  wrong_c   += 1
    nxt = cur_i + 1

    cur.execute('UPDATE sessions SET current=%s,score=%s,correct=%s,wrong=%s WHERE token=%s',
                (nxt,score,correct_c,wrong_c,token))
    conn.commit(); cur.close(); conn.close()

    result = {
        'correct': ok, 'correct_answer': correct,
        'correct_text': cur_q[f'opts_{lang}' if f'opts_{lang}' in cur_q else 'opts_ht'][correct],
        'pts': pts, 'score': score,
        'done': nxt >= total, 'q_num': nxt+1, 'total': total
    }
    if nxt < total:
        result['question'] = strip_ans(pool[indices[nxt]], lang)
    return jsonify(result)

@app.route('/api/finish', methods=['POST'])
def finish_game():
    data    = request.get_json() or {}
    token   = data.get('token','')
    elapsed = int(data.get('time_elapsed', 0))

    conn = get_db(); cur = conn.cursor()
    cur.execute('SELECT * FROM sessions WHERE token=%s',(token,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({'error':'Sesyon invalid'}), 400

    cur.execute('''INSERT INTO scores
        (name,score,total,category,difficulty,lang,correct,wrong,time_elapsed,played_at)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        (row['name'], row['score'],
         len(row['q_indices'].split(',')),
         row['category'], row['difficulty'], row.get('lang','ht'),
         row['correct'], row['wrong'],
         elapsed, datetime.utcnow()))
    cur.execute('DELETE FROM sessions WHERE token=%s',(token,))
    conn.commit()
    final = row['score']; cur.close(); conn.close()
    return jsonify({'ok':True,'final_score':final})

@app.route('/api/leaderboard')
def leaderboard():
    """Leaderboard global — tout tan."""
    conn = get_db(); cur = conn.cursor()
    cur.execute('''
        SELECT name, score, total, category, difficulty, played_at
        FROM scores
        ORDER BY score DESC, correct DESC, time_elapsed ASC
        LIMIT 20
    ''')
    rows = cur.fetchall(); cur.close(); conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/leaderboard/monthly')
def leaderboard_monthly():
    """
    Leaderboard mansyèl — sèlman pi bon skor pa jwè pou mwa sa a.
    Kòmanse 1ye chak mwa, remete a zewo vizuèlman (done pa efase).
    """
    conn = get_db(); cur = conn.cursor()
    cur.execute('''
        SELECT name,
               MAX(score) AS score,
               MAX(correct) AS correct,
               MAX(total) AS total,
               (array_agg(category ORDER BY score DESC))[1] AS category,
               (array_agg(difficulty ORDER BY score DESC))[1] AS difficulty,
               MAX(played_at) AS played_at
        FROM scores
        WHERE played_at >= DATE_TRUNC('month', NOW())
          AND played_at <  DATE_TRUNC('month', NOW()) + INTERVAL '1 month'
        GROUP BY name
        ORDER BY MAX(score) DESC, MAX(correct) DESC
        LIMIT 10
    ''')
    rows = cur.fetchall()
    # Re-trier pa skor
    data = sorted([dict(r) for r in rows], key=lambda x: -x['score'])
    cur.close(); conn.close()
    return jsonify(data[:10])


@app.route('/api/leaderboard/monthly/winner')
def monthly_winner():
    """Retounen lidè mwa a + konbyen jou ki rete nan mwa a."""
    conn = get_db(); cur = conn.cursor()
    cur.execute('''
        SELECT name, MAX(score) AS score, COUNT(*) AS games_played
        FROM scores
        WHERE played_at >= DATE_TRUNC('month', NOW())
          AND played_at <  DATE_TRUNC('month', NOW()) + INTERVAL '1 month'
        GROUP BY name
        ORDER BY MAX(score) DESC
        LIMIT 1
    ''')
    row = cur.fetchone()
    # Kalkile jou ki rete nan mwa a
    cur.execute("SELECT EXTRACT(DAY FROM (DATE_TRUNC('month', NOW()) + INTERVAL '1 month' - NOW())) AS days_left")
    days_row = cur.fetchone()
    cur.close(); conn.close()

    days_left = 0
    if days_row and days_row['days_left'] is not None:
        try:
            days_left = int(days_row['days_left'])
        except:
            days_left = 0

    return jsonify({
        'winner': dict(row) if row else None,
        'days_left': days_left
    })


@app.route('/service-worker.js')
def service_worker():
    """Sèvè service worker depi rasin pou PWA fonksyone."""
    from flask import send_from_directory
    return send_from_directory('static', 'service-worker.js',
                               mimetype='application/javascript')


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health():
    """Health check endpoint for Render."""
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute('SELECT 1'); cur.close(); conn.close()
        return jsonify({'status': 'ok', 'app': 'SeptaQuiz', 'brand': 'Septech'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
