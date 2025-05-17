# ChallFail_discord_bot
This Python script is a Discord bot designed to keep track of the challenge scores for you and your friends during your Dofus adventures. The bot allows players to compete in a friendly challenge


Documentation : 

## Installation 
    je dois encore l'ecrire 


## commande prefix : '!' 
        !setmessage --> Redefinis le message statique qui accueillera le ladderr 
        
        !clearLadder --> supprime l'ensemble des données du ladder (vide la base de données et les variables du bot)

        !clearchannel --> principalement utilitaire supprime l'ensemble des messages du channel dans le quels vous etes ATTENTION : discord limite le nombre de message supprimer a 100 par appel

        !sync [guilds] [spec] --> synchronise les commandes slash avec Discord
            [guilds] --> (optionnel) IDs des serveurs à synchroniser
            [spec] --> (optionnel) modificateur de synchronisation:
                - sans modificateur: synchronise globalement
                - "~": synchronise avec le serveur actuel uniquement
                - "*": copie les commandes globales vers le serveur actuel
                - "^": supprime toutes les commandes du serveur actuel

## commande slash 

        *argument optionnel 

        /addscore [event] [victory] [nb_of_opponent] [image] [image2] [joueur1] [joueur2*] [joueur3*] [joueur4*] [joueur5*] :

            [event] --> rendre les evenements configurable
            [victory : boolean] --> True or False (victoire ou defaite)
            [nb_of_opponent] --> 0, 1, 2, 3, 4, 5 (nombre d'adversaire)
            [image] --> image de l'attaque/defense
            [image2] --> image de l'attaque/defense
            [joueur1->5] --> pseudo discord des joueurs participants

        /adminpoint [action] [target] [nb_de_points] :
            [action] --> Ajouter des points a un joueur ou Retirer des points a un joueur
            [target] --> pseudo discord des joueurs participants
            [nb_de_points] --> nombre de points a ajouter ou retirer

        /showscore : Affiche le tableau des scores des joueurs
        /exoscore : Affiche le tableau des scores des joueurs en forgemagie
        /tryexo : Permet de lancer une petite simulation de tentative de exo   avec une proba a 1%
        

        
            
![alt text](Untitled__11_-1.png)