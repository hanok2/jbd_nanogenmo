import os, sys
import string
import random
import pickle

import markov

# A Culture Generates names for people and places, and has character
# attributes.

# Funny names from markov cities:
# Funkstown 'N' Country Estate
# Snoverdale-By-The-Lake
# Musselwhitemarshville Manors
# Umbers Locational Highgate Of Bachmann
# Smileyview
# Bjorkdale Hill
# Poignant Acre

# From https://www.maxmind.com/en/free-world-cities-database
CITIES_FILE = "srcdata/worldcitiespop.txt"

cultures = {}

class Culture(object):

    def __init__(self):

        self.placeNameGenerator = None
        self.personNameGenerator = None
        self.ranks = [ ('Emperor', 'Emperess'), # Ruler of continent
                       ('King', 'Queen'),       # Ruler of country
                       ('Duke', 'Duchess'),     # Ruler of province

                       [('Marquess','Marchioness'), # Other misc nobility
                        ('Earl', 'Countess'),
                        ('Viscount', 'Viscountess'),
                        ('Baron', 'Baroness') ] ]

    def genPlaceName(self):

        city = self.placeNameGenerator.genString()

        # some sanity checks
        parts = city.split( ' ' )

        didFilter = False
        filteredParts = []
        for part in parts:
            if len(part) > 1:
                filteredParts.append( part )
                didFilter = True
        if (didFilter):
            parts = filteredParts
            city = ' '.join(filteredParts)

        if (len(parts) > 2):
            city = ' '.join(parts[:2])

        return city

    def genContinentName(self):
        """
         Generates a place name, but makes sure it's short and a single word so you
         don't get stuff like 'Clebe Farm'
        """
        while 1:
            candidate = self.genPlaceName()

            parts = string.split( candidate )
            if (len(parts)==1) and len(candidate) < 10:
                return candidate

# Block some frequent, modern words, or weird data in the src data
BANNED_WORDS = ['mobile home', 'trailer', 'condominium', 'subdivision', 'addition', '9zenic',
                '((', '))', '?' ]

def filterCities( countrycodes ):

    result = set()
    count = 0
    countryCodes = {}
    for line in open(CITIES_FILE):
        lsplit = string.split(string.strip(line),',')
        cc = lsplit[0]
        countryCodes[cc] = countryCodes.get(cc, 0) + 1

        if (cc in countrycodes):
            city = lsplit[1]
            if not city in result:

                banned = False
                for bannedword in BANNED_WORDS:
                    if city.find( bannedword ) != -1:
                        banned = True

                if not banned:
                    result.add( city )

        count += 1

    result = list(result)
    result.sort()
    return result

def setupCulture( ident, countrycodes, srccount, depth, ranks=None ):


    print "Setup Culture : ", ident, "-"*10
    cachedCulture = os.path.join( 'data', ident+'_culture.p')

    if os.path.exists( cachedCulture ):
        print "Reading cached culture ", cachedCulture
        result = pickle.load( open(cachedCulture, 'rb'))
    else:
        placeNameSrcList = os.path.join( 'data', ident+'_cities.txt' )

        if not os.path.exists( placeNameSrcList ):
            cities = filterCities( countrycodes )

            fp = open ( placeNameSrcList, "wt" )
            for city in cities:
                fp.write( city+'\n' )
            fp.close()
        else:
            # Read cached filtered names
            cities = []
            for line in open( placeNameSrcList ):
                cities.append( string.strip(line))

        print "Setup Culture", ident, len(cities), "cities "

        # Make a city generator
        gen = markov.MarkovGenerator( depth=depth )

        random.shuffle(cities)

        trainCities = cities[:srccount]
        for w in trainCities:
            wseq = list(w)
            gen.trainOne( wseq )

        gen.trainFinish()

        result = Culture()
        result.placeNameGenerator = gen

        pickle.dump( result, open(cachedCulture, 'wb' ))

    # Rank
    if ranks:
        result.ranks = ranks

    # Test cities
    targetNum = 20
    uniqCount = 0
    for i in range(targetNum):
        #city = result.genPlaceName()
        city = result.genContinentName()
        print city.title()

    cultures[ident] = result

    return result

def setupCultures():

    newWorldRanks =[ ('Secretary-General', 'Secretary-General'),
                       ('President', 'President'),
                       ('Governer', 'Governer'),

                       [('Mayor','Mayor'), # Other misc nobility
                        ('Representitive', 'Representitive'),
                        ('Congressman', 'Congresswoman') ] ]

    setupCulture( "newworld", [ 'us', 'ca'], 50000, 5, ranks=newWorldRanks )

    setupCulture( "oldworld", [ 'gb', 'ie'], 50000, 5 ) # Old world uses default ranks

    # Magical, quasi-religious ranks
    islandRanks = [ ('God Priest', 'Goddess'),
                       ('Archdruid', 'Archdruidess'),
                       ('High Priest', 'High Priestess'),

                       [('Bishop','Mayor'), # Other misc nobility
                        ('Seer', 'Devoted'),
                        ('Watcher', 'Watcher') ] ]
    setupCulture( "island", [ 'ba', 'aw', 'ai', 'bb', 'bm', 'vg', 'ky', 'ht', 'jm', 'kn', 'sc', 'tt', 'tm', 'vi' ],
                   10000, 5 )
    setupCulture( "spanish", [ 'es', 'mx', 'cr', 'br'], 50000, 5 )
    setupCulture( "india", [ 'in' ], 50000, 5 )
    setupCulture( "nordic", [ 'fi', 'se', 'no' ], 50000, 5 )



if __name__=='__main__':

    setupCultures()