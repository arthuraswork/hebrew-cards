from colorama import Fore, Style
from random import randint
import questionary 
from dataclasses import dataclass
import json
import os

@dataclass
class Card:
    word: str
    translate: str
    translit: str
    sample: str
    sample_translate: str
    learned: bool
    
    def show_word(self):
        print(fr"""

________________________________
\                               \
 \{(28 - len(self.word)) * " "}{Style.BRIGHT}{self.word}{Style.RESET_ALL}   \
  \                               \
   \                               \
    \_______________________________\
 
""")
    
    def show_translate(self):
        print(fr"""
________________________________
\                               \
 \{(28 - len(self.word)) * " "}{Style.BRIGHT}{self.word}{Style.RESET_ALL}   \
  \   {Style.DIM}{self.translate}{Style.RESET_ALL}{(28 - len(self.translate)) * " "}\
   \  {Fore.CYAN}{self.translit}{Fore.RESET}{(28 - len(self.translit)) * " "} \
    \_______________________________\

     {self.sample} - {self.sample_translate}
""")
    
    def do_test(self):
        if '/' in self.translate:
            answers = [i.strip().lower() for i in self.translate.split('/')]
        else:
            answers = [self.translate.strip().lower()]
        self.show_word()
        user_input = input('>>>').strip().lower()
        if user_input in answers:
            print(f"{Fore.GREEN}Правильно{Fore.RESET}")
            return 1
        else:
            print(f"{Fore.RED}Не правильно{Fore.RESET}")
            return 0


def inplace_choices(array: list, k: int):
    result = []
    for _ in range(k):
        array_len = len(array)
        result.append(array.pop(randint(0, array_len-1)))
    return result


class Session:
    def __init__(self, path: str = None, count_of_cards: int = None, cards: list[Card] = None, clear = True):
        self.clear = clear
        if not cards:
            self.path = path
            self.count_of_cards = count_of_cards
            with open(self.path, 'r', encoding='utf-8') as f:
                cards = f.readlines()
                self.cards: list[Card] = []
                cards_jsonl = inplace_choices(cards, count_of_cards)
                for card in cards_jsonl:
                    self.cards.append(Card(**(json.loads(card))))
        else:
            self.cards = cards
            self.count_of_cards = len(cards)

    def end_of_iteration(self):
        if self.clear:
            os.system('clear')

    def learn_mod(self):
        for card in self.cards:
            self.end_of_iteration()
            card.show_word()
            translation = questionary.press_any_key_to_continue('Показать перевод?')
            translation.ask()
            card.show_translate()
            translation = questionary.press_any_key_to_continue('Продолжить?')
            translation.ask()
        finish_session = questionary.confirm('Закончить сессию?')
        if finish_session.ask() == False:
            return self.learn_mod()
        
    def test_mod(self):
        corrects = 0
        uncorrects: list[Card] = []
        for card in self.cards:
            self.end_of_iteration()
            result = card.do_test()
            questionary.press_any_key_to_continue().ask()
            corrects += result
            if not result:
                uncorrects.append(card)
        print(f'Правильных ответов: {corrects}/{self.count_of_cards}')
        print("Cтоит повторить:")
        for card in uncorrects:
            print(f"{card.word}[{card.translit}] - {card.translate}")
        return uncorrects 


        
class Menu:

    def __init__(self):
        self.options = ["Просмотр Карточек", "Тест", "Настройки","Выйти"]
        self.count_of_cards = 5
        self.path = './words.jsonl'
        self.clear_console = True

    def include_words_lib(self):
        path = questionary.path('Добавьте библиотеку слов').ask()
        if path:
            self.path = path
    def style_settings(self):
        self.clear_console = questionary.confirm('Отчищать консоль после итераций?').ask()


    def change_session_count(self):
        print('Колличество карточек в сессии')
        count_of_cards = input('>>>')
        if not count_of_cards.isdigit():
            print(f'{Fore.RED}Необходимо ввести число{Fore.RESET}')
        else:
            self.count_of_cards = int(count_of_cards)
            print(f'{Fore.GREEN}Изменение применено: {count_of_cards}{Fore.RESET}')

    def settings(self):
        settings = {
            "Изменить количество слов в сессии":  self.change_session_count,
            "Заменить библиотеку слов": self.include_words_lib,
            "Настройки стиля": self.style_settings
        }

        setting = questionary.select("Настройки", list(settings.keys())).ask()
        return settings[setting]()


    def main_menu(self):
        while True:
            options = questionary.select('Меню:', self.options)
            match options.ask():
                case "Просмотр Карточек":
                    session = Session(self.path, self.count_of_cards, clear=self.clear_console)
                    session.learn_mod()

                case "Тест":
                    session = Session(self.path, self.count_of_cards, clear=self.clear_console)
                    uncorrects = session.test_mod()
                    if uncorrects:
                        repeat_the_words = questionary.confirm("Повторить карточки?").ask()
                        if repeat_the_words:
                            session = Session(cards=uncorrects, clear=self.clear_console)
                            session.learn_mod()

                case "Настройки":
                    self.settings()
                case "Выйти":
                    break
if __name__ == '__main__':
    menu = Menu()
    menu.main_menu()
