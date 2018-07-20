# coding: utf8


import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import random as rd
import datetime
import pyttsx3
import time
import os


PROBABILITY_RECAP = .14  # about 1/7
PROBABILITY_SHOT = .059  # about 1/17
MAX_SWALLOWS = 5
MAX_WAIT = 4 * 60
HISTORY = []

COLORS_ALL = ['b','g','r','c','m','gold','orange','gray','k','w']

DRAWING = "\
                               (\n\
                                )   *\n\
                  )     *      (\n\
        )        (                   (\n\
       (          )     (             )\n\
        )    *           )        )  (\n\
       (                (        (      *\n\
        )          H     )        )\n\
                  [ ]            (\n\
           (  *   |-|       *     )    (\n\
     *      )     |_|        .          )\n\
           (      | |    .  \n\
     )           /   \     .    ' .        *\n\
    (           |_____|  '  .    .  \n\
     )          | ___ |  \~~~/  ' .   (\n\
            *   | \ / |   \_/  \~~~/   )\n\
                | _Y_ |    |    \_/   (\n\
    *           |-----|  __|__   |      *\n\
                `-----`        __|__"


def clear():
    import platform
    if platform.system() == 'Windows':
        os.system("cls")
    else:
        os.system("clear")


def format(name, swallows):
    if swallows == 1:
        return "{0} boit une gorgée, ".format(name)
    return "{0} boit {1} gorgées, ".format(name, swallows)


def generate_sentence(players, scores):
    global HISTORY
    sentence = ""
    drinkers = rd.sample(players, rd.randint(1, len(players)))
    swallows = [rd.randint(1, MAX_SWALLOWS) for _ in range(len(drinkers))]
    swallows.sort()
    HISTORY.append((time.time(), []))
    for i, person in enumerate(drinkers):
        sentence += format(person, swallows[i])
        scores[person] += swallows[i]
        HISTORY[-1][1].append((person, swallows[i]))
    return sentence[:-2], scores


def catch(players, scores):
    global HISTORY
    max_score = max(list(scores.values()))
    sentence = "Rattrapages: "
    HISTORY.append((time.time(), []))
    for person in players:
        if scores[person] != max_score:
            sentence += format(person, max_score - scores[person])
            HISTORY[-1][1].append((person, max_score - scores[person]))
            scores[person] = max_score
    return sentence[:-2], scores


def shot(players):
    global HISTORY
    HISTORY.append((time.time(), rd.choice(players)))
    return "{0} finit son verre !".format(HISTORY[-1][1])


def generate_plot(players, t_start):
    global HISTORY
    global COLORS_ALL
    t_stop = time.time()
    duration = int(t_stop - t_start)
    time_step = 1  # second(s)
    t = [(i + 1) * time_step for i in range(duration // time_step + 1)]
    swallows = {p:[0] for p in players}
    shots = {p:[] for p in players}
    history_index = 0  # next shot
    for tt in t:
        if history_index < len(HISTORY) and\
        t_start + tt >= HISTORY[history_index][0]:
            seen_players = []
            if len(HISTORY[history_index][1]) > 0 and\
            type(HISTORY[history_index][1][0]) == type(("", 0)):
                for p, s in HISTORY[history_index][1]:
                    swallows[p].append(swallows[p][-1] + s)
                    seen_players.append(p)
            elif len(HISTORY[history_index][1]) > 0:
                shots[HISTORY[history_index][1]].append(tt)
            for p in players:
                if p not in seen_players:
                    swallows[p].append(swallows[p][-1])
            history_index += 1
        else:
            for p in players:
                swallows[p].append(swallows[p][-1])
    plt.style.use('seaborn')
    fig = plt.figure(figsize=(14, 6))
    plt.title("Débit de boisson entre {0} et {1}".format(
        datetime.datetime.fromtimestamp(t_start).strftime('%H:%M'),
        datetime.datetime.fromtimestamp(t_stop).strftime('%H:%M')))
    ax = fig.add_subplot(111)
    ax.set_xlabel("Temps")
    ax.set_ylabel("Gorgées")

    colors = []
    for i, p in enumerate(players):
        colors.append(COLORS_ALL[i % len(COLORS_ALL)])
    xaxis = [datetime.datetime.fromtimestamp(ttt)\
        for ttt in [t_start] + [tt + t_start for tt in t]]
    for p, c in zip(players, colors):
        ax.plot(xaxis, swallows[p], label=p, c=c)
        ax.plot(
            [datetime.datetime.fromtimestamp(t_start + tt) for tt in shots[p]],
            [swallows[p][tt] for tt in shots[p]], '*', c=c)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    plt.legend(loc='best')
    plt.show()


def init():
    global PROBABILITY_RECAP
    global PROBABILITY_SHOT
    global MAX_SWALLOWS
    global MAX_WAIT

    clear()
    print("\n\n\t\t====================")
    print("\t\t| BUVETTE ROULETTE |")
    print("\t\t====================\n\n")
    print(DRAWING)
    print("\n\n\tInscription des joueurs (laisser vide pour commencer):")
    players = []
    while len(players) == 0:
        while True:
            line = input("Joueur {0}> ".format(len(players) + 1))
            if len(line) == 0:
                break
            players.append(line)
    scores = {p:0 for p in players}
    print("\n\n\tRéglage des paramètres (laisser vide pour utiliser\
la valeur par défaut):")
    line = input("Probabilité de rattrapage ({0}): ".format(PROBABILITY_RECAP))
    if len(line) > 0 and float(line) >= 0 and float(line) <= 1:
        PROBABILITY_RECAP = float(line)
    line = input("Probabilité de cul-sec   ({0}): ".format(PROBABILITY_SHOT))
    if len(line) > 0 and float(line) >= 0 and float(line) <= 1:
        PROBABILITY_SHOT = float(line)
    line = input("Nombre maximal de gorgées    ({0}): ".format(MAX_SWALLOWS))
    if len(line) > 0 and int(line) > 0:
        MAX_SWALLOWS = int(line)
    line = input("Temps d'attente maximal  ({0} s): ".format(MAX_WAIT))
    if len(line) > 0 and int(line) >= 1:
        MAX_WAIT = int(line)
    return players, scores


def main():
    players, scores = init()
    engine = pyttsx3.init()
    t_start = time.time()
    try:
        sentence = "Bienvenue à "
        for p in players[:-1]:
            sentence += "{0}, ".format(p)
        sentence += "et {0}. Le jeu va commencer. Remplissez vos verres."\
                        .format(players[-1])
        clear()
        print("\n\n\t" + sentence + "\n\n")
        engine.say(sentence)
        engine.runAndWait()
        while True:
                for i in range(rd.randint(1, MAX_WAIT)):
                    time.sleep(1)
                if rd.random() < PROBABILITY_SHOT:
                    sentence = shot(players)
                elif rd.random() < PROBABILITY_RECAP and\
                    min(list(scores.values())) != max(list(scores.values())):
                    sentence, scores = catch(players, scores)
                else:
                    sentence, scores = generate_sentence(players, scores)
                print(sentence)
                engine.say(sentence)
                engine.runAndWait()
    except KeyboardInterrupt as e:
        print("\n\n\tFin du game. Durée : {0}min. Scores finaux:".format(
            int(time.time() - t_start) // 60))
        for p in players:
            print("{0}:\t {1} gorgées".format(p, scores[p]))
        generate_plot(players, t_start)

if __name__ == "__main__":
    main()
