# coding: utf-8

from time import time

from .block import Block
from .._global import OptionalModule

try:
  import tkinter as tk
except (ModuleNotFoundError, ImportError):
  tk = OptionalModule("tkinter")


class GUI(Block):
  """This block allows the user to send a signal upon clicking on a button in
  a graphical user interface.

  It sends an integer value, that starts from `0` and is incremented every time
  the user clicks on the button.
  """

  def __init__(self,
               send_0: bool = False,
               label: str = 'step',
               time_label: str = 't(s)',
               freq: float = 50,
               spam: bool = False,) -> None:
    """Sets the args and initializes the parent class."""

    Block.__init__(self)
    self.freq = freq
    self.spam = spam
    self.labels = [time_label, label]

    self._send_0 = send_0

  def prepare(self) -> None:
    """Creates the graphical interface and sets its layout and callbacks."""

    self._root = tk.Tk()
    self._root.title("GUI block")
    self._root.resizable(False, False)

    self._step = tk.IntVar()
    self._step.trace_add('write', self._update_text)
    self._text = tk.StringVar(value=f'step: {self._step.get()}')

    self._label = tk.Label(self._root, textvariable=self._text)
    self._label.pack(padx=7, pady=7)

    self._button = tk.Button(self._root,
                             text='Next step',
                             command=self._next_step)
    self._button.pack(padx=25, pady=7)

    self._root.update()

  def begin(self) -> None:
    """Sends the value of the first step (`0`) if required."""

    if self._send_0:
      self.send([time() - self.t0, self._step.get()])

  def loop(self) -> None:
    """Updates the interface, and sends the current step value if spam is
    :obj:`True`. """

    try:
      self._root.update()
    except tk.TclError:
      return

    if self.spam:
      self.send([time() - self.t0, self._step.get()])

  def finish(self) -> None:
    """Closes the interface window."""

    try:
      self._root.destroy()
    except tk.TclError:
      pass

  def _update_text(self, _, __, ___) -> None:
    """Simply updates the displayed text."""

    self._text.set(f'step: {self._step.get()}')

  def _next_step(self) -> None:
    """Increments the step counter and sends the corresponding signal."""

    self._step.set(self._step.get() + 1)
    self.send([time() - self.t0, self._step.get()])
