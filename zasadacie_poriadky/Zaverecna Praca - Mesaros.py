# Importovanie modulov
import os
import sys
import tkinter
from datetime import datetime
from math import *
from random import *
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageFont

# Definícia globálnych premenných
root = tkinter.Tk()
canvas = tkinter.Canvas()
export = Image.new("RGB", (1000, 1440), "white")
draw = ImageDraw.Draw(export)
appState = "Main menu"
actionBoxes = {}
binds = []
tabulka = []
tabulkaOriginal = []
textBox = ""
trieda = ''
target = False
targetStudent = ""
OS = os.name
scale = 1
mode = "local".capitalize()  # local pre lokalny testovaci mod a database pre mod prace s databazou


# Definícia funkcií
def _init():
    global canvas, appState, scale
    # Reset premenných
    appState = "Main menu"

    if OS == "nt":
        scale = 0.75

    # Nastavenie okna
    root.resizable(False, False)
    root.title("Zasadací poriadok")

    # Inicializácia plátna
    canvas.pack()
    canvasReset()


def canvasReset(appStateInternal="Main menu", addInfo=None):
    if addInfo is None:
        addInfo = ""
    global canvas, tabulka, db_connect, tabulkaOriginal, trieda
    stop = False
    canvas.delete("all")
    canvas.pack_forget()
    match appStateInternal:
        case "Main menu":
            canvas = tkinter.Canvas(width='300', height='400')
            canvas.pack()
            canvas.create_text(150, 75, text="Program na\nzasadací poriadok",
                               font="Arial {} bold".format(round(30 * scale)), justify="center")
            actionBoxes.clear()
            create_button(50, 150, "startButton", text="Štart", textOptions="bold", textScale=2, sizeX=200, sizeY=75)
            create_button(50, 250, "localMode", text="Lokálny", textScale=0.8, sizeX=87.5, sizeY=25)
            create_button(162.5, 250, "dbMode", text="Databáza", textScale=0.8, sizeX=87.5, sizeY=25)
            if len(addInfo) < 2:
                addInfo = ['', '']
            create_text_box(50, 300, "filePath-textBox-", sizeX=200, defaultText="Meno triedy", typedText=addInfo[0])
            create_text_box(50, 350, "group-textBox-", sizeX=200, defaultText="Meno skupiny", typedText=addInfo[1])
        case "Main App":
            canvas = tkinter.Canvas(width='650', height='695')
            canvas.pack()
            if addInfo is not None and addInfo[3]:
                if mode == "Database":
                    if 'psycopg2' not in sys.modules:
                        import psycopg2 as db_connect
                    try:
                        databaza = db_connect.connect(database="ZasadaciPoriadok",
                                                      user="postgres",
                                                      host='localhost',
                                                      port=5432)
                        kurzor = databaza.cursor()

                        if actionBoxes[addInfo[1]][1] == "":
                            kurzor.execute("""SELECT "Meno a Priezvisko", "Skupina" FROM public."ZoznamZiakov"
                                                    WHERE "Trieda" = '{}' and "Zahranicie" = false 
                                                    ORDER BY "Meno a Priezvisko" ASC;""".format(
                                actionBoxes[addInfo[0]][1].capitalize()))
                        else:
                            kurzor.execute("""SELECT "Meno a Priezvisko", "Skupina" FROM public."ZoznamZiakov"
                                                                                WHERE "Trieda" = '{}' and "Zahranicie" = false and "Skupina" ~ '{}'
                                                                                ORDER BY "Meno a Priezvisko" ASC;""".format(
                                actionBoxes[addInfo[0]][1].capitalize(), actionBoxes[addInfo[1]][1].capitalize()))
                        tabulka = kurzor.fetchall()

                    except db_connect.OperationalError:
                        canvasReset(appStateInternal="Error", addInfo=["Pripojenie k databáze zlyhalo",
                                                                       "Skúste skontrolovať svoje internetové pripojenie",
                                                                       "quit",
                                                                       ""])
                        stop = True
                else:
                    Nriadok = 0
                    zahranicie = False
                    try:
                        subor = open(
                            os.path.expanduser('~') + '/zasadacie_poriadky/StudentLists/{}.tssl'.format(
                                actionBoxes[addInfo[0]][1].capitalize()), 'r', encoding='utf-8')
                        meno = ''
                        for riadok in subor:
                            if Nriadok >= 0:
                                if not " -info" in riadok:
                                    meno = riadok.strip()
                                elif 'Z' in riadok:
                                    zahranicie = True
                                else:
                                    skupina = riadok.strip()[:3]
                                    if not zahranicie:
                                        if actionBoxes[addInfo[1]][1].capitalize() in skupina:
                                            tabulka.append((meno, skupina))
                                    zahranicie = False
                            Nriadok += 1
                    except FileNotFoundError:
                        tabulka = []
                trieda = [actionBoxes[addInfo[0]][1].capitalize(), actionBoxes[addInfo[1]][1].capitalize()]
            if not stop:
                if tabulka != []:
                    tabulkaOriginal = tabulka
                    actionBoxes.clear()
                    NZiakov = len(tabulka)
                    create_text_box(105, 10, "pocetStlpcov-textBox-", sizeX=40, sizeY=20, typedText='4')
                    canvas.create_text(50, 18, text="Počet stĺpcov:")
                    create_text_box(105, 40, "pocetRadov-textBox-", sizeX=40, sizeY=20,
                                    typedText=str(ceil(NZiakov / int(actionBoxes["pocetStlpcov-textBox-"][1]))))
                    canvas.create_text(50, 48, text="Počet radov:")
                    canvas.create_line(155, 0, 155, 700, width=2)
                    create_button(10, 460, 'restart', sizeX=135, textScale=1.2, text="Späť", textOptions="bold")
                    create_button(10, 520, 'add', sizeX=135, textScale=1.2, text="Pridať", textOptions="bold")
                    create_button(10, 580, 'regen', sizeX=135, textScale=1, text="Generovať znova",
                                  textOptions="bold")
                    create_button(10, 640, 'export', sizeX=135, textScale=1.2, text="Export", textOptions="bold")
                    generateTable(tabulka.copy(), NZiakov)
                else:
                    canvasReset(appStateInternal="Error", addInfo=["Trieda s takým menom neexistuje",
                                                                   "Skúste to prosím znova, so správnym menom triedy",
                                                                   "reset",
                                                                   [actionBoxes[addInfo[0]][1],
                                                                    actionBoxes[addInfo[1]][1]]])
        case "Error":
            canvas = tkinter.Canvas(width='320', height='100')
            canvas.pack()
            actionBoxes.clear()
            canvas.create_text(165, 20, text=str(addInfo[0]), font="Arial {} bold".format(round(18 * scale)))
            canvas.create_text(165, 45, text=str(addInfo[1]), font="Arial {}".format(round(12 * scale)))
            create_button(130, 65, str(addInfo[2]), sizeX=60, sizeY=25, text="Ok", textScale=1.25, moreInfo=addInfo[3])
        case "Addition":
            addList = [x for x in tabulkaOriginal if x not in tabulka]
            height = len(addList) * 75 + 175
            canvas = tkinter.Canvas(width=300, height=height)
            canvas.pack()
            actionBoxes.clear()
            canvas.create_text(150, 30, text='Pridávanie žiakov', font="Arial {} bold".format(round(25 * scale)),
                               anchor="center")
            NStudents = 0
            for student in addList:
                tags = "addition-" + student[0].replace(" ", "_")
                canvas.create_rectangle(10, NStudents * 75 + 60, 290, NStudents * 75 + 135, width=2, tags=tags)
                canvas.create_text(20, NStudents * 75 + 70, text=student[0], anchor="nw",
                                   font="Arial {} bold".format(round(20 * scale)), tags=tags + "_text")
                canvas.create_text(280, NStudents * 75 + 125, text=student[1], anchor="se",
                                   font="Arial {}".format(round(18 * scale)), tags=tags + "_text")
                actionBoxes.update(
                    {tags: [[20, NStudents * 75 + 60, 280, 75, canvas.itemcget(tags, "fill"),
                             canvas.itemcget(tags + "_text", "fill")], student]}
                )
                NStudents += 1
            create_button(50, height - 100, "table", sizeX=200, sizeY=75, text="Späť", textScale=2, textOptions='bold')
    triggerDefinition()


def create_button(x, y, tags, sizeX=100, sizeY=50, text="", textScale=1.0, textOptions="", moreInfo=""):
    global actionBoxes
    canvas.create_rectangle(x, y, x + sizeX, y + sizeY, tags=tags, width=2)
    canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=text,
                       font="Arial {} {}".format(round(15 * textScale * scale), textOptions), tags=tags + "_text")
    actionBoxes.update(
        {tags: [[x, y, sizeX, sizeY, canvas.itemcget(tags, "fill"), canvas.itemcget(tags + "_text", "fill")],
                moreInfo]})


def create_text_box(x, y, tags, sizeX=100, sizeY=25, defaultText="", typedText=""):
    global actionBoxes
    canvas.create_rectangle(x, y, x + sizeX, y + sizeY, fill="#999999", width=2, tags=tags)
    if typedText == "":
        canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=defaultText, tags=tags + "_text", justify="left")
    else:
        canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=typedText, tags=tags + "_text", justify="left")
    actionBoxes.update(
        {tags: [[x, y, sizeX, sizeY, canvas.itemcget(tags, "fill"), canvas.itemcget(tags + "_text", "fill")],
                typedText]})


def create_student(x, y, tags, sizeX=100, sizeY=100, name="", groups="", position=""):
    global draw
    if OS == 'posix':
        font = "Arial.ttf"
    else:
        font = "arial.ttf"
    groups = groups.split(", ")
    group = groups[0]
    if len(groups) > 1:
        for skupina in groups[1:]:
            group += ", " + skupina
    tagName = tags + "-" + name.replace(" ", "_")
    nameSplit = name.split(" ")
    name = ""
    for word in nameSplit:
        name += word + "\n "
    name = name[:-2]
    if sizeX > sizeY:
        sizeText = sizeY
    else:
        sizeText = sizeX
    canvas.create_rectangle(x, y, x + sizeX, y + sizeY, tags=tagName, width=2)
    canvas.create_text(round(x + (sizeX / 2)), round(y + (sizeY / 12) * 5), text=name, tags=tagName + '_text',
                       justify="center", font="Arial {}".format(str(round((sizeText / 3) / 2.25 * scale))))
    canvas.create_text(round(x + (sizeX / 2)), round(y + (sizeY / 12) * 10), text=group, tags=tagName + '_text2',
                       font="Arial {}".format(str(round((sizeText / 3) / 2.75 * scale))))
    canvas.create_rectangle(x + sizeX - sizeX / 9, y + sizeY / 9, x + sizeX - sizeX / 9 - sizeText / 9,
                            y + sizeY / 9 + sizeText / 9, outline='', tags=tagName + '_close')
    canvas.create_line(x + sizeX - sizeX / 9, y + sizeY / 9, x + sizeX - sizeX / 9 - sizeText / 9,
                       y + sizeY / 9 + sizeText / 9, fill='red', width=2, tags=tagName + '_close_text2')
    canvas.create_line(x + sizeX - sizeX / 9, y + sizeY / 9 + sizeText / 9, x + sizeX - sizeX / 9 - sizeText / 9,
                       y + sizeY / 9, fill='red', width=2, tags=tagName + '_close_text')
    draw.rectangle((200, 0, 800, 40), outline="black", width=2)
    draw.rectangle(((x - 155) * 2, (y + 20) * 2, (x + sizeX - 155) * 2, (y + sizeY + 20) * 2), outline="black", width=2)
    draw.text(((round(x + sizeX / 2) - 155) * 2, (round(y + (sizeY / 12) * 5) + 20) * 2), text=name, anchor="mm",
              font=ImageFont.truetype(font, round(sizeText / 3)), fill="black", align="center")
    draw.text(((round(x + sizeX / 2) - 155) * 2, (round(y + (sizeY / 12) * 10) + 20) * 2), text=group, anchor="mm",
              font=ImageFont.truetype(font, round(sizeText / 4)), fill="black")
    actionBoxes.update(
        {tagName + '_close': [[x + sizeX - sizeX / 9 - sizeText / 9, y + sizeY / 9, sizeText / 9, sizeText / 9,
                               canvas.itemcget(tagName + "_close", "fill"),
                               canvas.itemcget(tagName + "_close_text", "fill")], tagName]}
    )
    actionBoxes.update(
        {tagName: [[x, y, sizeX, sizeY, canvas.itemcget(tagName, "fill"), canvas.itemcget(tagName + "_text", "fill")],
                   group, position]})


def executeBox(tags):
    global canvas, binds, appState, textBox, tabulka, target, targetStudent, export, mode, trieda
    if binds != []:
        for bind in binds:
            canvas.unbind_all(bind)
            binds.remove(bind)
        binds = []
    textBox = tags
    match tags:
        case 'startButton':
            appState = 'Main App'
            canvasReset(appState, ['filePath-textBox-', 'group-textBox-', '', True])
        case 'localMode':
            mode = 'Local'
        case 'dbMode':
            mode = 'Database'
        case 'quit':
            quit()
        case 'reset':
            appState = 'Main menu'
            canvasReset(appState, actionBoxes[tags][1])
        case 'restart':
            appState = 'Main menu'
            tabulka = []
            canvasReset()
        case 'regen':
            generateTable(tabulka.copy(), len(tabulka))
        case 'add':
            appState = 'Addition'
            canvasReset(appState)
        case 'export':
            if not os.path.exists(os.path.expanduser('~') + "/zasadacie_poriadky"):
                os.mkdir(os.path.expanduser('~') + "/zasadacie_poriadky")
            cas = datetime.now()
            cas_a_trieda = cas.strftime("-%d:%m:%Y")
            for element in trieda:
                if element != '':
                    cas_a_trieda += "-" + element
            export.save(
                "{}/zasadacie_poriadky/zasadaci_poriadok{}.png".format(os.path.expanduser('~'),
                                                                       cas_a_trieda.replace(":", ";")))
            messagebox.showinfo(parent=canvas, title="Zasadací poriadok - export",
                                message="Zasadací poriadok exportovaný do:\n{}/zasadacie_poriadky/zasadaci_poriadok{}.png".format(
                                    os.path.expanduser('~'), cas_a_trieda.replace(":", ";")))
        case 'table':
            appState = "Main App"
            canvasReset(appState, ['', '', '', False])
    if '-textBox-' in tags:
        canvas.bind_all("<Key>", keyPressed)
        binds.append("<Key>")
    elif 'class-' in tags:
        if "_close" in tags:
            tags = tags.removesuffix("_close")
            tabulka = [x for x in tabulka if x != (tags.removeprefix("class-").replace("_", " "), actionBoxes[tags][1])]
            generateTable(tabulka.copy(), len(tabulka))
        else:
            if target:
                exchange(tags, targetStudent)
                target = False
            else:
                targetStudent = tags
                target = True
    elif 'addition-' in tags:
        tabulka.append(actionBoxes[tags][1])
        canvasReset(appState, ['', '', '', False])


def keyPressed(event):
    global textBox
    if event.char != "" and not '\x08' in event.char and not '\r' in event.char:
        char = event.char
        actionBoxes.update({textBox: [actionBoxes[textBox][0], actionBoxes[textBox][1] + char]})
        canvas.itemconfig(textBox + "_text", text=actionBoxes[textBox][1])
    else:
        match event.keysym:
            case "Return":
                executeBox("")
            case "BackSpace":
                actionBoxes.update({textBox: [actionBoxes[textBox][0], actionBoxes[textBox][1][:-1]]})
                canvas.itemconfig(textBox + "_text", text=actionBoxes[textBox][1])
    if textBox == "pocetStlpcov-textBox-" or textBox == "pocetRadov-textBox-":
        generateTable(tabulka.copy(), len(tabulka))


def generateTable(use_tabulka, NZiakov):
    global actionBoxes, export, draw
    export = Image.new("RGB", (1000, 1440), "white")
    draw = ImageDraw.Draw(export)
    for box in actionBoxes.copy():
        if "class-" in box:
            canvas.delete(box)
            canvas.delete(box + "_text")
            canvas.delete(box + "_text2")
            actionBoxes.pop(box)
    canvas.delete("class-warning")
    dimensionX = [165, 645]
    dimensionY = [10, 690]
    sizeX = dimensionX[1] - dimensionX[0]
    sizeY = dimensionY[1] - dimensionY[0]
    try:
        NCols = int(actionBoxes['pocetStlpcov-textBox-'][1])
    except ValueError:
        NCols = 4
    try:
        NRows = int(actionBoxes['pocetRadov-textBox-'][1])
    except ValueError:
        NRows = ceil(NZiakov / NCols)
    if NCols == 0:
        NCols = 4
    if NRows == 0:
        NRows = ceil(NZiakov / NCols)
    for i in range(NZiakov):
        if len(use_tabulka) > 1:
            meno = use_tabulka[randrange(0, len(use_tabulka))]
            use_tabulka.remove(meno)
        elif len(use_tabulka) == 1:
            meno = use_tabulka[0]
            use_tabulka.remove(meno)
        else:
            meno = ""
        if not floor(dimensionY[0] + (sizeY / NRows) * floor(i / NCols)) >= dimensionY[1]:
            create_student(floor(dimensionX[0] + (sizeX / NCols) * (i % NCols)),
                           floor(dimensionY[0] + (sizeY / NRows) * floor(i / NCols)),
                           "class", sizeX=round(sizeX / NCols), sizeY=round(sizeY / NRows), name=meno[0],
                           groups=meno[1],
                           position=[chr(65 + i % NCols), floor(i / NCols) + 1])
        else:
            canvas.create_text(77.5, 100,
                               text="!! VAROVANIE !!\nTabuľka nie je \ndostatočne veľká,\nna daný počet žiakov",
                               fill='Red', tags="class-warning", justify="center")


def exchange(student1, student2):
    global actionBoxes, canvas
    temp = actionBoxes[student1]
    actionBoxes.update({student1: actionBoxes[student2]})
    actionBoxes.update({student2: temp})
    temp = actionBoxes[student1 + "_close"]
    actionBoxes.update({student1 + "_close": actionBoxes[student2 + "_close"]})
    actionBoxes.update({student2 + "_close": temp})
    canvas.move(student1, actionBoxes[student1][0][0] - actionBoxes[student2][0][0],
                actionBoxes[student1][0][1] - actionBoxes[student2][0][1])
    canvas.move(student1 + "_text", actionBoxes[student1][0][0] - actionBoxes[student2][0][0],
                actionBoxes[student1][0][1] - actionBoxes[student2][0][1])
    canvas.move(student1 + "_text2", actionBoxes[student1][0][0] - actionBoxes[student2][0][0],
                actionBoxes[student1][0][1] - actionBoxes[student2][0][1])
    canvas.itemconfig(student2, fill="#d0d0d0")
    canvas.itemconfig(student2 + "_text", fill="#2F2F2F")
    canvas.itemconfig(student2 + "_text2", fill="#2F2F2F")
    canvas.itemconfig(student1, fill=actionBoxes[student1][0][4])
    canvas.itemconfig(student1 + "_text", fill=actionBoxes[student1][0][5])
    canvas.itemconfig(student1 + "_text2", fill=actionBoxes[student1][0][5])
    canvas.move(student1 + "_close", actionBoxes[student1][0][0] - actionBoxes[student2][0][0],
                actionBoxes[student1][0][1] - actionBoxes[student2][0][1])
    canvas.move(student1 + "_close_text", actionBoxes[student1][0][0] - actionBoxes[student2][0][0],
                actionBoxes[student1][0][1] - actionBoxes[student2][0][1])
    canvas.move(student1 + "_close_text2", actionBoxes[student1][0][0] - actionBoxes[student2][0][0],
                actionBoxes[student1][0][1] - actionBoxes[student2][0][1])
    canvas.move(student2, actionBoxes[student2][0][0] - actionBoxes[student1][0][0],
                actionBoxes[student2][0][1] - actionBoxes[student1][0][1])
    canvas.move(student2 + "_text", actionBoxes[student2][0][0] - actionBoxes[student1][0][0],
                actionBoxes[student2][0][1] - actionBoxes[student1][0][1])
    canvas.move(student2 + "_text2", actionBoxes[student2][0][0] - actionBoxes[student1][0][0],
                actionBoxes[student2][0][1] - actionBoxes[student1][0][1])
    canvas.move(student2 + "_close", actionBoxes[student2][0][0] - actionBoxes[student1][0][0],
                actionBoxes[student2][0][1] - actionBoxes[student1][0][1])
    canvas.move(student2 + "_close_text", actionBoxes[student2][0][0] - actionBoxes[student1][0][0],
                actionBoxes[student2][0][1] - actionBoxes[student1][0][1])
    canvas.move(student2 + "_close_text2", actionBoxes[student2][0][0] - actionBoxes[student1][0][0],
                actionBoxes[student2][0][1] - actionBoxes[student1][0][1])


# Definícia triggerov
def triggerDefinition():
    global canvas
    canvas.bind('<Motion>', mouseMove)
    canvas.bind('<Button-1>', LMBClick)


def mouseMove(event):
    mouseX = event.x
    mouseY = event.y
    for box in actionBoxes:
        if (
                actionBoxes[box][0][0] < mouseX < actionBoxes[box][0][0] + actionBoxes[box][0][2] and
                actionBoxes[box][0][1] < mouseY < actionBoxes[box][0][1] + actionBoxes[box][0][3]):
            canvas.itemconfig(box, fill="#d0d0d0")
            canvas.itemconfig(box + "_text", fill="#2F2F2F")
            canvas.itemconfig(box + "_text2", fill="#2F2F2F")
        else:
            canvas.itemconfig(box, fill=actionBoxes[box][0][4])
            canvas.itemconfig(box + "_text", fill=actionBoxes[box][0][5])
            canvas.itemconfig(box + "_text2", fill=actionBoxes[box][0][5])


def LMBClick(event):
    mouseX = event.x
    mouseY = event.y
    for box in actionBoxes.copy():
        if (
                actionBoxes[box][0][0] < mouseX < actionBoxes[box][0][0] + actionBoxes[box][0][2] and
                actionBoxes[box][0][1] < mouseY < actionBoxes[box][0][1] + actionBoxes[box][0][3]):
            executeBox(box)
            break
        else:
            executeBox("")


# Inicializácia celého programu
_init()
root.mainloop()
