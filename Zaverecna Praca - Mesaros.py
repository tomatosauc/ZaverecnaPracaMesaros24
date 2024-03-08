# Importovanie modulov
import tkinter

import psycopg2 as db_connect

# Definícia globálnych premenných
root = tkinter.Tk()
canvas = tkinter.Canvas()
appState = "Main menu"
actionBoxes = {}
binds = []
tabulka = []


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


def canvasReset(appStateInternal="Main menu", addInfo=''):
    global canvas, tabulka
    stop = False
    canvas.delete("all")
    canvas.destroy()
    if appStateInternal == "Main menu":
        canvas = tkinter.Canvas(width='300', height='500')
        canvas.pack()
        canvas.create_text(150, 75, text="Program na\nzasadací poriadok", font="Arial 30 bold", justify="center")
        actionBoxes.clear()
        create_button(50, 150, text="Štart", textOptions="bold", textScale=2, sizeX=200, sizeY=75, tags="startButton")
        create_text_box(50, 250, "filePath", sizeX=200, defaultText="Insert file path here")
    elif appStateInternal == "Main App":
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
                canvasReset(appStateInternal="Error", addInfo=["Pripojenie k databáze zlyhalo","Skúste skontrolovať svoje internetové pripojenie"])
                stop = True
        if not stop:
            actionBoxes.clear()
            create_text_box(10, 10, "pocetRadov", sizeX=100, sizeY=20, defaultText="Počet radov")
            i = 0
            for riadok in tabulka:
                print(riadok)
                i += 1
            print(i)
    elif appStateInternal == "Error":
        canvas = tkinter.Canvas(width='320', height='100')
        canvas.pack()
        actionBoxes.clear()
        canvas.create_text(165, 20, text=addInfo[0], font="Arial 18 bold")
        canvas.create_text(165, 45, text=addInfo[1], font="Arial 12")
        create_button(130, 65, "quit", sizeX=60, sizeY=25, text="Ok", textScale=1.25)
    triggerDefinition()


def create_button(x, y, tags, sizeX=100, sizeY=50, text="", textScale=1.0, textOptions=""):
    global actionBoxes
    canvas.create_rectangle(x, y, x + sizeX, y + sizeY, tags=tags, width=2)
    canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=text,
                       font="Arial {} {}".format(round(15 * textScale), textOptions), tags=tags + "_text")
    actionBoxes.update(
        {tags: [[x, y, sizeX, sizeY, canvas.itemcget(tags, "fill"), canvas.itemcget(tags + "_text", "fill")]]})


def create_text_box(x, y, tags, sizeX=100, sizeY=25, defaultText=""):
    global actionBoxes
    canvas.create_rectangle(x, y, x + sizeX, y + sizeY, fill="#808080", width=2, tags=tags)
    canvas.create_text(x + (sizeX / 2), y + (sizeY / 2), text=defaultText, tags=tags + "_text", justify="left")
    actionBoxes.update(
        {tags: [[x, y, sizeX, sizeY, canvas.itemcget(tags, "fill"), canvas.itemcget(tags + "_text", "fill")], ""]})


def writeToBox(tags, text):
    canvas.itemconfig(tags + "_text", text=text)


def executeBox(tags):
    global canvas, binds, appState
    match tags:
        case 'filePath':
            canvas.bind_all('<Key>', filePathPressed)
            binds.append('<Key>')
            return False
        case 'startButton':
            appState = 'Main App'
            canvasReset(appState, 'filePath')
            return True
        case 'quit':
            quit()
        case _:
            if binds != []:
                for bind in binds:
                    canvas.bind_all(bind, "")
                    binds.remove(bind)


def filePathPressed(event):
    if event.char != "":
        char = event.char
        actionBoxes.update({"filePath": [actionBoxes["filePath"][0], actionBoxes["filePath"][1] + char]})
        canvas.itemconfig("filePath_text", text=actionBoxes["filePath"][1])
    else:
        match event.keysym:
            case "Return":
                executeBox("")
            case "BackSpace":
                actionBoxes.update({"filePath": [actionBoxes["filePath"][0], actionBoxes["filePath"][1][:-1]]})
                canvas.itemconfig("filePath_text", text=actionBoxes["filePath"][1])


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
            if executeBox(box):
                break
        else:
            executeBox("")


# Inicializácia celého programu
_init()
root.mainloop()
