import random
import pygame
import pygame_menu


class Dice:
    def __init__(self):
        self.value = 0
        self.held = False
        self.locked = False

    def roll(self):
        self.value = random.randint(1, 6)


class Game:
    def __init__(self):
        self.dices = [Dice() for i in range(6)]
        for dice in self.dices:
            dice.roll()
        self.turn = 1
        self.target_score = 0
        self.turn_score = 0
        self.throw_score = 0
        self.player1 = Player()
        self.player2 = Player()
        self.active_player = self.player1
        self.unactive_player = self.player2

    def roll(self):
        for dice in self.dices:
            if not dice.held:
                dice.roll()

    def lock(self):
        for dice in self.dices:
            if dice.held:
                dice.locked = True
                dice.held = False

    def unlock_all(self):
        for dice in self.dices:
            dice.locked = False

    def hold(self, dice):
        if dice.held:
            dice.held = False
        else:
            dice.held = True

    def hold_all(self):
        for dice in self.dices:
            dice.held = True

    def unhold_all(self):
        for dice in self.dices:
            dice.held = False

    def count_score(self):
        dices_values = [dice.value for dice in self.get_held_dices()]
        count_list = [1, 2, 3, 4, 5, 6]
        nb_of_each_values = [dices_values.count(value) for value in count_list]

        # On s'occupe d'abord des brelans, carrés, etc.
        # cas particulier du 1
        if nb_of_each_values[0] >= 3:
            self.throw_score += 1000*(2**(nb_of_each_values[0]-3))
            for _i in range(nb_of_each_values[0]):
                nb_of_each_values[0] -= 1

        # cas général
        for i in range(1, 6):
            if nb_of_each_values[i] >= 3:
                self.throw_score += (i+1)*100*(2**(nb_of_each_values[i]-3))
                for _i in range(nb_of_each_values[i]):
                    nb_of_each_values[i] -= 1

        # On s'occupe ensuite des 1 et 5 restants
        if nb_of_each_values[0] > 0 or nb_of_each_values[4] > 0:
            self.throw_score += \
                nb_of_each_values[0]*100 + nb_of_each_values[4]*50

        print(f"Score : {self.throw_score}")

        if self.throw_score == 0:
            self.turn_score = 0
            print("Vous sautez !")

        return self.throw_score

    def validate(self):
        self.turn_score += self.count_score()
        self.throw_score = 0
        self.lock()

    def next_turn(self):
        self.active_player.score += self.turn_score
        self.check_win()
        self.turn += 1
        self.unlock_all()
        self.unhold_all()

        temp = self.active_player
        self.active_player = self.unactive_player
        self.unactive_player = temp

        self.roll()

    def surrender(self):
        print(f"{self.active_player.name} a abandonné !")
        print(f"{self.unactive_player.name} a gagné !")

    def check_win(self):
        if self.active_player.score >= self.target_score:
            print(f"{self.active_player.name} a gagné !")

    def get_held_dices(self):
        return [dice for dice in self.dices if dice.held]

    def __str__(self):
        return f"Turn: {self.turn}\nTarget Score: {self.target_score}\n" \
               f"Turn score: {self.turn_score}\n" \
               f"Throw score: {self.throw_score}\n" \
               f"Active player: {self.active_player.name}"


class Player:
    def __init__(self):
        self.score = 0


class GUI:
    def __init__(self, app):
        self.dimensions = [(640, 480), (800, 600), (1024, 768), (1280, 1024)]
        self.width = self.dimensions[0][0]
        self.height = self.dimensions[0][1]

        self.J1_input = None
        self.J2_input = None
        self.target_score_input = None
        self.resolution_choice = 0
        self.app = app

        pygame.init()

        self.fenetre = pygame.display.set_mode((self.width, self.height))
        self.myFont = pygame.font.SysFont("Times New Roman", 30)
        self.white = (255, 255, 255)

        self.dices = [pygame.image.load(f"assets/dice{i}.png").convert_alpha()
                      for i in range(1, 7)]

        self.bg_image = pygame.image.load("assets/bg.jpg").convert()
        self.bg = None

        self.resize(self.resolution_choice)

        self.menu = pygame_menu.Menu("Farkle",
                                     self.dimensions[0][0],
                                     self.dimensions[0][1],
                                     theme=pygame_menu.themes.THEME_BLUE)
        self.create_menu()

    def play_button(self):
        print("Jouer")

        self.resize(self.resolution_choice.get_value()[1])

        if self.J1_input.get_value() == "":
            self.J1_input.set_value("Joueur 1")
        if self.J2_input.get_value() == "":
            self.J2_input.set_value("Joueur 2")

        if (not (self.target_score_input.get_value()).isdigit()):
            self.app.game.target_score = 10000
        elif int(self.target_score_input.get_value()) == 0:
            self.app.game.target_score = 10000
        else:
            self.app.game.target_score = int(
                self.target_score_input.get_value())

        self.display_hud()
        self.gui_loop()

    def resize(self, resolution_value):
        self.width = self.dimensions[resolution_value][0]
        self.height = self.dimensions[resolution_value][1]
        self.fenetre = pygame.display.set_mode((self.width, self.height))

        for i in range(6):
            self.dices[i] = pygame.transform.scale(self.dices[i],
                                                   (self.width/640*50,
                                                   self.width/640*50))

        self.bg = pygame.transform.scale(self.bg_image,
                                         (self.width, self.height))

    def reset_screen(self):
        self.fenetre.blit(self.bg, (0, 0))

    def get_len_string(self, string):
        return self.myFont.size(string)[0]

    def display_hud(self):
        self.reset_screen()

        # Affichage des noms
        text = str(self.J1_input.get_value())
        text_render = self.myFont.render(text, True, self.white)
        self.fenetre.blit(text_render, (20, 5))

        text = str(self.J2_input.get_value())
        text_render = self.myFont.render(text, True, self.white)
        self.fenetre.blit(text_render,
                          (self.width-self.get_len_string(text)-20, 5))

        # Affichage des scores des joueurs
        text = "Score :" + str(self.app.game.player1.score) + '/' + str(
            self.app.game.target_score)
        text_render = self.myFont.render(text, True, self.white)
        self.fenetre.blit(text_render, (20, 50))

        text = "Score : " + str(self.app.game.player2.score) + '/' + str(
            self.app.game.target_score)
        text_render = self.myFont.render(text, True, self.white)
        self.fenetre.blit(text_render,
                          (self.width-self.get_len_string(text)-20, 50))

    def create_menu(self):
        self.menu.add.button("Jouer", self.play_button)
        self.J1_input = self.menu.add.text_input("J1 : ",
                                                 default="Joueur 1",
                                                 maxchar=10)
        self.J2_input = self.menu.add.text_input("J2 : ",
                                                 default="Joueur 2",
                                                 minchar=1,
                                                 maxchar=10)
        self.target_score_input = self.menu.add.text_input(
                                                    "Score à atteindre : ",
                                                    default="10000",
                                                    maxchar=5)

        self.resolution_choice = self.menu.add.selector(
            "Résolution : ",
            [(f"{self.dimensions[i][0]}x{self.dimensions[i][1]}", i)
             for i in range(len(self.dimensions))])

        self.menu.add.button("Quitter", pygame_menu.events.EXIT)
        self.GotoMenu()

    def GotoMenu(self):
        self.fenetre = pygame.display.set_mode((
            self.dimensions[0][0], self.dimensions[0][1]))
        self.menu.mainloop(self.fenetre)

    def gui_loop(self):

        running = True

        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("Quitter")
                        running = False
                    elif event.key == pygame.K_TAB:
                        self.GotoMenu()
                    elif event.key == pygame.K_RETURN:
                        print("Entrée")

                        self.app.game.roll()

                        self.display_hud()

                        # Affichage des dés
                        for i in range(6):
                            self.fenetre.blit(
                                self.dices[self.app.game.dices[i].value-1],
                                (self.width*0.2+75*(i), self.height/2))
                        pygame.display.flip()

            pygame.display.update()

        pygame.quit()


class App:
    def __init__(self):
        self.game = Game()
        self.gui = GUI(self)

        # self.gui.gui_loop()

    def engine_loop1(self):
        print(self.game.__str__())
        self.game.hold_all()
        print_dice(self.game)
        self.game.count_score()
        self.game.roll()
        print_dice(self.game)
        self.game.hold(self.game.dices[0])
        self.game.roll()
        print_dice(self.game)
        self.game.roll()
        print_dice(self.game)
        self.game.roll()
        print_dice(self.game)
        print(self.game.__str__())

    def engine_loop(self):
        print("Engine loop")


def print_dice(game):
    print("Dice: ", end="")
    for dice in game.dices:
        print(dice.value, end=" ")
    print()


# TEST ############################


def test():
    app = App()


test()
