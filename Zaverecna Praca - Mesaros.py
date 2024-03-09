# Importovanie modulov
import math
import tkinter

import psycopg2 as db_connect

# Definícia globálnych premenných
root = tkinter.Tk()
canvas = tkinter.Canvas()
appState = "Main menu"
actionBoxes = {}
binds = []
tabulka = []
textBox = ""


# Definícia funkcií
def _init():
    global canvas, appState
    # Reset premenných
    canvas = tkinter.Canvas()
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
            canvas = tkinter.Canvas(width='300', height='500')
            canvas.pack()
            canvas.create_text(150, 75, text="Program na\nzasadací poriadok", font="Arial 30 bold", justify="center")
            actionBoxes.clear()
            create_button(50, 150, "startButton", text="Štart", textOptions="bold", textScale=2, sizeX=200, sizeY=75)
            create_text_box(50, 250, "filePath -textBox- ", sizeX=200, defaultText="Meno triedy", typedText=addInfo)
        case "Main App":
            canvas = tkinter.Canvas(width='1000', height='700')
            canvas.pack()
            if addInfo != "":
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
            if not stop:
                if tabulka != []:
                    actionBoxes.clear()
                    i = len(tabulka) + 1
                    create_text_box(105, 10, "pocetStlpcov -textBox- ", sizeX=40, sizeY=20, typedText='4')
                    canvas.create_text(50, 18, text="Počet stĺpcov:")
                    create_text_box(105, 40, "pocetRadov -textBox- ", sizeX=40, sizeY=20,
                                    typedText=str(math.ceil(i / int(actionBoxes["pocetStlpcov"][1]))))
                    canvas.create_text(50, 48, text="Počet radov:")
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


def executeBox(tags):
    global canvas, binds, appState, textBox
    if binds != []:
        for bind in binds:
            canvas.unbind_all(bind)
            binds.remove(bind)
        binds = []
    textBox = tags
    match tags:
        case 'startButton':
            appState = 'Main App'
            canvasReset(appState, 'filePath')
        case 'quit':
            quit()
        case 'reset':
            appState = 'Main menu'
            canvasReset(appState, actionBoxes[tags][1])
    if tags.contains(" -textBox- "):
        canvas.bind_all("<Key>", keyPressed)
        binds.append("<Key>")


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


# Definícia triggerov
def triggerDefinition():
    global canvas
    canvas.bind('<Motion>', mouseMove)
    canvas.bind('<Button-1>', LMBClick)


def mouseMove(event):
    mouseX = event.x
    mouseY = event.y
    canvas.itemconfig("mousePos", text="{}, {}".format(mouseX, mouseY))
    for box in actionBoxes:
        if (
                actionBoxes[box][0][0] < mouseX < actionBoxes[box][0][0] + actionBoxes[box][0][2] and
                actionBoxes[box][0][1] < mouseY < actionBoxes[box][0][1] + actionBoxes[box][0][3]):
            canvas.itemconfig(box, fill="#d0d0d0")
            canvas.itemconfig(box + "_text", fill="#2F2F2F")
        else:
            canvas.itemconfig(box, fill=actionBoxes[box][0][4])
            canvas.itemconfig(box + "_text", fill=actionBoxes[box][0][5])


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
