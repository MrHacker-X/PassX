# !/bin/python3
from time import sleep
import random
import array
import os

banner = """\033[1;92m
██████╗░░█████╗░░██████╗░██████╗██╗░░██╗
██╔══██╗██╔══██╗██╔════╝██╔════╝╚██╗██╔╝
██████╔╝███████║╚█████╗░╚█████╗░░╚███╔╝░
██╔═══╝░██╔══██║░╚═══██╗░╚═══██╗░██╔██╗░
██║░░░░░██║░░██║██████╔╝██████╔╝██╔╝╚██╗
╚═╝░░░░░╚═╝░░╚═╝╚═════╝░╚═════╝░╚═╝░░╚═╝
░░░░░░░░░Created by: MrHacker-X░░░░░░░░░
"""
m_menu = """\033[1;92m
[?] Select any option:

[1] Generate password
[2] Connect with US
[3] About
[0] Quit

[~]passx>> """

soc = """\033[1;92m
[*] Select any option

[01] Instagram
[02] Facebook
[03] Github
[04] YouTube
[05] Telegram
[06] My Website
[99] Back
[00] Quit

[??] >> """

about = """\033[1;92m
[*] What is password generator ?

>>> A password generator is a software tool that creates random or customized passwords for users. It helps users create stronger passwords that provide greater security for a given type of access.

[*] Tool's Overview

>>> 'PassX' is a strong password generator for linux or termux. This tool can use by both kind of user That is Termux and Linux. You can generate very strong password for your account. This tool is work on a simple tecghnique which is random password generator. You can generate password with your custom length, I did't fixed length or count of password. So that you can generate customized password. 

[*] My Social Media username:

>>> Instagram  : @ 0hacker_x0
>>> Telegram   : @ mrhackersx
>>> YouTube    : @ sololex
>>> Facebook   : @ hackerxmr
>>> Github     : @ Mrhacker-X
>>> My website : hackwithalex.github.io

[*] For You

>>> You can contact me if you're getting error in usages, via instagram. If you don't want to contact me on instagram then you can contact me via whatsapp. You can get my whatsapp number from my website, So go on my website for my whatsapp number.

>>> And thanks for using my tool 'PassX'.

"""


def mai():
    while True:
        os.system('clear')
        print(banner)
        man = input(m_menu)
        if man == '':
            print('\033[1;92m[!] No Input Detected')

        elif man == '1' or man == '01':
            print("\033[1;92m\n[*] Password generator launching...")
            sleep(1)
            MAX_LEN = int(input('[?] Password length: '))
            cot = int(input('[?] Password count: '))

            print('\033[1;92m\n[*] Password length ' + str(MAX_LEN) + ' Selected')
            print('\033[1;92m[*] ' + str(cot) + ' Password will generate\n')

            print('\033[1;92m\n[*] Generating.....\n')
            sleep(1.3)
            print('\033[1;92m\n[*] Following are the generated password.\n')

            sleep(1)

            for i in range(cot):
                
                DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
                SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>', '*', '(', ')', '<']
                
                COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS
                rand_digit = random.choice(DIGITS)
                rand_upper = random.choice(UPCASE_CHARACTERS)
                rand_lower = random.choice(LOCASE_CHARACTERS)
                rand_symbol = random.choice(SYMBOLS)
                temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol
                
                for x in range(MAX_LEN - 4):
                    temp_pass = temp_pass + random.choice(COMBINED_LIST)
                    temp_pass_list = array.array('u', temp_pass)
                    random.shuffle(temp_pass_list)
                password = ""
                
                for x in temp_pass_list:
                        password = password + x
                print(password)
                sleep(0.1)

            print('\033[1;92m\n[*] Mission completed\n')
            input('\033[1;94mPress ENTER To Continue\033[1;92m')

        elif man == '2' or man == '02':
            os.system("clear")
            print(banner)
            print()
            print("\033[1;92m[*] Thanks for using my tool 'PassX'. So you can follow me on various social media site. Link and options are given down below, So select here options where you want to follow me ")
            print()
            print()
            while True:
                fol = input(soc)
                if fol == '1' or fol == '01':
                    print()
                    print("\033[1;92m[*] Opening my Instagram profile in your device \n")
                    sleep(1)
                    os.system("xdg-open https://instagram.com/0hacker_x0")
                
                elif fol == '2' or fol == '02':
                    print()
                    print("\033[1;92m[*] Opening my Facebook page in your device \n")
                    sleep(1)
                    os.system("xdg-open https://facebook.com/hackerxmr")

                elif fol == '3' or fol == '03':
                    print()
                    print("\033[1;92m[*] Opening my Github profile in your device \n")
                    sleep(1)
                    os.system("xdg-open https://github.com/MrHacker-X")

                elif fol == '4' or fol == '04':
                    print()
                    print("\033[1;92m[*] Opening my YouTube channel in your device \n")
                    sleep(1)
                    os.system("xdg-open https://youtube.com/c/Sololex")
                
                elif fol == '5' or fol == '05':
                    print()
                    print("\033[1;92m[*] Opening my Telegram Channel in your device \n")
                    sleep(1)
                    os.system("xdg-open https://t.me/mrhackersx")

                elif fol == '6' or fol == '06':
                    print()
                    print("\033[1;92m[*] Opening my Website in your device \n")
                    sleep(1)
                    os.system("xdg-open https://hackwithalex.github.io")

                elif fol == '99':
                    print()
                    print("\033[1;92m[*] Getting back ...\n")
                    sleep(1)
                    break

                elif fol == '0' or fol == '00':
                    print()
                    print("\033[1;92m\n[*] Thanks for using PassX\n")
                    print("\033[1;92m[*] Quiting ...\n")
                    sleep(1)
                    exit()
                    
                else:
                    print()
                    print("\033[1;92m[*] Invalid Input")
                    print()

        
        elif man == '3' or man == '03':
            os.system('clear')
            print(banner)
            print(about)
            input('\033[1;94mPress ENTER To Continue\033[1;92m')
            print()
        
        elif man == '0':
            print('\033[1;92m\n[*] Thanks for using PassX')
            print('\033[1;92m[*] Quitting.....\n')
            sleep(1)
            exit()

        else:
            print('\033[1;92m\n[!] Invalid Input Detected')
            print('\033[1;92m[*] Please Enter A Valid Input\n')
            sleep(1)

mai()