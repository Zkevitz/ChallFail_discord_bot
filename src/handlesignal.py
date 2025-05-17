import signal
import sys

def signal_handler(sig, frame) -> None:
    print('Arrêt du bot...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)