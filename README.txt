Nous avons créé 3 executables de notre programme sous 3 OS differents (MacOS, Linux, Windows).
Pour lancer un executable il suffit de faire : "./ex_mac", "./ex_linux" ou "./ex_windows". 
Attention il est possible que l'executable n'ait pas les droits de s'executer sur votre machine. 
Pour résoudre ce problème : chmod 777 <ex_name>
Si jamais vous avez des problèmes à lancer les executables à la fin du rapport nous citons les modules necessaires et les étapes pour lancer directement le code python.


Les fichiers "eukaryotes.txt", "plasmids.txt", "prokaryotes.txt" et "viruses.txt" se trouvent en local.
Ces fichiers contiennent le nom, le groupes et le sous groupe d'un organisme. 
Ainsi que le(s) nom(s) de leurs NC si l'organisme en possède.


Dans l'arborescence :
    - Les nouveaux fichiers NC sont affichés sur fond vert.
    - Les fichiers NC modifiés sont affichés sur fond jaune.
    - Les fichiers NC non modifiés sont affichés sur fond blanc.
Comme l'arborescence se recharge après chaque traitement d'un organisme nous conseillons de mettre en pause le parsing si vous voulez explorer l'arborescence.
Vous pouvez bien sur reprendre le cours du parsing plus tard.


Utilisation de l'interface :
    - Cocher les familles (eukaryotes, prokaryotes, plasmids et viruses) que vous voulez parser.
        si plusieurs ont été cochés alors leur execution se fera à la suite.

    - Cocher "Suppression des NC n'ayant plus de CDS" si vous voulez supprimer les NC deja telechargés qui à l'heure actuelle n'ont plus de CDS.
    
    - Lancer le parsing

    Vous pouvez naviguer dans l'arborescence durant son execution.
    En double cliquant sur un fichier NC de l'arborescence son contenu est affiché dans l'interface.

    Une barre de chargement indique le nombre de NC qu'il reste à traiter.

    Lors du déroulement du parsing on affiche :
        - l'organisme en cours de traitement
        - le nombre de nouveaux NC trouvés
        - le nombre de NC déjà presents qui ont été modifiés 
        - le nombre de NC déjà presents qui n'ont pas été modifiés 
        - le nombre de NC déjà presents qui n'ont plus de CDS dans la mise a jour (supprimé ou non selon votre choix)
        - le nombre de NC sans CDS
    
    - On peut arreter le parsing.
    - Si on arrête le parsing, et qu'on le reprend en ayant coché d'autres options, les autres options ne seront pas prises en compte, le logiciel continuera à parser pour celui qu'on avait choisi à la base.
    - Si on souhaite parser avec des nouvelles options, il faut fermer le logiciel, et le relancer puis cocher les nouvelles options qu'on souhaite.
    - Le reprendre.
    - Le logiciel crée un dossier contenant un fichier, à partir du moment où celui-ci contient des CDS. Par exemple, si on parse 10 fichiers et qu'aucun ne contient des CDS, on aura
        pas de dossier crée. Un dossier sera crée quand le logiciel trouve des CDS.
    
    - Quitter en fermant la fenetre.


Nous utilisons des threads pour pouvoir utiliser l'interface durant le parsing.


Tout les fichiers/dossiers extraits de GenBank se trouvent dans le dossier "Data".
Le dossier "ExempleData" est un exemple de ce que le programme crée.
Au cas où vous n'arriverez pas à lancer le programme nous mettons à disposition des captures d'écran de notre interface.


Si vous voulez executer les fichiers python il vous faut :
    - Une version python3 ou plus
    - Les modules :
        - tkinter : pip install tkinter
        - Biopython : pip install biopython
        - multiprocessing : pip install multiprocessing
        - threading : pip install threading
        - parsing : pip install parsing
    
    - Lancer la commande : python3 ex.py
