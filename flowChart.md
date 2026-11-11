```mermaid
graph TD
    %% 1. INTRO & AUTH
    Start([Lancement de l'App]) --> Intro[explication du contexte du jeu]
    Intro --> Auth{Authentification}
    Auth -->|Nouveau joueur| Register(Créer un compte email/mdp)
    Auth -->|Joueur existant| Login(Se connecter)
    
    %% 2. DASHBOARD
    Register --> Dash{Tableau de Bord / Profil <br/>  <br/> UI : Niveau, Solde Dabloons}
    Login --> Dash
    
    %% 3. BRANCHES DU DASHBOARD
    Dash -->|Bouton| Jouer[Star(t) creating <br/> 20 Niveaux / 6 sessions par niveau]
    Dash -->|Bouton| Quiz[Quizz <br/> 5 questions]
    Dash -->|Bouton| Diary[Star Diary <br/> Historique des étoiles]
    Dash -->|Bouton| Trophy[Trophées]

    %% 4. GAMEPLAY LOOP
    Jouer --> Sim[Console de Simulation <br/> Jauges interactives + Étoile 3D en direct]
    Sim -.->|Achat| Indice(Utiliser un Indice <br/> Max 3 par session)
    Sim --> Valider{Validation des paramètres}
    
    Valider -->|3 erreurs ou plus| Fail[ÉCHEC]
    Fail --> Dash
    
    Valider -->|Moins de 3 erreurs| Win[SUCCÈS : Étoile forgée]
    Win --> UpdateD[Gains : +100 Dabloons]
    UpdateD --> AddDiary[Ajout au Star Diary avec détails]
    AddDiary --> Jouer

    %% 5. QUIZ LOOP
    Quiz --> QLoop[Série de 5 questions]
    QLoop --> Score{Calcul du score}
    Score -->|+10 par bonne réponse <br/> -10 par mauvaise| GainQ[Mise à jour des Dabloons]
    GainQ --> Dash
```
