import tkinter as tk
import sys
import trace
import os
from os import path
from tkinter import ttk, messagebox
from tkinter.constants import BOTH, HORIZONTAL, LEFT, SUNKEN, VERTICAL
from tkinter.ttk import Progressbar, Style
import tkinter.font as font
from parsing import Parser
from threading import Thread
from tkinter import *
from multiprocessing import Process
import pathlib
import io 
from ftplib import FTP


class thread_with_trace(Thread):
  def __init__(self, *args, **keywords):
    Thread.__init__(self, *args, **keywords)
    self.killed = False
  
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run      
    Thread.start(self)
  
  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
  
  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None
  
  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace
  
  def kill(self):
    self.killed = True


def createData():
    if (not path.exists("./Data")):
        os.mkdir("./Data") 


def traverse_dir(parent,path):
    global nouveauxGlobal
    global modifiesGlobal
    for d in os.listdir(path):
        full_path=os.path.join(path,d)
        isdir = os.path.isdir(full_path)
        if(os.path.isfile(full_path)):
            chunks = full_path.split('Data')
            my_string = ("./Data" + chunks[1])
            if(my_string in nouveauxGlobal):
                id=tv.insert(parent,'end',text=d,open=False, tag=('nouveau',))
            elif(my_string in modifiesGlobal):
                id=tv.insert(parent,'end',text=d,open=False, tag=('modif',))
            else:
                id=tv.insert(parent,'end', text=d, open=False)
            liste.append(full_path)
        else:
            id=tv.insert(parent,'end',text=d,open=False)
        if isdir:
            traverse_dir(id,full_path)
            

def update_arbo():
    tv.delete(*tv.get_children())
    createData()
    directory='Data'
    tv.heading('#0',text='Dir：'+directory,anchor='w')
    mypath=os.path.abspath(directory)
    chunks = mypath.split('Data')
    new = "Data/" + chunks[1]
    node=tv.insert('','end',text=new,open=True)
    traverse_dir(node,mypath)


def parsing():
    global parser
    global nouveauxGlobal
    global modifiesGlobal
    global inchangesGlobal



    # parser = Parser(fileToParse)
    progress['maximum'] = parser.nc_to_treat
    parsing_button[ "state" ] = "disabled"
    stop_button["state"] = 'normal'
    reprendre_button["state"] = 'disabled' 


    while(parser.nc_treat != parser.nc_to_treat):
        global stop_thread, nouveaux, modifies, inchanges
        if stop_thread:
            break


        if parser.suppr == 1:
            supprText = "Nombre de NC deja parsés n'ayant plus de CDS (supprimés) : " + str(parser.nc_supprimes)
        else:
            supprText = "Nombre de NC deja parsés n'ayant plus de CDS : " + str(parser.nc_supprimes)


        nameOrgaLabel['text'] = "Organisme en cours de traitement :\n" + parser.next_orga_to_treat.prefix
        pourcent['text'] = str(parser.nc_treat) + "/" + str(parser.nc_to_treat)
        nouveauxLabel['text'] = "Nombre de nouveaux NC : " + str(parser.nc_nouveaux)
        modifiesLabel['text'] = "Nombre de NC modifiés : " + str(parser.nc_modifies)
        inchangesLabel['text'] = "Nombre de NC non modifiés : " + str(parser.nc_inchanges)
        supprimesLabel['text'] = supprText
        sansCDSLabel['text'] = "Nombre de NC sans CDS : " + str(parser.nc_sans_cds)


        tmp = parser.nc_treat
        nouveaux, modifies, inchanges =  parser.treat_next_organism()

        nouveauxGlobal += nouveaux
        modifiesGlobal += modifies
        inchangesGlobal += inchanges

        progress['value'] += parser.nc_treat - tmp
        pourcent['text'] = str(parser.nc_treat) + "/" + str(parser.nc_to_treat)
        nouveauxLabel['text'] = "Nombre de nouveaux NC : " + str(parser.nc_nouveaux)
        modifiesLabel['text'] = "Nombre de NC modifiés : " + str(parser.nc_modifies)
        inchangesLabel['text'] = "Nombre de NC non modifiés : " + str(parser.nc_inchanges)
        supprimesLabel['text'] = supprText
        sansCDSLabel['text'] = "Nombre de NC sans CDS : " + str(parser.nc_sans_cds)

        tv.tag_configure('nouveau', background='green', foreground="white")
        tv.tag_configure('modif',   background='yellow', foreground="black")
        update_arbo()
        window.update_idletasks()


def ParseData():
    print("Téléchargements des fichiers\n")

    majFilesToParse(1)
    majFilesToParse(2)
    majFilesToParse(3)
    majFilesToParse(4)

    print("------------------------\n")

    s = Style()
    s.theme_use('clam')
    s.configure("green.Horizontal.TProgressbar", foreground='green', background='green')

    for e in c:
        if not isinstance(e, int):
            fileToParse.append(e)

    global parser
    parser = Parser(fileToParse, checkSupprime.get())
    
    global t1
    t1 = thread_with_trace(target=parsing,args=())
    # t1 = thread_with_trace(target=parsing,args=(fileToParse,))
    t1.start()

    print("Le parsing commence")
    print("------------------------")


def ReprendreParsing():
    if not parser.hasStarted:
        print("Le parsing n'avait pas encore commencé")
        print("------------------------")
    else:
        global t1
        t1 = thread_with_trace(target=parsing,args=())
        # t1 = thread_with_trace(target=parsing,args=(fileToParse,))
        t1.start()
        print("Le parsing reprend")
        print("------------------------")




def StopParsing():
    # global stop_thread
    # stop_thread = True
    global t1
    t1.kill()
    t1.join()
    print('On stoppe le parsing')
    stop_button["state"] = 'disabled'
    parsing_button['state'] = 'normal'
    reprendre_button['state'] = 'normal'



def majFilesToParse(bouton):


    if not os.path.exists('Datamaj'):
        os.makedirs('Datamaj')

    ftp_server = FTP('ftp.ncbi.nlm.nih.gov')
    ftp_server.connect()
    ftp_server.login()
 

    ftp_server.cwd('genomes/GENOME_REPORTS/')


    if (bouton == 1):
        if (checkEuk.get() == 1):
            c[0] = "eukaryotes"
            try:
                with open("Datamaj/eukaryotes.txt", "rb") as f:
                    print("deja telechargé") 
            except:
                ftp_server.retrbinary('RETR eukaryotes.txt' ,open('Datamaj/eukaryotes.txt',"wb").write)
        else:
            c[0] = 0
        return
    elif (bouton == 2):
        if (checkPlasmid.get() == 1):
            c[1] = "plasmids"
            try:
                with open("Datamaj/plasmids.txt", "rb") as f:
                    print("deja telechargé") 
            except:
                ftp_server.retrbinary('RETR plasmids.txt' ,open('Datamaj/plasmids.txt',"wb").write)
        else:
            c[1] = 0
        return
    elif (bouton == 3):
        if (checkProk.get() == 1):
            c[2] = "prokaryotes"
            try:
                with open("Datamaj/prokaryotes.txt", "rb") as f:
                    print("deja telechargé") 
            except:
                ftp_server.retrbinary('RETR prokaryotes.txt' ,open('Datamaj/prokaryotes.txt',"wb").write)
        else:
            c[2] = 0
        return
    elif (bouton == 4):
        if (checkVirus.get() == 1):
            c[3] = "viruses"
            try:
                with open("Datamaj/viruses.txt", "rb") as f:
                    print("deja telechargé") 
            except:
                ftp_server.retrbinary('RETR viruses.txt' ,open('Datamaj/viruses.txt',"wb").write)
        else:
            c[3] = 0
        return



def OnDoubleClick(event):
    
    item = tv.identify("item", event.x, event.y)
    name = tv.item(item)["text"]
    # child_id = tv.get_children()
    # tv.focus(child_id)

    # item_iid = tv.selection()
    # parent_iid = tv.parent(item_iid)
    # node = tv.item(parent_iid)['text']
    # print ("you clicked on", name)
    mypath=os.path.abspath(name)
        
    namefile, extension = os.path.splitext(name)
    # directory = os.path.abspath(name)
    # print(namefile)
    # print(extension)
    if(extension == '.txt'):
        for elem in liste:
            if(name in elem):
                savechemin = elem
        # print(savechemin)
        # print("oui")
        MsgBox = tk.messagebox.askquestion  ('Afficher','Souhaitez-vous afficher un aperçu du fichier?',icon = 'question')
        if(MsgBox=='yes'):
            # print(directory)
            # print('il a dit oui')
            configfile.delete("1.0","end")
            with open(savechemin, 'r') as f:
                 configfile.insert(INSERT, f.read())
                 configfile.bind("<Key>", lambda e: "break")
                 f.close()




# ----------------------------------------------------      MAIN       ------------------------------------------------------------------------------------- #

if __name__ == "__main__":

    window = tk.Tk()
    window.title('BioInfo')
    window.geometry('1200x700')

    nouveaux = []
    modifies = []
    inchanges = []

    nouveauxGlobal = []
    modifiesGlobal = []
    inchangesGlobal = []

    # ----------------------------------------------------       AFFICHAGE DE L'ARBORESCENCE        ------------------------------------------------------------------------------------- #

    m1 = PanedWindow(window)
    m1.pack(fill=BOTH, expand=1)


    frame_arbo = ttk.Frame(m1, width=100, height=300, relief=SUNKEN)
    frame_arbo.pack()

    liste = []

    tv = ttk.Treeview(frame_arbo, show='tree')
    ybar = tk.Scrollbar(frame_arbo, orient=tk.VERTICAL, command=tv.yview)
    tv.configure(yscroll=ybar.set)
    createData()
    directory = 'Data'
    tv.heading('#0', text='Dir：'+directory, anchor='w')
    mypath = os.path.abspath(directory)
    chunks = mypath.split('Data')
    new = "Data/" + chunks[1]
    node = tv.insert('', 'end', text=new, open=True)
    traverse_dir(node, mypath)
    ybar.pack(side=tk.RIGHT, fill=tk.Y)
    tv.pack(fill=BOTH, expand=True)
    frame_arbo.pack(side='left')


    m1.add(frame_arbo)


    m2 = ttk.PanedWindow(m1, orient=VERTICAL)
    m1.add(m2)
    fram2 = ttk.Frame(m2, width=800, height=800, relief=SUNKEN)
    fram2.pack()
    checkEuk = tk.IntVar()
    checkPlasmid = tk.IntVar()
    checkProk = tk.IntVar()
    checkVirus = tk.IntVar()
    checkSupprime = tk.IntVar()

    cEuk = tk.Checkbutton(fram2, text='Eukaryotes', variable=checkEuk)
    cEuk.pack(anchor="w", side="top")


    cPlasmid = tk.Checkbutton(fram2, text='Plasmids', variable=checkPlasmid)
    cPlasmid.pack(anchor="w", side="top")


    cProk = tk.Checkbutton(fram2, text='Prokaryotes', variable=checkProk)
    cProk.pack(anchor="w", side="top")


    cVirus = tk.Checkbutton(fram2, text='Viruses', variable=checkVirus)
    cVirus.pack(anchor="w", side="top")


    cSupprime = tk.Checkbutton(
        fram2, text='Suppression des NC n\'ayant plus de CDS', variable=checkSupprime)
    cSupprime.pack(anchor="w", side="top")


    m2.add(fram2)

    # --------------------------------------------------------------      AFFICHAGE DE TEXTE         --------------------------------------------------------------------- #


    fram3 = ttk.Frame(m2, width=400,  height=400, relief=SUNKEN)
    fram3.pack()
    configfile = Text(fram3, wrap=WORD, width=45, height=20)
    # configfile.configure(state='disabled')
    configfile.pack(fill=BOTH, expand=True)

    m2.add(fram3)

    c = [0, 0, 0, 0]
    fileToParse = []

    stop_thread = False
    t1 = None

    parser = Parser([])


    # --------------------------------------------------------------     FONCTIONS         --------------------------------------------------------------------- #


    p1 = Process(target=parsing, args=())


    nameOrgaLabel = tk.Label(fram2)
    nameOrgaLabel.pack()

    parsing_button = tk.Button(
        fram2, text="Lancer parsing", command=ParseData,  bg='white', fg='black')
    parsing_button.pack(padx=30, pady=30)

    progress = tk.ttk.Progressbar(fram2, style='green.Horizontal.TProgressbar',
                                orient='horizontal', length=500, mode='determinate')
    progress.pack(padx=40, pady=20)

    pourcent = tk.Label(fram2)
    pourcent.pack()

    nouveauxLabel = tk.Label(fram2)
    nouveauxLabel.pack()

    modifiesLabel = tk.Label(fram2)
    modifiesLabel.pack()

    inchangesLabel = tk.Label(fram2)
    inchangesLabel.pack()

    supprimesLabel = tk.Label(fram2)
    supprimesLabel.pack()

    sansCDSLabel = tk.Label(fram2)
    sansCDSLabel.pack()


    nameOrgaLabel['text'] = "En attente du lancement du parsing\n\n"
    pourcent['text'] = str(parser.nc_treat) + "/" + str(parser.nc_to_treat)
    nouveauxLabel['text'] = "Nombre de nouveaux NC : " + str(parser.nc_nouveaux)
    modifiesLabel['text'] = "Nombre de NC modifiés : " + str(parser.nc_modifies)
    inchangesLabel['text'] = "Nombre de NC non modifiés : " + \
        str(parser.nc_inchanges)
    supprimesLabel['text'] = "Nombre de NC deja parsés n'ayant plus de CDS : " + \
        str(parser.nc_supprimes)
    sansCDSLabel['text'] = "Nombre de NC sans CDS : " + str(parser.nc_sans_cds)

    stop_button = tk.Button(fram2, text="Arreter parsing",
                            command=StopParsing, bg='white', fg='black', state='disabled')
    stop_button.pack(padx=30, pady=10)

    reprendre_button = tk.Button(fram2, text="Reprendre parsing",
                                command=ReprendreParsing, bg='white', fg='black', state='disabled')
    reprendre_button.pack(padx=30, pady=5)


    # --------------------------------------------------------------    TRAITEMENT ET  AFFICHAGE DE L'ARBORESCENCE        --------------------------------------------------------------------- #

    savechemin = ''


    tv.bind('<Double-1>', OnDoubleClick)


    print("Lancement de l'interface")
    print("------------------------")
    window.mainloop()
