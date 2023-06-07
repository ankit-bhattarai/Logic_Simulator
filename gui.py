"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import os
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
from guiint import GuiInterface
import webbrowser
import json

change_button_cycles = False
text_min_height = 1


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    guiint: instance of the guiint.GuiInterface() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render_axes(self, x_start, y_start,
                values, name, width,
                height): Draws axes around signal on the canvas.

    render_signal(self, x_start, y_start,
                    values, name, colour,
                    width, height): Draws a signal on the canvas based on
                                    the signal's values.

    render_signals(self): Renders all signals on the canvas.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.

    reset_pan(self, event): Resets the pan.

    reset_zoom(self, event): Resets the zoom.

    reset_view(self, event): Resets the pan and zoom.
    """

    def __init__(self, parent, guiint):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.parent = parent
        self.guiint = guiint
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.reset_pan)
        self.Bind(wx.EVT_RIGHT_DOWN, self.reset_view)

        self.canvas_colour = (1, 1, 1, 0)  # Default colour is white
        self.axes_colour = (0, 0, 0)  # Default colour is black
        self.signal_colour = (0, 0, 1)  # Default colour is blue
        self.text_colour = (0, 0, 0)  # Default colour is black

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(*self.canvas_colour)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render_axes(self, x_start, y_start, values, name, width, height):
        """Method to render axes around signal on the canvas.

        Parameters
        ----------
        x_start: int
            x coordinate of the start of the signal on the canvas.
        y_start: int
            y coordinate of the start of the signal on the canvas.
        values: list
            list of values containing the state of the signal.
        name: str
            name of the signal.
        width: int
            width of a specific time unit for the signal.
        height: int
            height of the signal.
        """
        # Initialising variables for drawing axes
        axes_offset_x = 5
        axes_offset_y = 5
        axes_offset_y = 8
        axes_offset_x = 8
        ticker_offset = 3
        value_offset_down_x = 15
        value_offset_left_x = 5
        value_offset_down_y = 5
        value_offset_left_y = 15
        x_end = x_start + width * values

        # Drawing the x axis
        GL.glColor3f(*self.axes_colour)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(x_start - axes_offset_x, y_start - axes_offset_y)
        GL.glVertex2f(x_end + axes_offset_x, y_start - axes_offset_y)
        GL.glEnd()

        # Drawing the y axis
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(x_start - axes_offset_x, y_start - axes_offset_y)
        GL.glVertex2f(x_start - axes_offset_x,
                      y_start + height + axes_offset_y)
        GL.glEnd()

        # Drawing ticks on x axis
        for i in range(1, values + 1):
            GL.glBegin(GL.GL_LINES)
            x_value = x_start + width * i
            GL.glVertex2f(x_value, y_start -
                          axes_offset_y - ticker_offset)
            GL.glVertex2f(x_value, y_start -
                          axes_offset_y + ticker_offset)
            GL.glEnd()
            self.render_text(str(i), x_value - value_offset_left_x,
                             y_start - axes_offset_y - value_offset_down_x)

        # Drawing ticks on y axis
        for i in range(0, 2):
            x_value = x_start - axes_offset_x
            y_value = y_start + height * i
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(x_value - ticker_offset, y_value)
            GL.glVertex2f(x_value + ticker_offset, y_value)
            GL.glEnd()
            self.render_text(str(i), x_value - value_offset_left_y,
                             y_value - value_offset_down_y)

        # Drawing name of the signal on top left corner of the plot
        name_offset_up = 15
        name_offset_left = 10
        self.render_text(name, x_start - name_offset_left,
                         y_start + height + name_offset_up)

    def render_signal(self, x_start, y_start, values, name,
                      width=20, height=25):
        """Method to render a single signal based on the values provided.

        Parameters
        ----------
        x_start: int
            x coordinate of the start of the signal on the canvas.
        y_start: int
            y coordinate of the start of the signal on the canvas.
        values: list
            list of values containing the state of the signal.
        name: str
            name of the signal.
        colour: tuple, optional, default=(0.0, 0.0, 1.0)
            tuple containing the RGB values of the colour of the signal.
        width: int, optional, default=20
            width of a specific time unit for the signal.
        height: int, optional, default=25
            height of the signal.
        """
        GL.glColor3f(*self.signal_colour)
        GL.glBegin(GL.GL_LINE_STRIP)
        x = x_start
        y = y_start
        for i, value in enumerate(values):
            if value is None:  # Ignore and move to next value if None
                x += width
            else:
                if value == 0:
                    y = y_start
                else:
                    y = y_start + height
                x_next = x + width
                GL.glVertex2f(x, y)
                GL.glVertex2f(x_next, y)
                x = x_next
        GL.glEnd()
        self.render_axes(x_start, y_start, len(values), name, width, height)

    def render_signals(self):
        """Method to render all signals."""
        # Initialising variables for drawing signals
        height_above_signal = 100
        base_x = 40
        base_y = 80

        for i, (name, values) in enumerate(self.guiint.get_signals().items()):
            self.render_signal(base_x, base_y + i * height_above_signal,
                               values, name)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        # self.render_text(text, 10, 10)
        # Draw the signal traces
        self.render_signals()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.reset_view()  # Rest the zoom and pan whenever screen is resized
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(*self.text_colour)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def reset_pan(self, event=None):
        """Reset the pan."""
        self.pan_x = 0
        self.pan_y = 0
        self.init = False

    def reset_zoom(self, event=None):
        """Reset the zoom."""
        self.zoom = 1.0
        self.init = False

    def reset_view(self, event=None):
        """Reset the view to the initial view and zoom."""
        self.reset_pan()
        self.reset_zoom()

    def change_colour(self):
        """Change the colour scheme of the canvas.

        Called when colour mode is changed by the parent. The colour attributes
        are set to the appropriate values and the canvas is refreshed."""
        colour_mode = self.parent.colour_mode
        colour_dict = self.parent.colour_palette[colour_mode]
        # Reset the attributes as per new colour scheme
        self.canvas_colour = colour_dict["Canvas Colour"]
        self.axes_colour = colour_dict["Axes Colour"]
        self.signal_colour = colour_dict["Signal Colour"]
        self.text_colour = colour_dict["Canvas Text Colour"]
        # Re-render the canvas
        self.init = False
        self.Refresh()


class SwitchPanel(wx.Panel):
    """
    Panel for the switches

    This panel will contain the functionality for the showing the switches'
    state and changing their state.

    Parameters
    ----------
    parent : parent Window
    guiint : instance of the guiint.GuiInterface() class.

    Public Methods
    --------------
    renderSwitchBoxes(self): Renders the switch boxes based on their state.

    OnComboSwitch(self, event): Handles the event when a switch is selected in
                                the combo box.
    """

    def __init__(self, parent, guiint):
        """Method initalises the panel."""
        super().__init__(parent=parent)  # Initialise
        self.parent = parent
        self.grand_parent = parent.parent
        self.guiint = guiint

        # Creating the sizers

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.Add(self.left_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.right_sizer, 0, wx.ALL, 5)

        # Creating the widgets

        # Text for the switches
        SWITCH_STATE_TEXT = self.grand_parent.GetTranslation(
            "SELECT SWITCH AND STATE") + ":"
        self.switch_text = wx.StaticText(
            self, wx.ID_ANY, SWITCH_STATE_TEXT)
        self.left_sizer.Add(self.switch_text, 1, wx.EXPAND,
                            wx.ALIGN_LEFT | wx.ALL, 10)

        combo_id_switch = wx.NewIdRef()
        combo_choices = list(self.guiint.list_of_switches())
        self.combo_box_switch = wx.ComboBox(self, combo_id_switch,
                                            choices=combo_choices,
                                            style=wx.TE_PROCESS_ENTER)
        # Bind the combo box
        self.combo_box_switch.Bind(wx.EVT_COMBOBOX, self.OnComboSwitch)
        # Want it to work for both enter and selection
        self.combo_box_switch.Bind(wx.EVT_TEXT_ENTER, self.OnComboSwitch)
        # Add combo box to switch sizer
        self.left_sizer.Add(self.combo_box_switch, 1,
                            wx.ALIGN_LEFT, wx.ALL, 10)
        self.switch_text = None  # The option chosen on the combo box

        self.switch_state_display = wx.StaticText(self, wx.ID_ANY, "")
        self.right_sizer.Add(self.switch_state_display, 1,
                             wx.EXPAND, wx.ALIGN_RIGHT | wx.ALL, 10)

        # Create single button - SWITCHES state from the current state
        self.switch_button_id = wx.NewIdRef(count=1)
        self.button_switch = wx.Button(
            self, self.switch_button_id, "")

        # Bind button
        self.button_switch.Bind(wx.EVT_BUTTON, self.OnButtonSwitch)

        # Add buttons to switch state sizer
        self.right_sizer.Add(self.button_switch, 1, wx.ALIGN_RIGHT, wx.ALL, 10)
        # Initially hide the buttons
        self.button_switch.Hide()
        self.switch_state_display.Hide()

        self.SetSizer(self.main_sizer)

    def renderSwitchBoxes(self):
        """Method renders the switch boxes based on their current state."""
        # Get the current switch
        switch_text = self.switch_text
        if switch_text is None:  # This can't ever happen
            # As this function is only called when the combo box is changed
            pass
        switch_state = self.guiint.get_switch_state(switch_text)
        # Show the buttons
        self.button_switch.Show()
        # Set the text of the buttons based on the current state - ACTIONS
        if switch_state == 0:
            self.button_switch.SetLabel(
                self.grand_parent.GetTranslation("CLOSE"))
        else:  # switch_state == 1
            self.button_switch.SetLabel(
                self.grand_parent.GetTranslation("OPEN"))

        self.main_sizer.Layout()
        self.parent.GetSizer().Layout()
        # self.grand_parent.GetSizer().Layout()

    def OnComboSwitch(self, event):
        """Method called when the combo box is changed.

        This method will change the switch text and render the switch boxes.
        It also displays the appropriate message on the canvas."""
        combo_value = self.combo_box_switch.GetValue()
        if combo_value in self.guiint.list_of_switches():
            self.switch_text = combo_value  # Only change this if valid
            switch_state = self.guiint.get_switch_state(self.switch_text)

            self.switch_state_display.Show()
            if switch_state == 1:
                switch_state_string = self.grand_parent.GetTranslation(
                    "CLOSED")
            else:
                switch_state_string = self.grand_parent.GetTranslation(
                    "OPENED")

            self.switch_state_display.SetLabel(
                f'{self.switch_text} : {switch_state_string}')

            self.renderSwitchBoxes()
            self.grand_parent.canvas.render(
                f"Combo box changed. New_value: {combo_value}")
        else:
            self.grand_parent.canvas.render("Invalid Selection Made")

        self.main_sizer.Layout()
        self.parent.GetSizer().Layout()
        # self.grand_parent.GetSizer().Layout()

    def OnButtonSwitch(self, event):
        """Method called when button is pressed.

        This method will change the state of the switch and render the
        switch boxes."""
        switch_text = self.switch_text
        if switch_text is None:  # This can't ever happen
            pass
        else:
            switch_state = self.guiint.get_switch_state(switch_text)
            # Flip the switch
            desired_switch_state = 1 if switch_state == 0 else 0
            self.guiint.set_switch_state(
                switch_text, desired_switch_state)  # Render the change
            self.renderSwitchBoxes()

            switch_state_string = self.grand_parent.GetTranslation(
                "CLOSED") if desired_switch_state == 1 else self.grand_parent.GetTranslation("OPENED")
            self.switch_state_display.SetLabel(
                f'{self.switch_text}: {switch_state_string}')

            text = f"Switch {switch_text} is now {switch_state_string}."
            self.grand_parent.canvas.render(text)

            self.main_sizer.Layout()
            self.parent.GetSizer().Layout()
            # self.grand_parent.GetSizer().Layout()


class MonitorPanel(wx.Panel):
    """
    Panel for the monitors

    This panel will have the functionalities of viewing which outputs are being
    monitored as well as add or remove outputs to be monitored.

    Parameters
    ----------
    parent : parent window
    guiint: instance of the guiint.GuiInterface() class.

    Public Methods
    --------------
    None
    """

    def __init__(self, parent, guiint):
        """Method initialises the panel."""
        super().__init__(parent=parent)  # Initialise
        self.parent = parent
        self.grand_parent = self.parent.parent
        self.guiint = guiint
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.left_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.right_sizer, 1, wx.EXPAND | wx.ALL, 10)

        # Text for the monitors
        MONITOR_SELECT_TEXT = self.grand_parent.GetTranslation(
            "SELECT MONITOR") + ": "
        self.monitor_text = wx.StaticText(
            self, wx.ID_ANY, MONITOR_SELECT_TEXT)
        self.left_sizer.Add(self.monitor_text, 1, wx.EXPAND,
                            wx.ALIGN_LEFT | wx.ALL, 10)

        # Have to create the combo box for the monitors
        combo_id_monitor = wx.NewIdRef()
        combo_choices = list(self.guiint.list_of_outputs())
        self.combo_box_monitor = wx.ComboBox(self, combo_id_monitor,
                                             choices=combo_choices,
                                             style=wx.TE_PROCESS_ENTER)
        # Bind the combo box
        self.combo_box_monitor.Bind(wx.EVT_COMBOBOX, self.OnComboMonitor)
        # Want it to work for both enter and selection
        self.combo_box_monitor.Bind(wx.EVT_TEXT_ENTER, self.OnComboMonitor)
        self.monitor_state_display = wx.StaticText(self, wx.ID_ANY, "")
        self.right_sizer.Add(self.monitor_state_display, 1,
                             wx.EXPAND, wx.ALIGN_RIGHT | wx.ALL, 10)

        # Add combo box to monitor sizer
        self.left_sizer.Add(self.combo_box_monitor, 1,
                            wx.ALIGN_LEFT, wx.ALL, 10)
        self.monitor_text = None  # The option chosen on the combo box

        # For representing the state of the monitor, will have two buttons
        # The button corresponding to the current state of the monitor
        # will be green and the other one will be red

        # Create the two buttons
        self.monitor_button_id = wx.NewIdRef(count=1)
        self.button_monitor = wx.Button(self, self.monitor_button_id,
                                        "")

        # Bind buttons
        self.button_monitor.Bind(wx.EVT_BUTTON, self.OnButtonMonitor)

        # Add buttons to monitor state sizer
        self.right_sizer.Add(self.button_monitor, 1,
                             wx.ALIGN_RIGHT, wx.ALL, 10)
        # Initially hide the buttons
        self.button_monitor.Hide()

        # Add the sizer to the panel
        self.SetSizer(self.main_sizer)

    def renderMonitorButtons(self):
        """Method renders the monitor buttons based on their current state."""
        # Get the current monitor
        monitor_text = self.monitor_text
        if monitor_text is None:  # This can't ever happen
            # As this function is only called when the combo box is changed
            pass
        monitor_state = self.guiint.get_output_state(monitor_text)
        # Show the buttons
        self.button_monitor.Show()
        # Set the text of the buttons based on the current state - ACTIONS
        if monitor_state == 0:
            self.button_monitor.SetLabel(
                self.grand_parent.GetTranslation("ADD") + " " +
                self.grand_parent.GetTranslation("MONITOR"))
        else:  # monitor_state == 1
            self.button_monitor.SetLabel(
                self.grand_parent.GetTranslation("HIDE") + " " + self.grand_parent.GetTranslation("MONITOR"))

        self.main_sizer.Layout()
        self.parent.GetSizer().Layout()
        # self.grand_parent.GetSizer().Layout()

    def OnComboMonitor(self, event):
        """Method called when the combo box is changed.

        Method changes the monitor text attribute and calls the
        renderMonitorButtons() method.

        It also sends the appropriate message to the canvas."""
        combo_value = self.combo_box_monitor.GetValue()
        if combo_value in self.guiint.list_of_outputs():
            self.monitor_text = combo_value  # Only change this if valid
            self.renderMonitorButtons()

            monitor_state = self.guiint.get_output_state(self.monitor_text)
            monitor_state_string = self.grand_parent.GetTranslation(
                "MONITORED") if monitor_state == 1 else self.grand_parent.GetTranslation("HIDDEN")
            self.monitor_state_display.SetLabel(
                f'{self.monitor_text}: {monitor_state_string}')

            self.grand_parent.canvas.render(
                f"Combo box changed. New_value: {combo_value}")
            self.main_sizer.Layout()
            # self.parent.GetSizer().Layout()
            # self.grand_parent.GetSizer().Layout()

        else:
            self.grand_parent.canvas.render("Invalid Selection Made")

    def OnButtonMonitor(self, event):
        """Method called when the monitor button is pressed.

        Method changes the state of the monitor and calls the
        renderMonitorButtons() method.
        """
        monitor_text = self.monitor_text
        if monitor_text is None:
            pass
        else:
            monitor_state = self.guiint.get_output_state(monitor_text)
            desired_monitor_state = 1 if monitor_state == 0 else 0
            self.guiint.set_output_state(monitor_text, desired_monitor_state)
            self.renderMonitorButtons()

            monitor_state_string = self.grand_parent.GetTranslation(
                "MONITORED") if desired_monitor_state == 1 else self.grand_parent.GetTranslation("HIDDEN")
            self.monitor_state_display.SetLabel(
                f'{self.monitor_text}: {monitor_state_string}')

            text = f"Switch {monitor_text} is now {monitor_state_string}."
            self.grand_parent.canvas.render(text)
            self.main_sizer.Layout()
            self.parent.GetSizer().Layout()
            # self.grand_parent.GetSizer().Layout()


class RunPanel(wx.Panel):
    """ Panel for the run button and the cycles text box.

    This panel is used for containing the run and continue buttons as well as
    a spin control object for the user to enter the number of cycles to run.

    Parameters
    ----------
    parent : parent Frame
    guiint: instance of the guiint.GuiInterface() class.

    Public Methods
    --------------
    None
    """

    def __init__(self, parent, guiint):
        """Method initalises the panel"""
        super().__init__(parent=parent)  # Initialise
        self.parent = parent
        self.grand_parent = self.parent.parent
        self.guiint = guiint

        # Creating the sizers
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.middle_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the sizers to the main sizer
        self.main_sizer.Add(self.top_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.middle_sizer, 0, wx.ALL, 5)

        # Add the text on the top
        CYCLES_TEXT = self.grand_parent.GetTranslation("CYCLES") + ": "
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, CYCLES_TEXT)
        self.top_sizer.Add(self.cycles_text, 1, wx.EXPAND | wx.ALL, 10)

        # Create the spin object
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "2", size=wx.Size(120, 10))
        # Can't have 0 cycles, default max seems to be 100!
        self.spin.SetMin(1)
        # Bind the spin object
        self.spin.Bind(wx.EVT_SPINCTRL, self.OnSpin)
        # Add spin to top sizer
        # self.spin.SetMinSize((wx.DefaultCoord, text_min_height))
        self.top_sizer.Add(self.spin, 1, wx.EXPAND | wx.ALL, 5)

        # Create the two buttons
        self.run_button_id, self.continue_button_id = wx.NewIdRef(count=2)
        self.button_run = wx.Button(
            self, self.run_button_id, self.grand_parent.GetTranslation("RUN"))
        self.button_continue = wx.Button(self, self.continue_button_id,
                                         self.grand_parent.GetTranslation("CONTINUE"))
        # Bind buttons
        self.button_run.Bind(wx.EVT_BUTTON, self.OnButtonRun)
        self.button_continue.Bind(wx.EVT_BUTTON, self.OnButtonContinue)
        # Add buttons to bottom sizer
        self.middle_sizer.Add(self.button_run, 1, wx.ALL, 5)
        self.middle_sizer.Add(self.button_continue, 1, wx.ALL, 5)
        # Want to hide this until the run button is pressed!
        self.button_continue.Hide()

        # Set the sizer
        self.SetSizer(self.main_sizer)

    def OnButtonRun(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        success = self.guiint.run_network(self.spin.GetValue())
        if isinstance(success, str):
            translated_message = self.grand_parent.GetTranslation(success)
            title = self.grand_parent.GetTranslation("Message")
            wx.MessageBox(translated_message, title, wx.OK | wx.ICON_ERROR)
        self.grand_parent.canvas.render(text)
        self.button_continue.Show()
        self.grand_parent.canvas.render_signals()
        self.main_sizer.Layout()

    def OnButtonContinue(self, event):
        """Handle the event when the user clicks the continue button."""
        text = "Continue button pressed."
        success = self.guiint.continue_network(self.spin.GetValue())
        if isinstance(success, str):
            translated_message = self.grand_parent.GetTranslation(success)
            title = self.grand_parent.GetTranslation("Message")
            wx.MessageBox(translated_message, title, wx.OK | wx.ICON_ERROR)
        self.grand_parent.canvas.render(text)
        self.grand_parent.canvas.render_signals()
        self.Layout()

    def OnSpin(self, event):
        """Handle the event when the user changes the spin value."""
        spin_value = self.spin.GetValue()
        self.grand_parent.canvas.render(f"Spin value: {spin_value}")


class RightPanel(wx.Panel):
    """ Panel for the run button and the cycles text box.

    This panel is the right panel of the GUI. It contains various sub panels
    for the run, switch and monitor controls

    Parameters
    ----------
    parent : parent Frame
    guiint: instance of the guiint.GuiInterface() class.

    Public Methods
    --------------
    None
    """

    def __init__(self, parent, guiint):
        """Method initalises the panel"""
        super().__init__(parent=parent)  # Initialise
        self.parent = parent
        self.guiint = guiint

        # Creating the sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create and add the run, switch and monitor panels to the main sizer
        self.run_panel = RunPanel(self, guiint)
        main_sizer.Add(self.run_panel, 0, wx.ALL, 5)

        self.switch_panel = SwitchPanel(self, guiint)
        main_sizer.Add(self.switch_panel, 0, wx.ALL, 5)

        self.monitor_panel = MonitorPanel(self, guiint)
        main_sizer.Add(self.monitor_panel, 0, wx.ALL, 5)

        # Set the sizer for the panel
        self.SetSizer(main_sizer)

    def change_colour_child(self, child):
        """Change the colour of the children of 'child'.
        This depends on the type of the children - StaticText or Button"""
        colour_dict = self.parent.colour_palette[self.parent.colour_mode]
        panel_colour = colour_dict["Panel Colour"]
        text_colour = colour_dict["Panel Text Colour"]
        # Change the background panel colour of the child
        child.SetBackgroundColour(panel_colour)
        # Recursively change the background/text colour for all panels
        for gchild in child.GetChildren():
            if isinstance(gchild, wx.StaticText):
                gchild.SetForegroundColour(text_colour)
            if isinstance(gchild, wx.Button):
                gchild.SetBackgroundColour(panel_colour)
        self.Refresh()
        self.Layout()
        self.parent.GetSizer().Layout()

    def change_colour(self):
        """Change the colour scheme of the panel - method called by the parent.
        """
        for child in self.GetChildren():
            self.change_colour_child(child)
        colour_dict = self.parent.colour_palette[self.parent.colour_mode]
        panel_colour = colour_dict["Panel Colour"]
        self.SetBackgroundColour(panel_colour)
        self.Refresh()


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors,
                 scanner=None, load_graphically=False, locale=None,
                 locale_text=None):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))
        # File path for circuit file which can be chosen from the GUI
        self.file_path = None
        self.guiint = None
        self.load_dictionary(locale_text)
        if locale is not None:
            allowed_locale = [wx.LANGUAGE_CHINESE_SIMPLIFIED,
                              wx.LANGUAGE_ENGLISH]
            if locale not in allowed_locale:
                print("Locale not supported, using default locale - English")
            else:
                locale = wx.Locale(locale)
                wx.Locale.AddCatalogLookupPathPrefix('locale')

        if load_graphically:
            self.start_graphically_control()
            # Can only reach this stage if a valid circuit file has been loaded
            # successfully, thus file_path is valid
        else:
            guiint = GuiInterface(names, devices, network, monitors, scanner)
            self.guiint = guiint

        if self.guiint is not None:
            # Configure the file menu
            fileMenu = wx.Menu()
            viewMenu = wx.Menu()
            helpMenu = wx.Menu()
            menuBar = wx.MenuBar()
            self.open_id, self.help_id_1, self.help_id_2 = wx.NewIdRef(count=3)
            self.reset_id, self.def_file_show_id, self.change_colour_id = wx.NewIdRef(
                count=3)
            fileMenu.Append(self.open_id,  self.GetTranslation("&Open"))
            fileMenu.Append(wx.ID_ABOUT, self.GetTranslation("&About"))
            fileMenu.Append(wx.ID_EXIT,  self.GetTranslation("&Exit"))
            viewMenu.Append(self.reset_id, self.GetTranslation("&Reset"))
            viewMenu.Append(self.def_file_show_id,
                            self.GetTranslation("&Show Definition File"))
            viewMenu.Append(self.change_colour_id,
                            self.GetTranslation("&Change Colour"))
            helpMenu.Append(self.help_id_1,
                            self.GetTranslation("&EBNF Syntax"))
            helpMenu.Append(self.help_id_2,
                            self.GetTranslation("&User Guide"))
            menuBar.Append(fileMenu, self.GetTranslation("&File"))
            menuBar.Append(viewMenu, self.GetTranslation("&View"))
            menuBar.Append(helpMenu,  self.GetTranslation("&Help"))
            self.SetMenuBar(menuBar)

            # Canvas for drawing signals
            self.canvas = MyGLCanvas(self, self.guiint)

            # Bind events to widgets
            self.Bind(wx.EVT_MENU, self.on_menu)

            # Configure sizers for layout
            main_sizer = wx.BoxSizer(wx.HORIZONTAL)

            main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)

            right_panel = RightPanel(self, self.guiint)
            main_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)

            self.SetSizeHints(600, 600)
            self.SetSizer(main_sizer)

        # String are wxpython colour names, tuples are RGB{A} for opengl render
        self.colour_palette = {"Light Mode": {"Panel Text Colour": "black",
                                              "Panel Colour": "light grey",
                                              "Canvas Colour": (1, 1, 1, 0),
                                              "Signal Colour": (0, 0, 1),
                                              "Axes Colour": (0, 0, 0),
                                              "Canvas Text Colour": (0, 0, 0)},
                               "Dark Mode": {"Panel Text Colour": "white",
                                             "Panel Colour": "black",
                                             "Canvas Colour": (0.1725, 0.1725,
                                                               0.1725, 1),
                                             "Signal Colour": (1, 1, 1),
                                             "Axes Colour": (1, 1, 1),
                                             "Canvas Text Colour": (1, 1, 1)}}

        self.colour_mode = "Light Mode"
        # Start of in light mode
        self.change_colour()

    def load_dictionary(self, locale_language):
        # English or some other language not supported
        if locale_language is not None:
            file = open(f"translations/{locale_language}.json", "r")
            self.translation_dict = json.load(file)
            file.close()
        else:
            self.translation_dict = {}

    def GetTranslation(self, string):
        translated = string
        if string[0] == "&":
            translated = "&" + \
                self.translation_dict.get(string[1:], string[1:])
        else:  # No &
            translated = self.translation_dict.get(string, string)
        # Return the string as it is if translation not found or translation
        return translated

    def change_colour(self):
        """Change the colour of the GUI by calling the change_colour method of
        the child panels."""
        for child in self.GetChildren():
            # Change the colour of right panel
            if isinstance(child, wx.Panel):
                child.change_colour()
            # Change the colour of the canvas
            if isinstance(child, wxcanvas.GLCanvas):
                child.change_colour()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        elif Id == wx.ID_ABOUT:
            about_string = self.GetTranslation("&About") + " Logsim"
            wx.MessageBox("Logic Simulator\nCreated by Ankit Adhi Jessy\n2023",
                          about_string, wx.ICON_INFORMATION | wx.OK)
        elif Id == self.open_id:
            self.load_graphically()

        elif Id == self.help_id_1:
            with open("EBNF.txt", "r") as f:
                # wx.MessageBox(f.read(), "EBNF Syntax")
                box = MyDialog(self, message=f.read(),
                               title=self.GetTranslation("EBNF Syntax"),
                               allow_wrap=False)
                box.ShowModal()
                box.Destroy()

        elif Id == self.help_id_2:
            # wx.MessageBox("User Guide", "User Guide")
            webbrowser.open(f"{os.getcwd()}/UserGuide.pdf")
        elif Id == self.reset_id:
            self.canvas.reset_view()
        elif Id == self.def_file_show_id:
            file_path = self.guiint.scanner.path
            with open(file_path, "r") as f:
                title = self.GetTranslation(
                    "Definition File") + " - " + file_path
                box = MyDialog(self, message=f.read(),
                               title=title,
                               editable=False)
                box.ShowModal()
                box.Destroy()

        elif Id == self.change_colour_id:
            # Flip the current colour mode and call the change_colour method
            if self.colour_mode == "Light Mode":
                self.colour_mode = "Dark Mode"
                self.change_colour()
            else:  # Self.colour_mode == "Dark Mode"
                self.colour_mode = "Light Mode"
                self.change_colour()

    def start_graphically(self):
        """Load the circuit definition file directly from the GUI."""
        title = self.GetTranslation("Open")
        title += " "
        title += self.GetTranslation("Definition File")
        openFileDialog = wx.FileDialog(self, title, "",
                                       "",
                                       wildcard="TXT files (*.txt)|*.txt",
                                       style=wx.FD_OPEN +
                                       wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            # The user has cancelled the dialog, close the program
            self.Close(True)
            return None
        # Proceed loading the file chosen by the user
        self.file_path = openFileDialog.GetPath()
        # These don't need to be initialised
        guiint = GuiInterface(None, None, None, None, None)
        success, message = guiint.update_network(self.file_path)
        if success:
            self.guiint = guiint
            if message == "":
                display_message = "Circuit loaded successfully.\n"
                title = self.GetTranslation("Circuit Loaded")
            else:  # There is a message to  be printed, but overall the
                # circuit is valid. It is only a warning
                display_message = "Circuit loaded with warnings.\n"
                display_message += "Warnings: \n\n"
                display_message += message
                title = self.GetTranslation("Warnings Present")
            box = MyDialog(self, message=display_message,
                           title=title)
            box.ShowModal()
            box.Destroy()
            return True
        else:
            error_display = "Invalid circuit definition file.\n"
            error_display += "Errors: \n\n"
            error_display += message
            title = self.GetTranslation("Errors Present")
            box = MyDialog(self, message=error_display,
                           title=title)
            box.ShowModal()
            box.Destroy()
            return False

    def start_graphically_control(self):
        """Ensure that a valid circuit is loaded before GUI starts.

        Method loops until a valid circuit is loaded, or the user cancels
        the operation."""
        while True:
            success = self.start_graphically()
            if success is None:
                self.Close(True)
                return
            if success:
                break
            else:
                continue
        return

    def load_graphically(self):
        """Load the circuit definition file directly from the GUI.

        This is called when the user selects the "Open" option from the menu.
        The selected file is sent to the GuiInterface object to be parsed and
        checked for errors. If errrors exist, they will be displayed in a
        dialog box and the current circuit will not be overwritten. If no
        errors exist, the circuit will be loaded and canvas updated."""
        title = self.GetTranslation("Open")
        title += " "
        title += self.GetTranslation("Definition File")
        openFileDialog = wx.FileDialog(self, title, "", "",
                                       wildcard="TXT files (*.txt)|*.txt",
                                       style=wx.FD_OPEN +
                                       wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return  # Cancelled, nothing selected
        # Proceed loading the file chosen by the user
        self.file_path = openFileDialog.GetPath()
        success, message = self.guiint.update_network(self.file_path)
        if success:
            if message == "":
                self.canvas.render("Circuit loaded successfully.")
                self.canvas.render_signals()
            else:  # There is a message to  be printed, but overall the
                # circuit is valid. It is only a warning
                error_display = "Circuit loaded with warnings.\n"
                error_display += "Warnings: \n\n"
                error_display += message
                box = MyDialog(self, message=error_display,
                               title="Warnings Present")
                box.ShowModal()
                box.Destroy()
        else:
            error_display = "Invalid circuit definition file.\n"
            error_display += "Errors: \n\n"
            error_display += message
            box = MyDialog(self, message=error_display,
                           title="Errors Present")
            box.ShowModal()
            box.Destroy()


class MyDialog(wx.Dialog):
    """Dialog box for displaying text.

    Class displays text in a dialog box to contain long messages including
    code, error messages, etc

    Parameters
    ----------
    parent : parent window
    message : string
        Message to be displayed
    title : string
        Title of the dialog box
    editable : bool
        Whether the text is editable or not
    allow_wrap : bool
        Whether the text can be wrapped or not

    Public Methods
    --------------
    None
    """

    def __init__(self, parent, message, title, editable=False,
                 allow_wrap=False):
        """Initialize the dialog box."""
        super(MyDialog, self).__init__(parent, title=title, size=(1000, 800))
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        if allow_wrap:
            self.text = wx.TextCtrl(self, value=message, style=wx.TE_MULTILINE)
        else:
            self.text = wx.TextCtrl(
                self, value=message,
                style=wx.TE_MULTILINE | wx.TE_DONTWRAP | wx.HSCROLL)
        self.text.SetEditable(editable)
        self.text.SetInsertionPoint(0)

        # Create a monospaced font and set it for the text control
        # This is so that when error messages are displayed with the arrow,
        # the spacing is appropriate such that the arrow points to the
        # desired character
        font = wx.Font(10, wx.FONTFAMILY_TELETYPE,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text.SetFont(font)

        sizer.Add(self.text, 1, wx.EXPAND)

        self.SetSizer(sizer)
