# Importovanie modulov
import tkinter
from math import *
from random import *

from PIL import Image, ImageDraw, ImageFont

# Definícia globálnych premenných
root = tkinter.Tk()
canvas = tkinter.Canvas()
appState = "Main menu"
actionBoxes = {}
binds = []
tabulka = []
textBox = ""
target = False
export = Image.new("RGB", (500, 700), "white")
draw = ImageDraw.Draw(export)
targetStudent = ""
mode = "database".capitalize()  # local pre lokalny testovaci mod a database pre mod prace s databazou

if mode == "Database":
    import psycopg2 as db_connect


# Definícia funkcií
def _init():
    global canvas, appState
    # Reset premenných
    appState = "Main menu"

    # Nastavenie okna
    root.resizable(False, False)
    root.title("Zasadací poriadok")

    # Inicializácia plátna
    canvas.pack()
    canvasReset()


def canvasReset(appStateInternal="Main menu", addInfo=None):
    if addInfo is None:
        addInfo = ""
    global canvas, tabulka
    stop = False
    canvas.delete("all")
    canvas.pack_forget()
    match appStateInternal:
        case "Main menu":
            canvas = tkinter.Canvas(width='300', height='320')
            canvas.pack()
            canvas.create_text(150, 75, text="Program na\nzasadací poriadok", font="Arial 30 bold", justify="center")
            actionBoxes.clear()
            create_button(50, 150, "startButton", text="Štart", textOptions="bold", textScale=2, sizeX=200, sizeY=75)
            create_text_box(50, 250, "filePath-textBox-", sizeX=200, defaultText="Meno triedy", typedText=addInfo)
        case "Main App":
            canvas = tkinter.Canvas(width='650', height='695')
            canvas.pack()
            if addInfo != "":
                if mode == "Database":
                    try:
                        databaza = db_connect.connect(database="ZasadaciPoriadok",
                                                      user="postgres",
                                                      host='localhost',
                                                      port=5432)
                        kurzor = databaza.cursor()

                        kurzor.execute("""SELECT "Meno a Priezvisko", "Skupina" FROM public."ZoznamZiakov"
                                                WHERE "Trieda" = '{}' and "Zahranicie" = false
                                                ORDER BY "Meno a Priezvisko" ASC;""".format(
                            actionBoxes[addInfo][1].capitalize()))
                        tabulka = kurzor.fetchall()
                    except db_connect.OperationalError:
                        canvasReset(appStateInternal="Error", addInfo=["Pripojenie k databáze zlyhalo",
                                                                       "Skúste skontrolovať svoje internetové pripojenie",
                                                                       "quit",
                                                                       ""])
                        stop = True
                else:
                    tabulka = [('Brňáková Ema', 'Aj2'), ('Drahoš Alex', 'Aj2'), ('Fajnor Ján', 'Aj2'),
                               ('Fejda Marko', 'Aj1'), ('Filc Marian', 'Aj1'), ('Gižická Tereza', 'Aj1'),
                               ('Golian Matej', 'Aj2'), ('Hitzingerová Silvia', 'Aj2'), ('Horská Barbora', 'Aj1'),
                               ('Horská Veronika', 'Aj1'), ('Katrincová Tereza', 'Aj1'), ('Kekeši Filip', 'Aj1'),
                               ('Kočan Maximilián', 'Aj2'), ('Lauko Pavol', 'Aj2'), ('Luknárová Hana', 'Aj1'),
                               ('Melioris Mia', 'Aj1'), ('Mésároš Tomáš', 'Aj2'), ('Navarčíková Natália', 'Aj1'),
                               ('Pavlíková Liana', 'Aj1'), ('Peschl Jakub', 'Aj2'), ('Pongrácová Petra Ella', 'Aj2'),
                               ('Salner Leon', 'Aj1'), ('Skoček Ilja', 'Aj2'), ('Vajdová Ina', 'Aj1'),
                               ('Zaťko Pavol', 'Aj2')]
            if not stop:
                if tabulka != []:
                    actionBoxes.clear()
                    NZiakov = len(tabulka)
                    create_text_box(105, 10, "pocetStlpcov-textBox-", sizeX=40, sizeY=20, typedText='4')
                    canvas.create_text(50, 18, text="Počet stĺpcov:")
                    create_text_box(105, 40, "pocetRadov-textBox-", sizeX=40, sizeY=20,
                                    typedText=str(ceil(NZiakov / int(actionBoxes["pocetStlpcov-textBox-"][1]))))
                    canvas.create_text(50, 48, text="Počet radov:")
                    canvas.create_line(155, 0, 155, 700, width=2)
                    create_button(10, 640, 'export', sizeX=135, textScale=1.2, text="Export", textOptions="bold")
                    create_button(10, 580, 'regen', sizeX=135, textScale=1, text="Generovať znova",
                                  textOptions="bold")
                    generateTable(tabulka.copy(), NZiakov)
                else:
                    canvasReset(appStateInternal="Error", addInfo=["Trieda s takým menom neexistuje",
                                                                   "Skúste to prosím znova, so správnym menom triedy",
                                                                   "reset",
                                                                   actionBoxes[addInfo][1]])
        case "Error":
            canvas = tkinter.Canvas(width='320', height='100')
            canvas.pack()
            actionBoxes.clear()
            canvas.create_text(165, 20, text=str(addInfo[0]), font="Arial 18 bold")
            canvas.create_text(165, 45, text=str(addInfo[1]), font="Arial 12")
            create_button(130, 65, str(addInfo[2]), sizeX=60, sizeY=25, text="Ok", textScale=1.25, moreInfo=addInfo[3])
    triggerDefinition()


def create_button(x, y, tags, sizeX=100, sizeY=50, text="", textScale=1.0, textOptions="", moreInfo=""):
    global actionBoxes
    canvas.create_rectangle(x, y, x + sizeX, y + sizeY, tags=tags, width=2)
    canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=text,
                       font="Arial {} {}".format(round(15 * textScale), textOptions), tags=tags + "_text")
    actionBoxes.update(
        {tags: [[x, y, sizeX, sizeY, canvas.itemcget(tags, "fill"), canvas.itemcget(tags + "_text", "fill")],
                moreInfo]})


def create_text_box(x, y, tags, sizeX=100, sizeY=25, defaultText="", typedText=""):
    global actionBoxes
    canvas.create_rectangle(x, y, x + sizeX, y + sizeY, fill="#808080", width=2, tags=tags)
    if typedText == "":
        canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=defaultText, tags=tags + "_text", justify="left")
    else:
        canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=typedText, tags=tags + "_text", justify="left")
    actionBoxes.update(
        {tags: [[x, y, sizeX, sizeY, canvas.itemcget(tags, "fill"), canvas.itemcget(tags + "_text", "fill")],
                typedText]})


def create_student(x, y, tags, sizeX=100, sizeY=100, name="", groups="", position=""):
    global draw
    font = ImageFont.truetype("Arial.ttf")
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
                       justify="center", font="Arial {}".format(str(round((sizeText / 3) / 2.25))))
    canvas.create_text(round(x + (sizeX / 2)), round(y + (sizeY / 12) * 10), text=group, tags=tagName + '_text2',
                       font="Arial {}".format(str(round((sizeText / 3) / 2.75))))
    canvas.create_rectangle(x + sizeX - sizeX / 9, y + sizeY / 9, x + sizeX - sizeX / 9 - sizeText / 9,
                       y + sizeY / 9 + sizeText / 9, outline='', tags=tagName + '_close')
    canvas.create_line(x + sizeX - sizeX / 9, y + sizeY / 9, x + sizeX - sizeX / 9 - sizeText / 9,
                       y + sizeY / 9 + sizeText / 9, fill='red', width=2, tags=tagName + '_close_text2')
    canvas.create_line(x + sizeX - sizeX / 9, y + sizeY / 9 + sizeText / 9, x + sizeX - sizeX / 9 - sizeText / 9,
                        y + sizeY / 9, fill='red', width=2, tags=tagName + '_close_text')
    draw.rectangle((x - 155, y, x + sizeX - 155, y + sizeY), outline="black", width=2)
    draw.text((round(x + sizeX / 2) - 155, round(y + (sizeY / 12) * 5)),text=name,anchor="mm", font=font, font_size=round((sizeText / 3) / 2.25), fill="black", justify="center")
    draw.text((round(x + sizeX / 2) - 155, round(y + (sizeY / 12) * 10)),text=group,anchor="mm", font=font, font_size=round((sizeText / 3) / 2.75), fill="black")
    actionBoxes.update(
        {tagName + '_close' : [[x + sizeX - sizeX / 9 - sizeText / 9, y + sizeY / 9, sizeText/9, sizeText/9, canvas.itemcget(tagName + "_close", "fill"), canvas.itemcget(tagName + "_close_text", "fill")], tagName]}
    )
    actionBoxes.update(
        {tagName: [[x, y, sizeX, sizeY, canvas.itemcget(tagName, "fill"), canvas.itemcget(tagName + "_text", "fill")],
                   group, position]})


def executeBox(tags):
    global canvas, binds, appState, textBox, tabulka, target, targetStudent, export
    if binds != []:
        for bind in binds:
            canvas.unbind_all(bind)
            binds.remove(bind)
        binds = []
    textBox = tags
    match tags:
        case 'startButton':
            appState = 'Main App'
            canvasReset(appState, 'filePath-textBox-')
        case 'quit':
            quit()
        case 'reset':
            appState = 'Main menu'
            canvasReset(appState, actionBoxes[tags][1])
        case 'regen':
            generateTable(tabulka.copy(), len(tabulka))
        case 'export':
            export.save("test.png")
    if '-textBox-' in tags:
        canvas.bind_all("<Key>", keyPressed)
        binds.append("<Key>")
    elif 'class-' in tags:
        if "_close" in tags:
            tags = tags.removesuffix("_close")
            canvas.delete(tags)
            canvas.delete(tags + "_text")
            canvas.delete(tags + "_text2")
            canvas.delete(tags + "_close")
            canvas.delete(tags + "_close_text")
            canvas.delete(tags + "_close_text2")
            tabulka = [x for x in tabulka if x!= (tags.removeprefix("class-").replace("_", " "),actionBoxes[tags][1])]
            generateTable(tabulka.copy(), len(tabulka))
        else:
            if target:
                exchange(tags, targetStudent)
                target = False
            else:
                targetStudent = tags
                target = True


def keyPressed(event):
    global textBox
    if event.char != "":
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
    export = Image.new("RGB", (500, 700), "white")
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
        if not round(dimensionY[0] + (sizeY / NRows) * floor(i / NCols)) >= dimensionY[1]:
            create_student(round(dimensionX[0] + (sizeX / NCols) * (i % NCols)),
                           round(dimensionY[0] + (sizeY / NRows) * floor(i / NCols)),
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
    temp = actionBoxes[student1+"_close"]
    actionBoxes.update({student1+"_close": actionBoxes[student2+"_close"]})
    actionBoxes.update({student2+"_close":temp})
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
