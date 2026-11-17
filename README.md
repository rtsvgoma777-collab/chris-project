# Site RTSV — Radio Télé Source de Vie Goma (97.5 FM)

## Lancer
    pip install -r requirements.txt
    python app.py        # http://localhost:5000
(En production Windows : `pip install waitress` puis `waitress-serve --port=5000 app:app`.)

## Brancher le direct (RadioBoss / MyRadio / autre)
1. Le logiciel d'automation envoie l'audio vers un serveur de streaming (Icecast ou Shoutcast).
   RadioBoss : Options > Streaming/Broadcasting (encodeur MP3 vers Icecast).
2. Dans `app.py` (ou variables d'environnement), mettez l'adresse du flux dans `STREAM_URL`.
3. Titre en cours :
   - RadioBoss : activez l'API (Options > API), puis réglez RADIOBOSS_API et RADIOBOSS_PASS.
   - Icecast : NOWPLAYING_MODE=icecast et ICECAST_STATUS.
4. Si le site est en HTTPS, le flux doit l'être aussi (sinon le navigateur le bloque).

Les messages du formulaire arrivent dans `messages.jsonl`.
Modifiez STATION et PROGRAMMES dans `app.py` pour vos vraies informations.
