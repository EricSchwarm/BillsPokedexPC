"""Entry point: wires the DB, e-ink display, and buttons into the Pokedex app."""

import signal

from config import DB_PATH
from pokedex import db
from pokedex.app import PokedexApp
from pokedex.display.waveshare_driver import WaveshareDriver
from pokedex.input.gpio_input import GpioButtonInput


def _raise_system_exit(signum, frame) -> None:
    raise SystemExit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, _raise_system_exit)

    conn = db.connect(DB_PATH)
    display = WaveshareDriver()
    button_input = GpioButtonInput()
    app = PokedexApp(conn, display, button_input)
    app.start()

    try:
        signal.pause()
    finally:
        button_input.close()
        display.sleep()
        conn.close()


if __name__ == "__main__":
    main()
