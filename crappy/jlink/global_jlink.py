



import pylink


class Global_JLINK():

    def __init__(self):
        self.jlink = pylink.JLink()

    def connect(self):
        # Établir la connexion avec le J-Link
        self.jlink.open()

        # Initialiser la cible (à adapter en fonction de votre configuration)
        self.jlink.connect("Cortex-M4")

        # Configurer le mode de transfert en temps réel (RTT)
        self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)

        # Ouvrir le canal RTT
        self.jlink.rtt_start()

    def rtt_write(self, channel, data):
        # Écrire des données RTT dans le canal spécifié
        self.jlink.rtt_write(channel, data)

    def rtt_read(self, channel, size):
        # Lire des données RTT à partir du canal spécifié
        return self.jlink.rtt_read(channel, size)

    def disconnect(self):
        # Arrêter le canal RTT
        self.jlink.rtt_stop()

        # Fermer la connexion avec le J-Link
        self.jlink.close()