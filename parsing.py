# Format requetes API E-utilities pour recuperer fichiers NC_
# https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_014138.1&rettype=fasta


   
import re
import os
import requests
from Bio import SeqIO
from Bio import Entrez
import shutil
import filecmp


url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
req_obj = {'db': 'nuccore', 'id': None, 'rettype': 'gb'}


class Organisme:
    def __init__(self, nom, groupe, sous_groupe, nc_names, family):
        self.nom = nom
        self.groupe = groupe
        self.sous_groupe = sous_groupe
        self.nc_names = nc_names
        self.family = family

        self.prefix = family + "/" + groupe + "/" + sous_groupe + "/" + nom


class Parser:
    def __init__(self, filesToParse, suppr=0):
        if not os.path.isdir('./Data'):
            os.makedirs('./Data')

        self.nc_to_treat = 0
        self.nc_treat = 0
        self.nc_nouveaux = 0
        self.nc_modifies = 0
        self.nc_inchanges = 0
        self.nc_sans_cds = 0
        self.nc_supprimes = 0

        self.suppr = suppr

        self.hasStarted = False

        self.organisms = []
        self.nb_files = len(filesToParse)

        self.familles = {}

        if (len(filesToParse) > 0):
            self.cur_family = filesToParse[0]

        for f in filesToParse:
            self.get_nc_by_organism(f)
        
        if (len(filesToParse) > 0):
            organisms_of_cur_family = self.familles[self.cur_family]
            self.next_orga_to_treat = organisms_of_cur_family.pop(0)
      

    def clean_data(self) :
        for e in os.listdir("./Data") :
            shutil.rmtree("./Data/" + e)


    def get_nc_by_organism(self, famille) :
        nc_pattern = 'NC_[0-9]*\.1'
        prefix = "./Data/" + famille

        f = open("./Datamaj/" + famille + ".txt")

        if not os.path.isdir(prefix):
            os.mkdir(prefix)

        organisms = []

        for line in f :
            if line.startswith("#"): # si c'est la premiere ligne
                continue

            # noms des fichiers NC_ present sur la ligne
            nc_files_names = re.findall(nc_pattern, line)

            # aucun NC dans la ligne
            if len(nc_files_names) != 0:
                lline = line.split("\t")
                organism_name = lline[0] # nom
                organism_group = lline[4] # groupe
                organism_ss_group = lline[5] # sous-groupe

                new_orga = Organisme(organism_name, organism_group, organism_ss_group, nc_files_names, famille)

                organisms.append(new_orga)

                self.nc_to_treat += len(nc_files_names)

        self.familles[famille] = organisms
            
        f.close()

    
    def treat_next_organism(self) :
        nouveaux = []
        modifies = []
        inchanges = []

        self.hasStarted = True

        organisms_of_cur_family = self.familles[self.cur_family]

        if (len(organisms_of_cur_family) > 0):
            prefix = "./Data/" + self.cur_family
            organism = organisms_of_cur_family.pop(0)
            prefix = prefix + "/" + organism.groupe + "/" + organism.sous_groupe + "/" + organism.nom
            
            # pour chaque fichiers NC_ 
            for nc_name in organism.nc_names :
                # handle = Entrez.efetch(db="nuccore", id=nc_name, rettype="gb", retmode="text")  
                # gb_record = SeqIO.read(handle, "genbank")

                # on envoie une requete avec l'api E-utilities 
                req_obj["id"] = nc_name
                contenu = requests.post(url, req_obj)

                # on ecrit le contenu dans un fichier temporaire .gbk
                file_name = nc_name + ".gbk"
                new_file = open(file_name, "w+")
                new_file.write(contenu.text)
                new_file.close()

                # on creer un fichier SeqIO
                gb_record = SeqIO.read(open(file_name,"r"), "genbank")

                os.remove(file_name)

                CDS_present_on_this_nc = False

                nc_filename = prefix + "/" + nc_name + ".txt"
                nc_filename_double = prefix + "/" + nc_name + "DOUBLE.txt"
                cur_filename = nc_filename
                already_exist = False

                if not os.path.isdir(prefix):
                    os.makedirs(prefix)

                if os.path.exists(nc_filename):
                    cur_filename = nc_filename_double
                    already_exist = True

                # fichier dans lequel on va ecrire les CDS
                # output_file = open(cur_filename, "w+")

                cpt=0
                # on extrait les CDS des features
                for gb_feature in gb_record.features:
                    if (gb_feature.type == "CDS"):
                        cpt += 1

                        if (cpt == 1):
                            output_file = open(cur_filename, "w+")
                        
                        CDS_present_on_this_nc = True

                        output_file.write("CDS " + str(gb_feature.location) + "\n")
                        extract = gb_feature.extract(gb_record.seq)
                        output_file.write(str(extract) + "\n")

                if cpt > 0:
                    output_file.close()
                    cpt=0

                # si on a recopié un fichier
                if already_exist:
                    # les nc ayant des cds avant n'en ont plus
                    if not CDS_present_on_this_nc:
                        if self.suppr == 1:
                            os.remove(nc_filename)

                        self.nc_supprimes += 1
                    # qu'on avait deja
                    elif filecmp.cmp(nc_filename, nc_filename_double, shallow=False):
                        os.remove(nc_filename_double)
                        inchanges.append(nc_filename)
        
                        self.nc_inchanges += 1
                    # differement
                    else:
                        os.remove(nc_filename)
                        os.rename(nc_filename_double, nc_filename)
                        modifies.append(nc_filename)

                        self.nc_modifies += 1
                else:
                    if CDS_present_on_this_nc:
                        nouveaux.append(nc_filename)

                        self.nc_nouveaux += 1
                    else:
                        self.nc_sans_cds += 1
                    
                self.nc_treat += 1

            self.familles[self.cur_family] = organisms_of_cur_family
            tmp = self.familles[self.cur_family]
            self.next_orga_to_treat = tmp.pop(0)

            if self.suppr == 1:
                self.delete_empty_dir('./DATA')
        
        else:
            self.cur_family += 1
            if (self.cur_family == self.nb_files):
                return 1
            self.treat_next_organism()

        return nouveaux, modifies, inchanges


    def delete_empty_dir(self, dir):
        for root, dirs, files in os.walk(dir, topdown=False):
            nroot = "./" + root
            # nroot = root.replace(" ", "\")
            
            if len(os.listdir(nroot) ) == 0:
                os.rmdir(nroot)


