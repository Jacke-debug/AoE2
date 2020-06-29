import numpy as np 
from PIL import Image, ImageGrab, ImageTk
import pytesseract
from scipy.ndimage import gaussian_filter
import itertools
import tkinter as tk
def interpertText(text):
    text = text.replace(",", "")
    text = text.replace(".", "")
    players = []
    elo = []
    for row in text.splitlines():
        if (not not row):
            if  (row.startswith("Close") or row.startswith("Open")):
                elo.append(int(0))
                players.append("Closed/Open")
            else:
                try:
                    elo.append(int(row[1:5]))
                except:
                    elo.append(int(0))
                players.append(row[7:])
    return (players, elo)

def manipulateColor(img):
    # RGB representation
    greenText = np.logical_and(img[:, :,0]>180, img[:, :, 1]<20)
    redText = img[:, :, 1]>180
    allText = np.logical_or(greenText, redText)

    # create a new image with same size as original
    image = img
    image[:, :, 0] = (1-allText)*255
    image[:, :, 1] = (1-allText)*255
    image[:, :, 2] = (1-allText)*255
    #image = gaussian_filter(image, sigma=0.1)
    return image

def readText(img):
    # Read text from image
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:/Program Files (x86)/Tesseract-OCR/tesseract")
    text = pytesseract.image_to_string(img,  config='--psm 11')
    return text

def optimalTeams(players, elo):
    elo = np.array(elo)
    nop = len(elo)
    teamSize = int(nop/2)
    halfElo = elo.sum()/2
    prevBest = halfElo
    bestTeam = range(teamSize)
    eloDiff = 0
    for combination in itertools.combinations(range(nop), teamSize):
        teamElo = 0
        for index in combination:
            teamElo = teamElo + elo[index]
    
        teamDiff = abs(halfElo-teamElo)
        if teamDiff<prevBest:
            prevBest = teamDiff
            bestTeam = combination
            eloDiff = int(teamDiff*2)

    team1Index = set(bestTeam)
    team2Index = set(range(nop))-team1Index

    my_str = "Team 1:"
    for i in team1Index:
        my_str = my_str + "\'"+players[i] + "\' "
    
    my_str = my_str + "   Team 2:"
    for i in team2Index:
        my_str = my_str + "\'"+players[i] + "\' "
    
    try:
        playerDiff = int(eloDiff/teamSize)
    except ZeroDivisionError:
        playerDiff = 0
    
    my_str = my_str + "\nElo diff between teams: " + str(eloDiff) + " \nElo diff per player: " + str(playerDiff)
    return my_str

class GetBoundingBox(tk.Toplevel):
    def __init__(self, master):
        super().__init__()
        self.father = master
        self.withdraw()
        self.attributes('-fullscreen', True)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both",expand=True)

        image = ImageGrab.grab()
        self.image = ImageTk.PhotoImage(image)
        self.photo = self.canvas.create_image(0,0,image=self.image,anchor="nw")

        self.x, self.y = 0, 0
        self.rect, self.start_x, self.start_y = None, None, None
        self.deiconify()

        self.canvas.tag_bind(self.photo,"<ButtonPress-1>", self.on_button_press)
        self.canvas.tag_bind(self.photo,"<B1-Motion>", self.on_move_press)
        self.canvas.tag_bind(self.photo,"<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)
    
    def retry_event(self):
        # start a new instance of the class
        self.withdraw()
        my_gui.capture_event(my_gui)  
        
    def confirm_event(self):
        img = np.array(self.img)
        refinedImage = manipulateColor(img)
        text = readText(refinedImage)
        players, elo = interpertText(text)
        # clean previous values and write text to boxes
        mainApplication.reset_event(my_gui)
        for i in range(len(players)):
            my_gui.eloEditId[i].delete(0, "end")
            my_gui.eloEditId[i].insert(0, elo[i])
            my_gui.nameEditId[i].delete(0, "end")
            my_gui.nameEditId[i].insert(0, players[i])
        self.withdraw()

    def on_button_release(self, event):
        bbox = self.canvas.bbox(self.rect)
        self.withdraw()
        self.img = ImageGrab.grab(bbox)
        self.new_image = ImageTk.PhotoImage(self.img)
        self.attributes('-fullscreen', False)
        self.title("Image grabbed")
        self.canvas.destroy()
        self.deiconify()
        tk.Label(self,image=self.new_image).pack()
        tk.Button(self, text = "Retry", command = self.retry_event).pack()
        tk.Button(self, text = "Confirm", command = self.confirm_event).pack()
 
class mainApplication:
    def __init__(self, master):
        #self.master = master
        master.title("AoE2 AutoBalance")

        # column headders
        self.label = tk.Label(master, text=f"Elo:")
        self.label.grid(row=0, column=1)
        self.label = tk.Label(master, text=f"Name:")
        self.label.grid(row=0, column=2)
        self.nameEditId = []
        self.eloEditId = []
        # Create one line for each possible player
        for i in range(8):
            playerN = i+1
            playerLabel = tk.Label(master, text=f"Player {playerN}")
            playerLabel.grid(row=i+1, column=0)
            eloEdit = tk.Entry(master, width=5)
            eloEdit.grid(row=i+1, column=1)
            self.eloEditId.append(eloEdit)
            nameEdit = tk.Entry(master, width=15)
            nameEdit.grid(row=i+1, column=2,)
            self.nameEditId.append(nameEdit)
        
        # Create action buttons at the bottom
        self.closeButton = tk.Button(master, text="Reset", command = self.reset_event)
        self.closeButton.grid(row=9, column=0)
        self.captureButton = tk.Button(master, text="Capture Players", command = self.capture_event)
        self.captureButton.grid(row=9, column=1)
        self.calcButton = tk.Button(master, text="Balance Teams", command = self.calc_event)
        self.calcButton.grid(row=9, column=2)

        self.resultText = tk.Text(master,  width = 60, height=4)
        self.resultText.grid(row=10, columnspan=3)

        # start window from clean slate
        self.reset_event()

    def reset_event(self):
        # clean previous values
        self.resultText.delete('1.0', tk.END)
        self.resultText.insert('1.0', " 1. Use the Capture players button or enter elo manually \n 2. Click Balance team to calcualte optimal setup \n 3. Copy output from here and paste in chat")
        for i in range(8):
            k = i+1
            self.eloEditId[i].delete(0, "end")
            self.nameEditId[i].delete(0, "end")
            self.eloEditId[i].insert(0, "0")
            self.nameEditId[i].insert(0, f"P{k}")

    def capture_event(self, *args):
        # GetBoundingBoxSavesImage
        GetBoundingBox(self)

    def calc_event(self):
        playerList = []
        eloList = []
        for i in range(8):
            if not int(self.eloEditId[i].get()) == 0:
                playerList.append(self.nameEditId[i].get())
                eloList.append(int(self.eloEditId[i].get()))
        
        resultString = optimalTeams(playerList, eloList)
        self.resultText.delete('1.0', tk.END)
        self.resultText.insert('1.0', resultString)


root = tk.Tk()
my_gui = mainApplication(root)
root.mainloop()
