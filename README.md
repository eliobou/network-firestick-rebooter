# firestick-reboot

Petit serveur HTTP Flask qui permet de rebooter un Amazon Firestick via ADB, déclenché depuis un raccourci iOS.

## Architecture

```
iPhone (Raccourcis iOS)
    └── VPN
        └── Raspberry Pi :8765
            └── Flask API
                └── ADB → Firestick 192.168.1.99:5555
```

## Prérequis

- Raspberry Pi avec Docker installé
- ADB activé sur le Firestick (`Paramètres > Options développeur > Débogage ADB`)
- **Raspberry Pi autorisé poour debugage ADB**
- VPN configuré pour accéder au réseau local depuis l'iPhone

## Fichiers

```
firestick-reboot/
├── app.py
├── requirements.txt
└── Dockerfile
```

## Déploiement

### 1. Build de l'image Docker

```bash
cd /home/pi/firestick-reboot
docker build -t firestick-reboot .
```

### 2. Lancement du conteneur

```bash
docker run -d \
  --name firestick-reboot \
  --restart always \
  --network host \
  firestick-reboot
```

L'option `--restart always` assure le redémarrage automatique du conteneur après un reboot du Raspberry Pi (à condition que le daemon Docker soit activé au démarrage).

### 3. Vérifier que le daemon Docker démarre au boot

```bash
sudo systemctl is-enabled docker
# Si "disabled" :
sudo systemctl enable docker
```

## API

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/reboot` | Déclenche le reboot du Firestick |

**Exemple :**
```bash
curl -X POST http://192.168.1.23:8765/reboot
```

**Réponse succès (200) :**
```json
{ "success": true, "message": "Reboot triggered successfully" }
```

**Réponse erreur (500) :**
```json
{ "success": false, "message": "<détail de l'erreur>" }
```

## Raccourci iOS

Dans l'app **Raccourcis** sur iPhone :

1. Créer un nouveau raccourci
2. Ajouter l'action **"Obtenir le contenu d'une URL"**
3. URL : `http://192.168.1.23:8765/reboot`
4. Méthode : **POST**
5. (Optionnel) Ajouter une action **"Afficher le résultat"** pour voir la réponse

> Le VPN doit être actif sur l'iPhone pour joindre l'IP locale du Raspberry Pi.

## Commandes utiles

```bash
# Voir les logs en temps réel
docker logs -f firestick-reboot

# Statut du conteneur
docker ps

# Redémarrer le conteneur (ex: après modif de app.py)
docker restart firestick-reboot

# Rebuild après modification de app.py
docker build -t firestick-reboot . && docker rm -f firestick-reboot && docker run -d \
  --name firestick-reboot \
  --restart always \
  --network host \
  firestick-reboot

docker rm -f firestick-reboot

# Tester l'API depuis le Pi
curl -X POST http://localhost:8765/reboot

# Tester ADB manuellement
adb connect 192.168.1.99:5555
adb shell setprop sys.powerctl reboot
adb disconnect
```

## Configuration

Les variables à modifier dans `app.py` si besoin :

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `FIRESTICK_IP` | `192.168.1.99` | IP du Firestick |
| `FIRESTICK_PORT` | `5555` | Port ADB |
| `port` | `8765` | Port d'écoute du serveur Flask |