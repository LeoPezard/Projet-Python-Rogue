import copy
import math
import random
import tkinter as tk
from tkinter.simpledialog import askinteger
import tkinter.font as tkFont
from tkinter.messagebox import *


# exceptions
MAX_SIZE = 22  ## la taille de la matrice
PIX_SIZE = 30 ##la taille des images en pixel si besoin de redimensionner 
HP = 15
HPMAX = 15

def _find_getch():
   """Single char input, only works only on mac/linux/windows OS terminals"""
   try:
       import termios
   except ImportError:
       # Non-POSIX. Return msvcrt's (Windows') getch.
       import msvcrt
       return lambda: msvcrt.getch().decode('utf-8')
   # POSIX system. Create and return a getch that manipulates the tty.
   import sys, tty
   def _getch():
       fd = sys.stdin.fileno()
       old_settings = termios.tcgetattr(fd)
       try:
           tty.setraw(fd)
           ch = sys.stdin.read(1)
       finally:
           termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
       return ch
   return _getch

def sign(x):
    if x > 0:
        return 1
    return -1


class Coord(object):
    """Implementation of a map coordinate"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return '<' + str(self.x) + ',' + str(self.y) + '>'

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def distance(self, other):
        """Returns the distance between two coordinates."""
        d = self - other
        return math.sqrt(d.x * d.x + d.y * d.y)

    cos45 = 1 / math.sqrt(2)

    def direction(self, other):
        """Returns the direction between two coordinates."""
        d = self - other
        cos = d.x / self.distance(other)
        if cos > Coord.cos45:
            return Coord(-1, 0)
        elif cos < -Coord.cos45:
            return Coord(1, 0)
        elif d.y > 0:
            return Coord(0, -1)
        return Coord(0, 1)


class Element(object):
    """Base class for game elements. Have a name.
        Abstract class."""

    def __init__(self, name, abbrv=""):
        self.name = name
        if abbrv == "":
            abbrv = name[0]
        self.abbrv = abbrv

    def __repr__(self):
        return self.abbrv

    def description(self):
        """Description of the element"""
        return "<" + self.name + ">"

    def meet(self, hero):
        """Makes the hero meet an element. Not implemented. """
        raise NotImplementedError('Abstract Element')


class Creature(Element):
    """A creature that occupies the dungeon.
        Is an Element. Has hit points and strength."""

    def __init__(self, name, hp, abbrv="", strength=1, XPgagné=0):
        Element.__init__(self, name, abbrv)
        self.hp = hp
        self.strength = strength
        self.XPgagné= XPgagné

    def description(self):
        """Description of the creature"""
        return Element.description(self) + "(" + str(self.hp) + ")"

    def meet(self, other):
        """The creature is encountered by an other creature.
            The other one hits the creature. Return True if the creature is dead."""
        if other.name == 'Mario' and other.armure >0 :
           other.armure -= self.strength
        else :
           other.hp -= self.strength
           theGame().addMessage(other.name + " hits the " + self.description())
        
        if self.hp > 0:
            return False
        if other.name == "Mario" and self.abbrv == 'k':
           other.poison = True
           
           
           
        if other.name=="Mario" and self.hp<=0:
              other.XP+=self.XPgagné
              theGame().addMessage("You won "+ str(self.XPgagné)+ "XP")
              if other.XP>=(other.LEVEL*10):
                 other.strength+=2
                 other.hp=15+(other.LEVEL*5)
                 other.LEVEL+=1
                 other.XP = 0
                 other.hpmax=15+((other.LEVEL-1)*5)
                 theGame().addMessage("You upgrade to Level n°"+ str(other.LEVEL)+" !")
        return True
        


class Hero(Creature):
    """The hero of the game.
        Is a creature. Has an inventory of elements. """

    def __init__(self, name="Mario", hp=HP, abbrv="@", strength=2, XP = 0,
                 LEVEL= 1, hpmax = HPMAX, satiété = 20,satiétéMAX=20, armure = 0,
                 poison = False, magie = 20):
        Creature.__init__(self, name, hp, abbrv, strength)
        self._inventory = []
        self.XP = XP
        self.LEVEL = LEVEL
        self.hpmax = hpmax
        self.satiété = satiété
        self.satiétéMAX = satiétéMAX
        self.armure = armure
        self.poison = poison
        self.magie = magie
        
    def haskey(self):
       inv_abbrv = [e.abbrv for e in self._inventory]
       if 'K' in inv_abbrv:
          return True
       else:
          return False

         
    def description(self):
        """Description of the hero"""
        return Creature.description(self) + str(self._inventory)

    def fullDescription(self):
        """Complete description of the hero"""
        res = ''
        for e in self.__dict__:
            if e[0] != '_':
                res += '> ' + e + ' : ' + str(self.__dict__[e]) + '\n'
        res += '> INVENTORY : ' + str([x.name for x in self._inventory])
        return res

    def checkEquipment(self, o):
        """Check if o is an Equipment."""
        if not isinstance(o, Equipment):
            raise TypeError('Not a Equipment')
    def checkElement(self, o):
       if not isinstance(o, Element):
          raise TypeError('Not a Element')
    
          
    def take(self, elem):
        """The hero takes adds the equipment to its inventory"""
        self.checkEquipment(elem)
        if elem.abbrv == 'p' :
           if self.armure >0 :
              self.armure -= 2
           else :
              self.hp -=2
        elif len(self._inventory)==10:
           theGame().addMessage('Inventaire plein, appuyez sur "o"')

        else:
           self._inventory.append(elem)
               
    def use(self, elem):
        """Use a piece of equipment"""
        if elem is None:
            return
        self.checkEquipment(elem)
        if elem not in self._inventory:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        if elem.use(self):
            self._inventory.remove(elem)

class Equipment(Element):
    """A piece of equipment"""

    def __init__(self, name, abbrv="", usage=None):
        Element.__init__(self, name, abbrv)
        self.usage = usage

    def meet(self, hero):
        """Makes the hero meet an element. The hero takes the element."""
        hero.take(self)
        if self.abbrv == 'p':
           theGame().addMessage("You walk on a trap")
        if len(hero._inventory) == 10:
           pass
        else :
           theGame().addMessage("You pick up a " + self.name)

        return True

    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if self.usage is None:
            theGame().addMessage("The " + self.name + " is not usable")
            return False
        else:
            theGame().addMessage("The " + creature.name + " uses the " + self.name)
            return self.usage(self, creature)


      
class Stairs(Element):
    """ Strairs that goes down one floor. """

    def __init__(self):
        super().__init__("Stairs", 'E')

    def meet(self, hero):
        """Goes down"""
        theGame().buildFloor()
        if theGame()._hero.haskey():
           inv_abbrv = [e.abbrv for e in hero._inventory]
           kidx = inv_abbrv.index('K')
           hero._inventory.pop(kidx)
         
        theGame().addMessage("The " + hero.name + " goes down")
        repos= askyesno("Repos","Voulez-vous vous reposez ?")
        if repos:
           if hero.hp+5> hero.hpmax:
              hero.hp=hero.hpmax
           else :
              hero.hp +=5
              i = 0
              while i != 10:
                 Map().moveAllMonsters()
                 i+=1
        else:
            pass

class Tresor(Element):
   def __init__(self):
      super().__init__("Tresor","T")

   def meet(self,other):
      if other.name == 'Mario':
         if other.haskey() :
            other._inventory.append(random.choice(theGame().equipments_list))
            inv_abbrv = [e.abbrv for e in other._inventory]
            kidx = inv_abbrv.index('K')
            other._inventory.pop(kidx)
         else :
             theGame().addMessage("Trouver la clé permettant d'ouvrir le coffre au trésor")
            
         

class Room(object):
    """A rectangular room in the map"""

    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return "[" + str(self.c1) + ", " + str(self.c2) + "]"

    def __contains__(self, coord):
        return self.c1.x <= coord.x <= self.c2.x and self.c1.y <= coord.y <= self.c2.y

    def intersect(self, other):
        """Test if the room has an intersection with another room"""
        sc3 = Coord(self.c2.x, self.c1.y)
        sc4 = Coord(self.c1.x, self.c2.y)
        return self.c1 in other or self.c2 in other or sc3 in other or sc4 in other or other.c1 in self

    def center(self):
        """Returns the coordinates of the room center"""
        return Coord((self.c1.x + self.c2.x) // 2, (self.c1.y + self.c1.y) // 2)

    def randCoord(self):
        """A random coordinate inside the room"""
        return Coord(random.randint(self.c1.x, self.c2.x), random.randint(self.c1.y, self.c2.y))

    def randEmptyCoord(self, map):
        """A random coordinate inside the room which is free on the map."""
        c = self.randCoord()
        while map.get(c) != Map.ground or c == self.center():
            c = self.randCoord()
        return c

    def decorate(self, map):
        """Decorates the room by adding a random equipment and monster."""
        map.put(self.randEmptyCoord(map), theGame().randEquipment())
        map.put(self.randEmptyCoord(map), theGame().randMonster())


class Map(object):
    """A map of a game floor.
        Contains game elements."""

    ground = '.'  # A walkable ground cell
    dir = {'z': Coord(0, -1), 's': Coord(0, 1), 'd': Coord(1, 0), 'q': Coord(-1, 0)}  # four direction user keys
    empty = ' '  # A non walkable cell

    def __init__(self, size = MAX_SIZE, hero=None):
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []
        

        for i in range(size):
            self._mat.append([Map.empty] * size)
        if hero is None:
            hero = Hero()
        self._hero = hero
        self.generateRooms(7)
        self.reachAllRooms()
        self.put(self._rooms[0].center(), hero)
        for r in self._rooms:
            r.decorate(self)

    def addRoom(self, room):
        """Adds a room in the map."""
        self._roomsToReach.append(room)
        for y in range(room.c1.y, room.c2.y + 1):
            for x in range(room.c1.x, room.c2.x + 1):
                self._mat[y][x] = Map.ground

    def findRoom(self, coord):
        """If the coord belongs to a room, returns the room elsewhere returns None"""
        for r in self._roomsToReach:
            if coord in r:
                return r
        return None

    def intersectNone(self, room):
        """Tests if the room shall intersect any room already in the map."""
        for r in self._roomsToReach:
            if room.intersect(r):
                return False
        return True

    def dig(self, coord):
        """Puts a ground cell at the given coord.
            If the coord corresponds to a room, considers the room reached."""
        self._mat[coord.y][coord.x] = Map.ground
        r = self.findRoom(coord)
        if r:
            self._roomsToReach.remove(r)
            self._rooms.append(r)

    def corridor(self, cursor, end):
        """Digs a corridors from the coordinates cursor to the end, first vertically, then horizontally."""
        d = end - cursor
        self.dig(cursor)
        while cursor.y != end.y:
            cursor = cursor + Coord(0, sign(d.y))
            self.dig(cursor)
        while cursor.x != end.x:
            cursor = cursor + Coord(sign(d.x), 0)
            self.dig(cursor)

    def reach(self):
        """Makes more rooms reachable.
            Start from one random reached room, and dig a corridor to an unreached room."""
        roomA = random.choice(self._rooms)
        roomB = random.choice(self._roomsToReach)

        self.corridor(roomA.center(), roomB.center())

    def reachAllRooms(self):
        """Makes all rooms reachable.
            Start from the first room, repeats @reach until all rooms are reached."""
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach) > 0:
            self.reach()

    def randRoom(self):
        """A random room to be put on the map."""
        c1 = Coord(random.randint(0, len(self) - 3), random.randint(0, len(self) - 3))
        c2 = Coord(min(c1.x + random.randint(3, 8), len(self) - 1), min(c1.y + random.randint(3, 8), len(self) - 1))
        return Room(c1, c2)

    def generateRooms(self, n):
        """Generates n random rooms and adds them if non-intersecting."""
        for i in range(n):
            r = self.randRoom()
            if self.intersectNone(r):
                self.addRoom(r)

    def __len__(self):
        return len(self._mat)

    def __contains__(self, item):
        if isinstance(item, Coord):
            return 0 <= item.x < len(self) and 0 <= item.y < len(self)
        return item in self._elem

    def __repr__(self):
        s = ""
        for i in self._mat:
            for j in i:
                s += str(j)
            s += '\n'
        return s

    def checkCoord(self, c):
        """Check if the coordinates c is valid in the map."""
        if not isinstance(c, Coord):
            raise TypeError('Not a Coord') 
        if not c in self:
            raise IndexError('Out of map coord')

    def checkElement(self, o):
        """Check if o is an Element."""
        if not isinstance(o, Element):
            raise TypeError('Not a Element')

    def put(self, c, o):
        """Puts an element o on the cell c"""
        self.checkCoord(c)
        self.checkElement(o)
        if self._mat[c.y][c.x] != Map.ground:
            raise ValueError('Incorrect cell')
        if o in self._elem:
            raise KeyError('Already placed')
        self._mat[c.y][c.x] = o
        self._elem[o] = c

    def get(self, c):
        """Returns the object present on the cell c"""
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def pos(self, o):
        """Returns the coordinates of an element in the map """
        self.checkElement(o)
        return self._elem[o]

    def rm(self, c):
        """Removes the element at the coordinates c"""
        self.checkCoord(c)
        del self._elem[self._mat[c.y][c.x]]
        self._mat[c.y][c.x] = Map.ground

    def move(self, e, way):
        """Moves the element e in the direction way."""
        orig = self.pos(e)
        dest = orig + way
        if dest in self:
            if self.get(dest) == Map.ground:
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
                self.satiété()
                self.poison()
            elif self.get(dest) != Map.empty and self.get(dest).meet(e) and self.get(dest) != self._hero:
                self.rm(dest)
            

    def moveAllMonsters(self):
        """Moves all monsters in the map.
            If a monster is at distance lower than 6 from the hero, the monster advances."""
        h = self.pos(self._hero)
        for e in self._elem:
            c = self.pos(e)
            if isinstance(e, Creature) and e != self._hero and c.distance(h) < 6:
                d = c.direction(h)
                if self.get(c + d) in [Map.ground, self._hero]:
                    self.move(e, d)
                 
    def satiété(self):
       self._hero.satiété-=1/4
       if self._hero.satiété<=0:
          self._hero.hp -= 1
          
    def poison(self):
       if self._hero.poison :
          self._hero.hp -=1
       
   

def heal(creature):
    """Heal the creature"""
    creature.hp += 3
    return True
   
def regen(hero):
   "regénère le héro"
   hero.satiété=20
   theGame().addMessage("Your level of satiety is now full")
   return True

def teleport(creature, unique):
    """Teleport the creature"""
    r = random.choice(theGame()._floor._rooms)
    c = r.randEmptyCoord(theGame()._floor)    
    theGame()._floor.rm(theGame()._floor.pos(creature))
    theGame()._floor.put(c, creature)
    return unique


def teleportmagie(creature, unique):
   """Teleport the creature"""
   if creature.magie<=0:
       pass
   else:
      make_trial = True
      while make_trial :
         r = random.choice(theGame()._floor._rooms)
         c = r.randCoord()
         if theGame()._floor._mat[c.y][c.x] == Map.ground :
            make_trial = False
    
      theGame()._floor.rm(theGame()._floor.pos(creature))
      theGame()._floor.put(c, creature)
      creature.magie-=4
      return unique
   
   
def force(creature, delta):
   creature.strength += delta
   return True

def armure(hero):
   hero.armure = 10
   return True

def healmagie(hero):
   if hero.magie<=0 or hero.hp>hero.hpmax-2:
      pass
   else:
      hero.hp += 2
      hero.magie-=2
      return True
   
def magie(hero):
   if hero.magie+5>20:
      hero.magie=20
   else:
      hero.magie+=5
   
def stoppoison(hero):
   hero.poison = False
   return True


class Game(object):
    """ Class representing game state """

    """ available equipments """
   
    equipments = {0: [Equipment("up", "!", usage=lambda self, hero: heal(hero)), \
                      Equipment("armure", "A", usage = lambda self, hero : armure(hero)), \
                      Equipment("poulet", "P", usage = lambda self, hero : regen(hero))], \
                  1: [Equipment("Yoshi", "Y", usage=lambda self, hero: teleport(hero, True)), \
                      Equipment("plume", "pl", usage = lambda self, hero : magie(hero))], \
                  2: [Equipment("Champi", "?", usage = lambda self, hero : stoppoison(hero))],\
                  3: [Equipment("star", 'e', usage=lambda self, hero : armure(hero))], \
                  4: [Equipment("fire flower", 'F', usage = lambda self, hero: force(hero, 3))], \
                  5: [Equipment("ice flower", 'f', usage = lambda self, hero: force(hero, 2))], \
                  }
    equipments_list = [e for i in equipments.values() for e in i]
    
    """ available monsters """
    monsters = {0: [Creature("Gumba", 2, "G", XPgagné=1),
                    Equipment("Piege", 'p')],
                1: [Creature("Bomb", 1, 'k',strength = 1, XPgagné = 3),
                    Creature("Tchomp", 5, '%', strength=2, XPgagné = 4),
                    Creature("Boo",6,'b', strength=2, XPgagné = 5),
                    Creature("Donkey kong", 10, XPgagné = 7)],
                5: [Creature("Bowser", 2, strength=3, XPgagné = 10)]}

    """ available actions """
    _actions = {'z': lambda h: theGame()._floor.move(h, Coord(0, -1)), \
                'q': lambda h: theGame()._floor.move(h, Coord(-1, 0)), \
                's': lambda h: theGame()._floor.move(h, Coord(0, 1)), \
                'd': lambda h: theGame()._floor.move(h, Coord(1, 0)), \
                'p': lambda h: theGame().addMessage(h.fullDescription()), \
                'k': lambda h: h.__setattr__('hp', 0), \
                'u': lambda h: h.use(theGame().select(h._inventory)), \
                ' ': lambda h: None, \
                'h': lambda hero: theGame().addMessage("Actions disponibles : " + str(list(Game._actions.keys()))), \
                'b': lambda hero: theGame().addMessage("It's me " + hero.name + '!'), \
                'm': lambda hero: healmagie(theGame()._floor._hero),\
                'g': lambda hero: teleportmagie(theGame()._floor._hero,True),\
                'i': lambda hero: None,\
                'o': lambda hero: theGame().deleteinvent()}

    def __init__(self, level=1, hero=None):
        self._level = level
        self._messages = []
        if hero == None:
            hero = Hero()
        self._hero = hero
        self._floor = None

        self.application = tk.Tk()
        self.application.title('MARIO')
        top = self.application.winfo_toplevel()
        MenuBar = tk.Menu(top, tearoff=0)
        top['menu'] = MenuBar 
        subMenu = tk.Menu(MenuBar)
        MenuBar.add_cascade(label='File', menu=subMenu)
        subMenu.add_command(label='Quit - Ctrl-q', command=self.application.quit)
        ##carte jeu
        carte = tk.Canvas(self.application, width = MAX_SIZE*PIX_SIZE, height = MAX_SIZE*PIX_SIZE, background="white")
        carte.grid(row=0, column=0)
        self.carte = carte
        ##zone de report      
        report = tk.Canvas(self.application, width = MAX_SIZE*PIX_SIZE, height = MAX_SIZE*PIX_SIZE, background = 'white')
        report.grid(row=0, column=1)
        self.report = report
        
# pour lancer le jeu et importer les éléments
        self.bind_elements()
        self.define_fonts()
        self.debut()

    def define_fonts(self):
       self.font_normal = tkFont.Font(family = 'Courier',size = 30, weight = 'bold')
       self.font_small = tkFont.Font(family = 'Courier',size = 20)
       self.font_tiny = tkFont.Font(family = 'Courier',size = 10)

       

    def bind_elements(self):
        
        brique = tk.PhotoImage(file="IMAGES/sols/brique.png")
        pelouse = tk.PhotoImage(file="IMAGES/sols/pelouse.png")
        tuyau = tk.PhotoImage(file="IMAGES/sols/tuyau.png")
        mario= tk.PhotoImage(file="IMAGES/persos/mario.png")
        armure = tk.PhotoImage(file="IMAGES/elements/armure.png")
        bowser = tk.PhotoImage(file="IMAGES/persos/bowser.png")
        bombe = tk.PhotoImage(file="IMAGES/persos/bombe.png")
        boo = tk.PhotoImage(file="IMAGES/persos/boo.png")
        ddkong= tk.PhotoImage(file = "IMAGES/persos/ddkong.png")
        tchomp = tk.PhotoImage(file="IMAGES/persos/tchomp.png")
        gumba = tk.PhotoImage(file="IMAGES/persos/gumba.png")
        etoile = tk.PhotoImage(file="IMAGES/elements/etoile.png")
        champiR = tk.PhotoImage(file="IMAGES/elements/champiR.png")
        champiV = tk.PhotoImage(file="IMAGES/elements/champiV.png")
        fleurR = tk.PhotoImage(file="IMAGES/elements/fleurR.png")
        fleurB = tk.PhotoImage(file="IMAGES/elements/fleurB.png")
        yoshi = tk.PhotoImage(file="IMAGES/persos/yoshi.png")
        coeur = tk.PhotoImage(file="IMAGES/elements/coeur.png")
        bg_report = tk.PhotoImage(file= "IMAGES/sols/bg_report.png")
        poulet = tk.PhotoImage(file="IMAGES/elements/poulet2.png")
        move = tk.PhotoImage(file="IMAGES/elements/move.png")
        piege = tk.PhotoImage(file="IMAGES/sols/piege.png")
        debut= tk.PhotoImage(file="IMAGES/elements/debutjeu.png")
        key= tk.PhotoImage(file="IMAGES/elements/key.png")
        tresor = tk.PhotoImage(file="IMAGES/elements/tresor.png")
        plume= tk.PhotoImage(file="IMAGES/elements/plume.png")
        inventaire = tk.PhotoImage(file="IMAGES/elements/inventaire.png")
        GAMEOVER = tk.PhotoImage(file = "IMAGES/elements/gameOver.png")
        
        self.dfloor = {'.': pelouse, ' ': brique}
        
        self.delements = {'@': mario, '!': champiV, '?': champiR, 'G': gumba,
                          'B': bowser, 'D': ddkong, '%': tchomp, 'k': bombe, 'e': etoile,
                          'b': boo, 'F': fleurR, 'f': fleurB, 'E': tuyau, 'Y': yoshi,
                          'A': armure, 'P': poulet, 'p': piege, 'T' : tresor, 'K': key,
                          'pl': plume}
        
        self.dautres = {'coeur': coeur,
                        'bg': bg_report, 'move': move , 'debut_jeu': debut,
                        'inventaire' : inventaire, 'GO': GAMEOVER}
        
        self.dinventory = {'!': champiV, '?': champiR, 'e': etoile,
                           'F': fleurR, 'f': fleurB, 'Y': yoshi, 'A' : armure,
                           'P' : poulet, 'pl': plume}

        self.application.bind("<Control-q>", quit)
        self.application.bind("<Key>", self.actions)
        self.application.bind("<Up>", lambda event: self.actions(event, 'z')) 
        self.application.bind("<Left>", lambda event: self.actions(event, 'q')) 
        self.application.bind("<Down>", lambda event: self.actions(event, 's')) 
        self.application.bind("<Right>", lambda event: self.actions(event, 'd'))

    

    def gdraw(self):
        self.carte.delete('all')
        
        for ni, i in enumerate(self._floor._mat): 
            for nj, j in enumerate(i):
                if j in self.dfloor.keys():
                   self.carte.create_image(nj*PIX_SIZE, ni*PIX_SIZE, image= self.dfloor[j], anchor=tk.NW)
                elif j.abbrv in self.delements.keys(): ## les "  '@', '!' ... sont des creatures donc on prend leur abbrv
                
                    self.carte.create_image(nj*PIX_SIZE, ni*PIX_SIZE, image=self.dfloor['.'], anchor=tk.NW)
                    self.carte.create_image(nj*PIX_SIZE, ni*PIX_SIZE, image=self.delements[j.abbrv], anchor=tk.NW)



    def draw_report(self):
       self.report.delete('all')
       self.report.create_image(320,300,image = self.dautres['bg'])
       self.report.create_image(550, 620, image = self.dautres['move'])
       self.report.create_image(250, 620, image = self.dautres['inventaire'])
       self.report.create_text(560,100,font = self.font_normal,fill = 'white', text = str(self._floor._hero.LEVEL))
       for num, elem in enumerate(self._hero._inventory):
          self.report.create_image(25+ num*25, 250, image = self.delements[elem.abbrv])
       
       #on dessine les hp
       self.report.create_image(40,100, anchor= tk.W ,image=self.dautres['coeur'])
       self.report.create_text(95,100, font= 'Courier', text= "x" + str(self._hero.hp))
       #on dessine les xp
       X =int((100*(theGame()._floor._hero.XP))/(10*theGame()._floor._hero.LEVEL))
       if theGame()._floor._hero.XP != 0 :
          self.report.create_rectangle(270,85,270 + X,105, width = 1, fill= "green" )
       self.report.create_rectangle(270,85,360,105, width = 2)
       #on dessine la satiété
       X =int(5*theGame()._floor._hero.satiété)
       self.report.create_image(235,145, image = self.delements['P'])
       if theGame()._floor._hero.satiété > 0 :
          self.report.create_rectangle(270,150,270 + X,130, width = 1, fill= "red" )
       self.report.create_rectangle(270,150,270 + int(5*theGame()._floor._hero.satiétéMAX),130, width = 2)
       # on dessine le niveau de magie
       X =int(5*theGame()._floor._hero.magie)
       self.report.create_image(490,490, image = self.dinventory['pl'])
       if theGame()._floor._hero.magie > 0 :
          self.report.create_rectangle(510,500,510 + X,480, width = 1, fill= "white" )
       self.report.create_rectangle(510,500,510 + int(100),480, width = 2)
          
       
       
                 
    def debut(self):
       self.carte.create_image(60,0, image = self.dautres['debut_jeu'], anchor = tk.NW)
       self.report.create_image(-600,0, image = self.dautres['debut_jeu'], anchor = tk.NW)
       play = askyesno('Jeu Mario', "Voulez-vous jouer?")
       if not play:
          exit()
               


    def buildFloor(self):
        """Creates a map for the current floor."""
        self._floor = Map(hero=self._hero)
        nb_rooms = len(self._floor._rooms)
        if nb_rooms >= 2:
           rand_rooms = random.sample(theGame()._floor._rooms, k=2)
           self._floor.put(rand_rooms[0].randEmptyCoord(theGame()._floor), Tresor())
           self._floor.put(rand_rooms[1].randEmptyCoord(theGame()._floor), Equipment('Key'))
        else:
           self._floor.put(self._floor._rooms[0].randEmptyCoord(theGame()._floor), Tresor())
           self._floor.put(self._floor._rooms[1].randEmptyCoord(theGame()._floor), Equipment('Key'))

        self._floor.put(self._floor._rooms[-1].center(), Stairs())
        self._level += 1


    def addMessage(self, msg):
        """Adds a message in the message list."""
        self._messages.append(msg)

    def readMessages(self):
        """Returns the message list and clears it."""
        s = ''
        for m in self._messages:
            s += m + '. ' 
        self._messages.clear()
        return s

    def randElement(self, collect):
        """Returns a clone of random element from a collection using exponential random law."""
        x = random.expovariate(1 / self._level)
        for k in collect.keys():
            if k <= x:
                l = collect[k]
        return copy.copy(random.choice(l))

    def randEquipment(self):
        """Returns a random equipment."""
        return self.randElement(Game.equipments)

    def randMonster(self):
        """Returns a random monster."""
        return self.randElement(Game.monsters)


    def select(self, l):
        c = askinteger("Inventory", "Choose item> " + str([str(l.index(e)) + ": " + e.name for e in l]))
        print(c, type(c))
        if c in range(len(l)):
            return l[int(c)]

         
    def deleteinvent(self):
       if len(self._floor._hero._inventory) >= 1:
          l = self._floor._hero._inventory
          c = askinteger("Inventory", "Equipement a supprimer " + str([str(l.index(e)) + ": " + e.name for e in l]))
          del self._floor._hero._inventory[c]
       else :
          print("Aucun objet dans votre inventaire")
          
        
    def actions(self, event, char=None):

        if char is None:
            char = event.char

        if char in theGame()._actions :
           if self._hero.hp > 0:
              print(self._hero.description())
              print(str(self.readMessages()))
              self._actions[char](self._floor._hero)
              self._floor.moveAllMonsters()
              self.draw_report()
              self.gdraw()
           else:
               print("--- Game Over ---")
               self.carte.delete('all')
               self.report.delete('all')
               self.carte.create_image(50,0, anchor=tk.NW, image = self.dautres['GO'])
               self.report.create_image(-600,0, anchor=tk.NW, image = self.dautres['GO'])
               replay = askyesno('Game over', "Voulez-vous rejouer?")
               if replay:
                   hero = Hero()
                   self._hero = hero
                   self.bind_elements()
                   self.define_fonts()
                   self.initialize()
               else:
                   self.application.quit()
        else:
            pass

    def initialize(self):
        print("--- Welcome Hero! ---")
        self.buildFloor()
        self.gdraw()
        self.draw_report()


    def play(self):
        """Main game loop"""
        self.application.focus_get()
        self.carte.delete('all')
        self.initialize()
        self.application.mainloop()
        

def theGame(game=Game()):
    """Game singleton"""
    return game

getch = _find_getch()
theGame().play()

