import os, sys
import random

import tracery
from tracery.modifiers import base_english

from pulpmill import world, scene, storygen, character, utils


title_rules = {
    'origin' : ['#a_conflict# #preposition# #desc_context#', '#a_and_b#',
                'the #desc_context#'],

    'a_and_b' : [ 'the #context# and the #desc_context#', 'of #context# and #context#',
                  '#context# and #context#'],

    'conflict' : ['war', 'battle', '#weather#', 'shadow', 'king', 'lord', 'god',
                  'trials', 'time', 'age', 'host' ],
    'a_conflict' : ['#conflict#','the #conflict#', 'a #conflict#'],
    'preposition' : ['of the', 'above the', 'through', 'amidst', 'among', 'amongst',
                     'beyond', 'against', 'from the', 'between'],
    'desc_context' : ['#context#', '#awesome# #context#'],
    'context' : ['rings', 'dragons', 'swords', 'roses', 'kingdoms',
                 'wizards', 'sorcerers', 'curses', 'spells', '#season#',
                 '#barren# lands', 'dungeons', 'fortresses', 'enchantresses',
                 'queens', 'kings'],

    'awesome' : ['lost', 'mighty', 'forgotten', 'purple', 'heavenly', '#number#',
                 'undead', 'unholy', 'cursed', 'hidden', 'false',
                 'royal', 'promised', 'forgotten', '#season#', 'golden' ],
    'number' : ['two', 'three', 'seven', 'nine', 'hundred'],
    'weather' : ['storm', 'thunder', 'lightning'],
    'season' : ['spring', 'summer', 'winter', 'autumn', 'night', 'dawn' ],
    'barren' : ['broken', 'barren', 'burning', 'auburn']
}


class Novel(object):

    def __init__(self, cultures):
        self.cultures = cultures
        self.scenes = []

    def generate(self):

        self.sg = storygen.StoryGen()

        self.map = world.World( self.cultures, self.sg )
        self.map.buildMap()

        # Main character
        firstNode = self.map.storyPath[0]
        self.protag = character.Character( firstNode )
        self.protag.tag = 'protag'

        self.party = []

        commonRules = self.sg.getCommonRules( firstNode )
        # print "Common Rules:"
        # kk = commonRules.keys()
        # kk.sort()
        # for k in kk:
        #     print k, "-> ", commonRules[k]
        #
        # print "Season is ", self.sg.season

        # sceneRules = {
        #     'origin' : '#weather_sentence.capitalize#'
        # }
        # sceneRules.update( commonRules )

        # grammar = tracery.Grammar( sceneRules )
        # grammar.add_modifiers( base_english )
        # for i in range(10):
        #     print str(i+1)+".", grammar.flatten( "#origin#")
        #
        # sys.exit(1)



        self.scenes += scene.sceneNormalLife( firstNode, self.protag )

        if (utils.randomChance(0.5)):
            self.scenes += scene.scenePlaceDesc( firstNode, self.protag )

        # Scramble the prologue scenes
        random.shuffle( self.scenes )

        self.scenes += scene.sceneIncitingIncident( firstNode, self.protag )

        # After this is the first point we can add new characters
        addCharIndex = len(self.scenes)

        # Walk the story path to generate scenes
        lastNode = None
        for item in self.map.storyPath:
            if isinstance(item,world.TerrainNode):

                if item.city:
                    self.scenes += scene.sceneCity( item, self.protag )
                    lastNode = item

                else:
                    # TODO encounter nodes
                    pass

            elif isinstance(item,world.TerrainArc):

                if item.arcType == world.TerrainArc_SEA:
                    self.scenes += scene.sceneSeaVoyage(  lastNode, item )


        self.currParty = [ self.protag ]

        # Add/Remove characters from the party
        addCooldown = 0
        maxChars = 5
        while addCharIndex < len(self.scenes):
            currScene = self.scenes[addCharIndex]

            if (addCooldown==0 and utils.randomChance(0.5) and
                    currScene.node and currScene.node.city and
                        len(self.currParty)<maxChars):
                addCooldown = 3

                print "currScene is ", currScene.desc, currScene.chapterTitle
                addCharScenes = scene.sceneAddCharacter( currScene.node, self.map )

                self.scenes[addCharIndex+1:addCharIndex+1] = addCharScenes

                for c in addCharScenes:
                    self.currParty += c.newChars

            # if chatCooldown==0 and len(self.currParty)>=2 and utils.randomChance(0.9):
            #
            #     convoScenes = scene.sceneDialogueFiller( currScene.node )
            #     self.scenes[addCharIndex+1:addCharIndex+1] = convoScenes
            #
            #     chatCooldown = 4


            addCharIndex += 1
            if addCooldown > 0:
                addCooldown -= 1



        # TODO: Here add fight scenes and run battle simulations

        # Update party track
        party = [ self.protag ]
        for scn in self.scenes:
            print "SCENE: %s -- %d in party, %d new" % ( scn.desc, len(party), len(scn.newChars) )
            scn.party = party[:]
            party += scn.newChars


        # Add a bunch of filler scenes
        chatCooldown = 0
        fillerSceneIndex = 0
        while fillerSceneIndex < len(self.scenes):
            currScene = self.scenes[fillerSceneIndex]

            if chatCooldown==0 and len(currScene.party)>=2 and utils.randomChance(0.9):
                convoScenes = scene.sceneDialogueFiller( currScene.node )

                for scn in convoScenes:
                    scn.node = currScene.node
                    scn.party = currScene.party

                self.scenes[fillerSceneIndex+1:fillerSceneIndex+1] = convoScenes

                chatCooldown = 4

            fillerSceneIndex += 1
            if chatCooldown > 0:
                chatCooldown -= 1

        # Last, generate the title. Right now this is random but it would
        # be cool to use some info from the story
        self.title = self.genTitle()

        # Do some sanity checks
        for scn in self.scenes:
            if scn.node is None:
                print "SCENE MISSING NODE: ", scn, scn.desc, scn.chapterTitle, scn.party
                sys.exit(1)

    def dbgPrint(self):

        print "Novel: ", self.title
        print "Setting Info: "
        self.map.dbgPrint()

        print "---- PARTY ", len(self.currParty), "-----"
        for p in self.currParty:
            print "  ",p.name, "a", p.rpgClass.rpgClass, "from", p.hometown.name


        print "---- SCENES: -------"

        wordCountTot = 0
        for scn in self.scenes:
            scn.doGenerate( self.sg )
            wordCountTot += scn.wordCount

            print "-", scn.desc, "("+scn.chapterTitle, scn.wordCount, "words)"
            for pp in scn.storyText:
                print pp
                print



        wordCountAvg = 50000 / len(self.scenes)
        print "Total word count", wordCountTot
        print "For a 50K novel, each scene would need to be approx ", wordCountAvg, "words."

        print "--- Kingdoms ---"
        for k in self.map.kingdoms:
            print k.name, "   Popular Fruits:", k.fruits


    def genTitle(self):
        grammar = tracery.Grammar( title_rules )
        grammar.add_modifiers( base_english )
        title = grammar.flatten( "#origin#").title()

        return title