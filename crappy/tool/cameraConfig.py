# coding: utf-8

import tkinter as tk
from platform import system
import numpy as np
from time import time, sleep
from typing import Optional, Tuple
from functools import partial

from .._global import OptionalModule
from .cameraConfigTools import Zoom

try:
  from PIL import ImageTk, Image
except (ModuleNotFoundError, ImportError):
  ImageTk = OptionalModule("pillow")
  Image = OptionalModule("pillow")


class Camera_config(tk.Tk):
  """This class is a GUI allowing the user to visualize the images from a
  camera before a Crappy test starts, and to tune the settings of the camera.

  It is meant to be user-friendly and interactive. It is possible to zoom on
  the image using the mousewheel, and to move on the zoomed image by
  left-clicking and dragging.

  In addition to the image, the interface also displays a histogram of the
  pixel values, an FPS counter, a detected bits counter, the minimum and
  maximum pixel values and the value and position of the pixel currently under
  the mouse. A checkbox allows auto-adjusting the pixel range to get a better
  contrast.
  """

  def __init__(self, camera) -> None:
    """Initializes the interface and starts displaying the first image.

    Args:
      camera: The camera object in charge of acquiring the images.
    """

    super().__init__()
    self._camera = camera

    # Attributes containing the several images and histograms
    self._img = None
    self._pil_img = None
    self._original_img = None
    self._hist = None
    self._pil_hist = None

    # Other attributes used in this class
    self._low_thresh = None
    self._high_thresh = None
    self._move_x = None
    self._move_y = None
    self._run = True

    # Settings for adjusting the behavior of the zoom
    self._zoom_ratio = 0.9
    self._zoom_step = 0
    self._max_zoom_step = 15

    # Settings of the root window
    self.title(f'Configuration window for the camera: {type(camera).__name__}')
    self.protocol("WM_DELETE_WINDOW", self._stop)
    self._zoom_values = Zoom()

    # Initializing the interface
    self._set_variables()
    self._set_traces()
    self._set_layout()
    self._set_bindings()
    self._add_settings()
    self.update()

    # Displaying the first image
    self._update_img()

  def main(self) -> None:
    """Constantly updates the image and the information on the GUI, until asked
    to stop."""

    n_loops = 0
    start_time = time()

    while self._run:
      # Update the image, the histogram and the information
      self._update_img()

      # Update the FPS counter
      n_loops += 1
      if time() - start_time > 0.5:
        self._fps_var.set(n_loops / (time() - start_time))
        n_loops = 0
        start_time = time()

    print("Camera config done !")

  def _set_layout(self) -> None:
    """Creates and places the different elements of the display on the GUI."""

    # The main frame of the window
    self._main_frame = tk.Frame()
    self._main_frame.pack(fill='both', expand=True)

    # The frame containing the image and the histogram
    self._graphical_frame = tk.Frame(self._main_frame)
    self._graphical_frame.pack(expand=True, fill="both", anchor="w",
                               side="left")

    # The image row will expand 4 times as fast as the histogram row
    self._graphical_frame.columnconfigure(0, weight=1)
    self._graphical_frame.rowconfigure(0, weight=1)
    self._graphical_frame.rowconfigure(1, weight=4)

    # Adapting the default dimension of the GUI according to the screen size
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    if screen_width < 1600 or screen_height < 900:
      min_width, min_height = 600, 450
    else:
      min_width, min_height = 800, 600

    # The label containing the histogram
    self._hist_canvas = tk.Canvas(self._graphical_frame, height=80,
                                  width=min_width, highlightbackground='black',
                                  highlightthickness=1)
    self._hist_canvas.grid(row=0, column=0, sticky='nsew')

    # The label containing the image
    self._img_canvas = tk.Canvas(self._graphical_frame, width=min_width,
                                 height=min_height)
    self._img_canvas.grid(row=1, column=0, sticky='nsew')

    # The frame containing the information on the image and the settings
    self._text_frame = tk.Frame(self._main_frame, highlightbackground='black',
                                highlightthickness=1)
    self._text_frame.pack(expand=True, fill='y', anchor='ne')

    # The frame containing the information on the image
    self._info_frame = tk.Frame(self._text_frame, highlightbackground='black',
                                highlightthickness=1)
    self._info_frame.pack(expand=False, fill='both', anchor='n', side='top',
                          ipady=2)

    # The information on the image
    self._fps_label = tk.Label(self._info_frame, textvariable=self._fps_txt)
    self._fps_label.pack(expand=False, fill='none', anchor='n', side='top')

    self._auto_range_button = tk.Checkbutton(self._info_frame,
                                             text='Auto range',
                                             variable=self._auto_range)
    self._auto_range_button.pack(expand=False, fill='none', anchor='n',
                                 side='top')

    self._min_max_label = tk.Label(self._info_frame,
                                   textvariable=self._min_max_pix_txt)
    self._min_max_label.pack(expand=False, fill='none', anchor='n', side='top')

    self._bits_label = tk.Label(self._info_frame, textvariable=self._bits_txt)
    self._bits_label.pack(expand=False, fill='none', anchor='n', side='top')

    self._zoom_label = tk.Label(self._info_frame, textvariable=self._zoom_txt)
    self._zoom_label.pack(expand=False, fill='none', anchor='n', side='top')

    self._reticle_label = tk.Label(self._info_frame,
                                   textvariable=self._reticle_txt)
    self._reticle_label.pack(expand=False, fill='none', anchor='n', side='top')

    # The frame containing the settings, the message and the update button
    self._sets_frame = tk.Frame(self._text_frame)
    self._sets_frame.pack(expand=True, fill='both', anchor='e', side='top')

    # Tha label warning the user
    self._validate_text = tk.Label(
      self._sets_frame,
      text='To validate the choice of the settings and start the test, simply '
           'close this window.',
      fg='#f00', wraplength=300)
    self._validate_text.pack(expand=False, fill='none', ipadx=5, ipady=5,
                             padx=5, pady=5, anchor='n', side='top')

    # The update button
    self._create_buttons()

    # The frame containing the settings
    self._settings_frame = tk.Frame(self._sets_frame,
                                    highlightbackground='black',
                                    highlightthickness=1)
    self._settings_frame.pack(expand=True, fill='both', anchor='n', side='top')

    # The canvas containing the settings
    self._settings_canvas = tk.Canvas(self._settings_frame)
    self._settings_canvas.pack(expand=True, fill='both', anchor='w',
                               side='left')
    self._canvas_frame = tk.Frame(self._settings_canvas)
    self._id = self._settings_canvas.create_window(
      0, 0, window=self._canvas_frame, anchor='nw',
      width=self._settings_canvas.winfo_reqwidth(), tags='canvas window')

    # Creating the scrollbar
    self._vbar = tk.Scrollbar(self._settings_frame, orient="vertical")
    self._vbar.pack(expand=True, fill='y', side='right')
    self._vbar.config(command=self._custom_yview)

    # Associating the scrollbar with the settings canvas
    self._settings_canvas.config(yscrollcommand=self._vbar.set)

  def _create_buttons(self) -> None:
    """This method is meant to simplify the addition of extra buttons in
    subclasses."""

    self._update_button = tk.Button(self._sets_frame, text="Apply Settings",
                                    command=self._update_settings)
    self._update_button.pack(expand=False, fill='none', ipadx=5, ipady=5,
                             padx=5, pady=5, anchor='n', side='top')

  def _custom_yview(self, *args) -> None:
    """Custom handling of the settings canvas scrollbar, that does nothing
    if the entire canvas is already visible."""

    if self._settings_canvas.yview() == (0., 1.):
      return
    self._settings_canvas.yview(*args)

  def _set_bindings(self) -> None:
    """Sets the bindings for the different events triggered by the user."""

    # Bindings for the settings canvas
    self._settings_canvas.bind("<Configure>", self._configure_canvas)
    self._settings_frame.bind('<Enter>', self._bind_mouse)
    self._settings_frame.bind('<Leave>', self._unbind_mouse)

    # Different mousewheel handling depending on the platform
    if system() == "Linux":
      self._img_canvas.bind('<4>', self._on_wheel_img)
      self._img_canvas.bind('<5>', self._on_wheel_img)
    else:
      self._img_canvas.bind('<MouseWheel>', self._on_wheel_img)

    # Bindings for the image canvas
    self._img_canvas.bind('<Motion>', self._update_coord)
    self._img_canvas.bind('<ButtonPress-3>', self._start_move)
    self._img_canvas.bind('<B3-Motion>', self._move)
    self._bind_canvas_left_click()

    # It's more efficient to bind the resizing to the graphical frame
    self._graphical_frame.bind("<Configure>", self._on_img_resize)
    self._graphical_frame.bind("<Configure>", self._on_hist_resize)

  def _bind_canvas_left_click(self) -> None:
    """This method is meant to simplify the modification of the left button
    behavior in subclasses."""

    pass

  def _bind_mouse(self, _: tk.Event) -> None:
    """Binds the mousewheel to the settings canvas scrollbar when the user
    hovers over the canvas."""

    if system() == "Linux":
      self._settings_frame.bind_all('<4>', self._on_wheel_settings)
      self._settings_frame.bind_all('<5>', self._on_wheel_settings)
    else:
      self._settings_frame.bind_all('<MouseWheel>', self._on_wheel_settings)

  def _unbind_mouse(self, _: tk.Event) -> None:
    """Unbinds the mousewheel to the settings canvas scrollbar when the mouse
    leaves the canvas."""

    self._settings_frame.unbind_all('<4>')
    self._settings_frame.unbind_all('<5>')
    self._settings_frame.unbind_all('<MouseWheel>')

  def _configure_canvas(self, event: tk.Event) -> None:
    """Adjusts the size of the scrollbar according to the size of the settings
    canvas whenever it is being resized."""

    # Adjusting the height of the settings window inside the canvas
    self._settings_canvas.itemconfig(
      self._id, width=event.width,
      height=self._canvas_frame.winfo_reqheight())

    # Setting the scroll region according to the height of the settings window
    self._settings_canvas.configure(
      scrollregion=(0, 0, self._canvas_frame.winfo_reqwidth(),
                    self._canvas_frame.winfo_reqheight()))

  def _on_wheel_settings(self, event: tk.Event) -> None:
    """Scrolls the canvas up or down upon wheel motion."""

    # Do nothing if the entire canvas is already visible
    if self._settings_canvas.yview() == (0., 1.):
      return

    # Different wheel management in Windows and Linux
    if system() == "Linux":
      delta = 1 if event.num == 4 else -1
    else:
      delta = int(event.delta / abs(event.delta))

    self._settings_canvas.yview_scroll(-delta, "units")

  def _on_wheel_img(self, event: tk.Event) -> None:
    """Zooms in or out on the image upon mousewheel motion.

    Handles the specific cases when the mouse is not on the image, or the
    maximum or minimum zoom levels are reached.
    """

    # If the mouse is on the canvas but not on the image, do nothing
    if not self._check_event_pos(event):
      return

    pil_width = self._pil_img.width
    pil_height = self._pil_img.height
    zoom_x_low, zoom_x_high = self._zoom_values.x_low, self._zoom_values.x_high
    zoom_y_low, zoom_y_high = self._zoom_values.y_low, self._zoom_values.y_high

    # Different wheel management in Windows and Linux
    if system() == "Linux":
      delta = 1 if event.num == 4 else -1
    else:
      delta = int(event.delta / abs(event.delta))

    # Handling the cases when the minimum or maximum zoom levels are reached
    self._zoom_step += delta
    if self._zoom_step < 0:
      self._zoom_step = 0
      self._zoom_level.set(100)
      return
    elif self._zoom_step == 0:
      self._zoom_values.reset()
      self._zoom_level.set(100)
      self._on_img_resize()
      return
    elif self._zoom_step > self._max_zoom_step:
      self._zoom_step = self._max_zoom_step
      self._zoom_level.set(100 * (1 / self._zoom_ratio) ** self._max_zoom_step)
      return

    # Correcting the event position to make it relative to the image and not
    # the canvas
    zero_x = (self._img_canvas.winfo_width() - pil_width) / 2
    zero_y = (self._img_canvas.winfo_height() - pil_height) / 2
    corr_x = event.x - zero_x
    corr_y = event.y - zero_y

    # The position of the mouse on the image as a ratio between 0 and 1
    x_ratio = corr_x * (zoom_x_high - zoom_x_low) / pil_width
    y_ratio = corr_y * (zoom_y_high - zoom_y_low) / pil_height

    # Updating the upper and lower limits of the image on the display
    ratio = self._zoom_ratio if delta < 0 else 1 / self._zoom_ratio
    self._zoom_values.update_zoom(x_ratio, y_ratio, ratio)

    # Redrawing the image and updating the information
    self._on_img_resize()
    self._zoom_level.set(100 * (1 / self._zoom_ratio) ** self._zoom_step)

  def _update_coord(self, event: tk.Event) -> None:
    """Updates the coordinates of the pixel pointed by the mouse on the
    image."""

    # If the mouse is on the canvas but not on the image, do nothing
    if not self._check_event_pos(event):
      return

    x_coord, y_coord = self._coord_to_pix(event.x, event.y)

    self._x_pos.set(x_coord)
    self._y_pos.set(y_coord)

    self._update_pixel_value()

  def _update_pixel_value(self) -> None:
    """Updates the display of the gray level value of the pixel currently being
    pointed by the mouse."""

    try:
      self._reticle_val.set(np.average(self._original_img[self._y_pos.get(),
                                                          self._x_pos.get()]))
    except IndexError:
      self._x_pos.set(0)
      self._y_pos.set(0)
      self._reticle_val.set(np.average(self._original_img[self._y_pos.get(),
                                                          self._x_pos.get()]))

  def _coord_to_pix(self, x: int, y: int) -> (int, int):
    """Converts the coordinates of the mouse in the GUI referential to
    coordinates on the original image."""

    pil_width = self._pil_img.width
    pil_height = self._pil_img.height
    zoom_x_low, zoom_x_high = self._zoom_values.x_low, self._zoom_values.x_high
    zoom_y_low, zoom_y_high = self._zoom_values.y_low, self._zoom_values.y_high
    img_height, img_width, *_ = self._img.shape

    # Correcting the event position to make it relative to the image and not
    # the canvas
    zero_x = (self._img_canvas.winfo_width() - pil_width) / 2
    zero_y = (self._img_canvas.winfo_height() - pil_height) / 2
    corr_x = x - zero_x
    corr_y = y - zero_y

    # Convert the relative coordinate of the mouse on the display to coordinate
    # of the mouse on the original image
    x_disp = corr_x / pil_width * (zoom_x_high - zoom_x_low) * img_width
    y_disp = corr_y / pil_height * (zoom_y_high - zoom_y_low) * img_height

    # The coordinate of the upper left corner of the displayed image
    # (potentially zoomed) on the original image
    x_trim = zoom_x_low * img_width
    y_trim = zoom_y_low * img_height

    return min(int(x_disp + x_trim),
               img_width - 1), min(int(y_disp + y_trim), img_height - 1)

  def _start_move(self, event: tk.Event) -> None:
    """Stores the position of the mouse upon left-clicking on the image."""

    # If the mouse is on the canvas but not on the image, do nothing
    if not self._check_event_pos(event):
      return

    # Stores the position of the mouse relative to the top left corner of the
    # image
    zero_x = (self._img_canvas.winfo_width() - self._pil_img.width) / 2
    zero_y = (self._img_canvas.winfo_height() - self._pil_img.height) / 2
    self._move_x = event.x - zero_x
    self._move_y = event.y - zero_y

  def _move(self, event: tk.Event) -> None:
    """Drags the image upon prolonged left-clik and drag from the user."""

    # If the mouse is on the canvas but not on the image, do nothing
    if not self._check_event_pos(event):
      return

    pil_width = self._pil_img.width
    pil_height = self._pil_img.height
    zoom_x_low, zoom_x_high = self._zoom_values.x_low, self._zoom_values.x_high
    zoom_y_low, zoom_y_high = self._zoom_values.y_low, self._zoom_values.y_high

    # Getting the position delta, in the coordinates of the display
    zero_x = (self._img_canvas.winfo_width() - pil_width) / 2
    zero_y = (self._img_canvas.winfo_height() - pil_height) / 2
    delta_x_disp = self._move_x - (event.x - zero_x)
    delta_y_disp = self._move_y - (event.y - zero_y)

    # Converting the position delta to a ratio between 0 and 1 relative to the
    # size of the original image
    delta_x = delta_x_disp * (zoom_x_high - zoom_x_low) / pil_width
    delta_y = delta_y_disp * (zoom_y_high - zoom_y_low) / pil_height

    # Actually updating the display
    self._zoom_values.update_move(delta_x, delta_y)

    # Resetting the original position, otherwise the drag never ends
    self._move_x = event.x - zero_x
    self._move_y = event.y - zero_y

  def _check_event_pos(self, event: tk.Event) -> bool:
    """Checks whether the mouse is on the image, and not between the image and
    the border of the canvas. Returns :obj:`True` if it is on the image,
    :obj:`False` otherwise."""

    if self._pil_img is None:
      return False

    if abs(event.x -
           self._img_canvas.winfo_width() / 2) > self._pil_img.width / 2:
      return False
    if abs(event.y -
           self._img_canvas.winfo_height() / 2) > self._pil_img.height / 2:
      return False

    return True

  def _add_settings(self) -> None:
    """Adds the settings of the camera to the GUI."""

    # First, sort the settings by type for a nicer display
    sort_sets = sorted(self._camera.settings.values(),
                       key=lambda setting: setting.type.__name__)

    for cam_set in sort_sets:
      if cam_set.type == bool:
        self._add_bool_setting(cam_set)
      elif cam_set.type in (int, float):
        self._add_slider_setting(cam_set)
      elif cam_set.type == str:
        self._add_choice_setting(cam_set)

  def _add_bool_setting(self, cam_set) -> None:
    """Adds a setting represented by a checkbutton."""

    cam_set.tk_var = tk.BooleanVar(value=cam_set.value)
    cam_set.tk_obj = tk.Checkbutton(self._canvas_frame,
                                    text=cam_set.name,
                                    variable=cam_set.tk_var)

    cam_set.tk_obj.pack(anchor='w', side='top', expand=False, fill='none',
                        padx=5, pady=2)

  def _add_slider_setting(self, cam_set) -> None:
    """Adds a setting represented by a scale bar."""

    # The scale bar is slightly different if the setting type is int or float
    if cam_set.type == int:
      cam_set.tk_var = tk.IntVar(value=cam_set.value)
    else:
      cam_set.tk_var = tk.DoubleVar(value=cam_set.value)
    res = 1 if cam_set.type == int else (cam_set.highest -
                                         cam_set.lowest) / 1000

    cam_set.tk_obj = tk.Scale(self._canvas_frame,
                              label=f'{cam_set.name} :',
                              variable=cam_set.tk_var,
                              resolution=res,
                              orient='horizontal',
                              from_=cam_set.lowest,
                              to=cam_set.highest)

    cam_set.tk_obj.pack(anchor='center', side='top', expand=False,
                        fill='x', padx=5, pady=2)

  def _add_choice_setting(self, cam_set) -> None:
    """Adds a setting represented by a list of radio buttons."""

    cam_set.tk_var = tk.StringVar(value=cam_set.value)
    label = tk.Label(self._canvas_frame, text=f'{cam_set.name} :')
    label.pack(anchor='w', side='top', expand=False, fill='none',
               padx=12, pady=2)
    for value in cam_set.choices:
      cam_set.tk_obj = tk.Radiobutton(self._canvas_frame,
                                      text=value,
                                      variable=cam_set.tk_var,
                                      value=value)
      cam_set.tk_obj.pack(anchor='w', side='top', expand=False,
                          fill='none', padx=5, pady=2)

  def _set_variables(self) -> None:
    """Sets the text and numeric variables holding information about the
    display."""

    # The FPS counter
    self._fps_var = tk.DoubleVar(value=0.)
    self._fps_txt = tk.StringVar(value=f'fps = {self._fps_var.get():.2f}')

    # The variable for enabling or disabling the auto range
    self._auto_range = tk.BooleanVar(value=False)

    # The minimum and maximum pixel value counters
    self._min_pixel = tk.IntVar(value=0)
    self._max_pixel = tk.IntVar(value=0)
    self._min_max_pix_txt = tk.StringVar(
      value=f'min: {self._min_pixel.get():d}, '
            f'max: {self._max_pixel.get():d}')

    # The number of detected bits counter
    self._nb_bits = tk.IntVar(value=0)
    self._bits_txt = tk.StringVar(
      value=f'Detected bits: {self._nb_bits.get():d}')

    # The display of the current zoom level
    self._zoom_level = tk.DoubleVar(value=100.0)
    self._zoom_txt = tk.StringVar(
      value=f'Zoom: {self._zoom_level.get():.1f}%')

    # The display of the current pixel position and value
    self._x_pos = tk.IntVar(value=0)
    self._y_pos = tk.IntVar(value=0)
    self._reticle_val = tk.IntVar(value=0)
    self._reticle_txt = tk.StringVar(value=f'X: {self._x_pos.get():d}, '
                                           f'Y: {self._y_pos.get():d}, '
                                           f'V: {self._reticle_val.get():d}')

  def _set_traces(self) -> None:
    """Sets the traces for automatically updating the display when a variable
    is modified."""

    self._fps_var.trace_add('write', self._update_fps)

    self._min_pixel.trace_add('write', self._update_min_max)
    self._max_pixel.trace_add('write', self._update_min_max)

    self._nb_bits.trace_add('write', self._update_bits)

    self._zoom_level.trace_add('write', self._update_zoom)

    self._x_pos.trace_add('write', self._update_reticle)
    self._y_pos.trace_add('write', self._update_reticle)
    self._reticle_val.trace_add('write', self._update_reticle)

  def _update_fps(self, _, __, ___) -> None:
    """Auto-update of the FPS display."""

    self._fps_txt.set(f'fps = {self._fps_var.get():.2f}')

  def _update_min_max(self, _, __, ___) -> None:
    """Auto-update of the minimum and maximum pixel values display."""

    self._min_max_pix_txt.set(f'min: {self._min_pixel.get():d}, '
                              f'max: {self._max_pixel.get():d}')

  def _update_bits(self, _, __, ___) -> None:
    """Auto-update of the number of detected bits display."""

    self._bits_txt.set(f'Detected bits: {self._nb_bits.get():d}')

  def _update_zoom(self, _, __, ___) -> None:
    """Auto-update of the current zoom level display."""

    self._zoom_txt.set(f'Zoom: {self._zoom_level.get():.1f}%')

  def _update_reticle(self, _, __, ___) -> None:
    """Auto-update of the current pixel position and value display."""

    self._reticle_txt.set(f'X: {self._x_pos.get():d}, '
                          f'Y: {self._y_pos.get():d}, '
                          f'V: {self._reticle_val.get():d}')

  def _update_settings(self) -> None:
    """Tries to update the settings values upon clicking on the Apply Settings
    button, and checks that the settings have been correctly set."""

    for setting in self._camera.settings.values():
      # Applying all the settings that differ from the read value
      if setting.value != setting.tk_var.get():
        setting.value = setting.tk_var.get()

      # Reading the actual value of all the settings
      setting.tk_var.set(setting.value)

  def _cast_img(self, img: np.ndarray) -> None:
    """Casts the image to 8-bits as a greater precision is not required.

    May also interpolate the image to obtain a higher contrast, depending on
    the user's choice.
    """

    # First, convert BGR to RGB
    if len(img.shape) == 3:
      img = img[:, :, ::-1]

    # If the auto_range is set, adjusting the values to the range
    if self._auto_range.get():
      self._low_thresh, self._high_thresh = np.percentile(img, (3, 97))
      self._img = ((np.clip(img, self._low_thresh, self._high_thresh) -
                    self._low_thresh) * 255 /
                   (self._high_thresh - self._low_thresh)).astype('uint8')

      # The original image still needs to be saved as 8-bits
      bit_depth = np.ceil(np.log2(np.max(img) + 1))
      self._original_img = (img / 2 ** (bit_depth - 8)).astype('uint8')

    # Or if the image is not already 8 bits, casting to 8 bits
    elif img.dtype != np.uint8:
      bit_depth = np.ceil(np.log2(np.max(img) + 1))
      self._img = (img / 2 ** (bit_depth - 8)).astype('uint8')
      self._original_img = np.copy(self._img)

    # Else, the image is usable as is
    else:
      self._img = img
      self._original_img = np.copy(img)

    # Updating the information
    self._nb_bits.set(int(np.ceil(np.log2(np.max(img) + 1))))
    self._max_pixel.set(int(np.max(img)))
    self._min_pixel.set(int(np.min(img)))

  def _resize_img(self) -> None:
    """Resizes the received image so that it fits in the image canvas and
    complies with the chosen zoom level."""

    if self._img is None:
      return

    # First, apply the current zoom level
    # The width and height values are inverted in NumPy
    img_height, img_width, *_ = self._img.shape
    y_min_pix = int(img_height * self._zoom_values.y_low)
    y_max_pix = int(img_height * self._zoom_values.y_high)
    x_min_pix = int(img_width * self._zoom_values.x_low)
    x_max_pix = int(img_width * self._zoom_values.x_high)
    zoomed_img = self._img[y_min_pix: y_max_pix, x_min_pix: x_max_pix]

    # Creating the pillow image from the zoomed numpy array
    pil_img = Image.fromarray(zoomed_img)

    # Resizing the image to make it fit in the image canvas
    img_canvas_width = self._img_canvas.winfo_width()
    img_canvas_height = self._img_canvas.winfo_height()

    zoomed_img_ratio = pil_img.width / pil_img.height
    img_label_ratio = img_canvas_width / img_canvas_height

    if zoomed_img_ratio >= img_label_ratio:
      new_width = img_canvas_width
      new_height = int(img_canvas_width / zoomed_img_ratio)
    else:
      new_width = int(img_canvas_height * zoomed_img_ratio)
      new_height = img_canvas_height

    self._pil_img = pil_img.resize((new_width, new_height))

  def _display_img(self) -> None:
    """Displays the image in the center of the image canvas."""

    if self._pil_img is None:
      return

    self._image_tk = ImageTk.PhotoImage(self._pil_img)
    self._img_canvas.create_image(int(self._img_canvas.winfo_width() / 2),
                                  int(self._img_canvas.winfo_height() / 2),
                                  anchor='center', image=self._image_tk)

  def _on_img_resize(self, _: Optional[tk.Event] = None) -> None:
    """Resizes the image and updates the display when the zoom level has
    changed or the GUI has been resized."""

    self._resize_img()
    self._display_img()
    self.update()

  def _calc_hist(self) -> None:
    """Calculates the histogram of the current image."""

    if self._original_img is None:
      return

    # The histogram is calculated on a grey level image
    if len(self._original_img.shape) == 3:
      self._original_img = np.mean(self._original_img, axis=2)

    # Building the image containing the histogram
    hist, _ = np.histogram(self._original_img, bins=np.arange(257))
    hist = np.repeat(hist / np.max(hist) * 80, 2)
    hist = np.repeat(hist[np.newaxis, :], 80, axis=0)

    out_img = np.fromfunction(partial(self._hist_func, histo=hist),
                              shape=(80, 512))
    out_img = np.flip(out_img, axis=0).astype('uint8')

    # Adding vertical grey bars to indicate the limits of the auto range
    if self._auto_range.get():
      out_img[:, round(2 * self._low_thresh)] = 127
      out_img[:, round(2 * self._high_thresh)] = 127

    self._hist = out_img

  @staticmethod
  def _hist_func(x: np.ndarray, _: np.ndarray, histo: np.ndarray):
    """Function passed to the :meth:`np.fromfunction` method for building the
    histogram."""

    return np.where(x <= histo, 0, 255)

  def _resize_hist(self) -> None:
    """Resizes the histogram image to make it fit in the GUI."""

    if self._hist is None:
      return

    pil_hist = Image.fromarray(self._hist)
    hist_canvas_width = self._hist_canvas.winfo_width()
    hist_canvas_height = self._hist_canvas.winfo_height()

    self._pil_hist = pil_hist.resize((hist_canvas_width, hist_canvas_height))

  def _display_hist(self) -> None:
    """Displays the histogram image in the GUI."""

    if self._pil_hist is None:
      return

    self._hist_tk = ImageTk.PhotoImage(self._pil_hist)
    self._hist_canvas.create_image(int(self._hist_canvas.winfo_width() / 2),
                                   int(self._hist_canvas.winfo_height() / 2),
                                   anchor='center', image=self._hist_tk)

  def _on_hist_resize(self, _: tk.Event) -> None:
    """Resizes the histogram and updates the display when the GUI has been
    resized."""

    self._resize_hist()
    self._display_hist()
    self.update()

  def _update_img(self) -> None:
    """Acquires an image from the camera, casts and resizes it, calculates its
    histogram, displays them and updates the image information."""

    _, img = self._camera.get_image()
    if img is None:
      return

    self._cast_img(img)
    self._resize_img()

    self._calc_hist()
    self._resize_hist()

    self._display_img()
    self._display_hist()

    self._update_pixel_value()

    self.update()

  def _stop(self) -> None:
    """When the window is being destroyed, stop the main loop."""

    self._run = False
    sleep(0.1)
    self.destroy()
