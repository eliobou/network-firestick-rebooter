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
- Raspberry Pi autorisé pour le débogage ADB
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

### 2. Première mise en route — générer et persister la clé ADB

La clé ADB doit être persistée sur le Pi pour survivre aux rebuilds Docker. Sans ça, chaque rebuild génère une nouvelle clé et le Firestick redemande une autorisation.

```bash
# Lancer le conteneur une première fois pour générer la clé
docker run -d --name firestick-reboot --network host firestick-reboot

# Déclencher une requête pour forcer la génération de la clé ADB
curl http://localhost:8765/reboot

# Copier la clé depuis le conteneur vers le Pi
docker exec firestick-reboot cat /root/.android/adbkey > /home/pi/adbkey
docker exec firestick-reboot cat /root/.android/adbkey.pub > /home/pi/adbkey.pub

# Supprimer le conteneur temporaire
docker rm -f firestick-reboot
```

### 3. Autoriser le Raspberry Pi sur le Firestick

```bash
# Se connecter au Firestick (accepter la popup sur le Firestick en cochant "Toujours autoriser")
docker run --rm --network host \
  -v /home/pi/adbkey:/root/.android/adbkey \
  -v /home/pi/adbkey.pub:/root/.android/adbkey.pub \
  firestick-reboot adb connect 192.168.1.99:5555
```

### 4. Lancement définitif du conteneur

```bash
docker run -d \
  --name firestick-reboot \
  --restart always \
  --network host \
  -v /home/pi/adbkey:/root/.android/adbkey \
  -v /home/pi/adbkey.pub:/root/.android/adbkey.pub \
  firestick-reboot
```

Les volumes `-v` permettent au conteneur d'utiliser toujours la même clé ADB, même après un rebuild. Le Firestick ne redemandera plus d'autorisation.

### 5. Vérifier que le daemon Docker démarre au boot

L'option `--restart always` assure le redémarrage automatique du conteneur après un reboot du Raspberry Pi, à condition que le daemon Docker soit activé au démarrage.

```bash
sudo systemctl is-enabled docker
# Si "disabled" :
sudo systemctl enable docker
```

## API

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/reboot` | Déclenche le reboot du Firestick |

**Exemple :**
```bash
curl http://192.168.1.23:8765/reboot
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
4. Méthode : **GET**
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

# Rebuild après modification de app.py (les clés ADB sont préservées via les volumes)
docker build -t firestick-reboot . && docker rm -f firestick-reboot && docker run -d \
  --name firestick-reboot \
  --restart always \
  --network host \
  -v /home/pi/adbkey:/root/.android/adbkey \
  -v /home/pi/adbkey.pub:/root/.android/adbkey.pub \
  firestick-reboot

# Tester l'API depuis le Pi
curl http://localhost:8765/reboot

# Tester ADB manuellement depuis le conteneur
docker exec firestick-reboot adb -s 192.168.1.99:5555 connect 192.168.1.99:5555
docker exec firestick-reboot adb -s 192.168.1.99:5555 shell echo "connexion ok"
```

## Configuration

Les variables à modifier dans `app.py` si besoin :

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `FIRESTICK_IP` | `192.168.1.99` | IP du Firestick |
| `FIRESTICK_PORT` | `5555` | Port ADB |
| `port` | `8765` | Port d'écoute du serveur Flask |