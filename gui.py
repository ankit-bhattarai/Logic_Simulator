"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
from guiint import GuiInterface

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

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
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
        axes_offset_x = 5
        axes_offset_y = 5
        GL.glColor3f(0.0, 0.0, 0.0)  # Black
        GL.glBegin(GL.GL_LINES)
        axes_offset_y = 8
        axes_offset_x = 8
        ticker_offset = 3
        value_offset_down_x = 15
        value_offset_left_x = 5
        value_offset_down_y = 5
        value_offset_left_y = 15
        x_end = x_start + width * values
        GL.glVertex2f(x_start - axes_offset_x, y_start - axes_offset_y)
        GL.glVertex2f(x_end + axes_offset_x, y_start - axes_offset_y)
        GL.glEnd()
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
                      colour=(0.0, 0.0, 1.0),
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
        GL.glColor3f(*colour)
        GL.glBegin(GL.GL_LINE_STRIP)
        x = x_start
        y = y_start
        for i, value in enumerate(values):
            if value is None:
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
        self.render_text(text, 10, 10)
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
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
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
        self.switch_text = wx.StaticText(
            self, wx.ID_ANY, "Select Switch and state: ")
        self.left_sizer.Add(self.switch_text, 1, wx.EXPAND | wx.ALL, 10)

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
        self.left_sizer.Add(self.combo_box_switch, 1, wx.ALL, 5)
        self.switch_text = None  # The option chosen on the combo box

        # For representing the state of the switch, will have two buttons
        # The button corresponding to the current state of the switch
        # will be green and the other one will be red

        # Create the two buttons
        self.switch_button_id_0, self.switch_button_id_1 = wx.NewIdRef(count=2)
        self.button_switch_0 = wx.Button(
            self, self.switch_button_id_0, "Open")
        self.button_switch_1 = wx.Button(
            self, self.switch_button_id_1, "Wired")

        # Bind buttons
        self.button_switch_0.Bind(wx.EVT_BUTTON, self._OnButtonSwitch0)
        self.button_switch_1.Bind(wx.EVT_BUTTON, self._OnButtonSwitch1)

        # Add buttons to switch state sizer
        self.right_sizer.Add(self.button_switch_0, 1, wx.ALL, 5)
        self.right_sizer.Add(self.button_switch_1, 1, wx.ALL, 5)
        # Initially hide the buttons
        self.button_switch_0.Hide()
        self.button_switch_1.Hide()

        # Specify the colors for the buttons
        self.red = wx.Colour(226, 126, 126, 255)
        self.green = wx.Colour(0, 255, 0, 255)

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
        self.button_switch_0.Show()
        self.button_switch_1.Show()
        # Set the colors of the buttons
        if switch_state == 0:
            # Change color of button 0 to green and button 1 to red
            self.button_switch_0.SetBackgroundColour(self.green)
            self.button_switch_1.SetBackgroundColour(self.red)
        else:  # switch_state == 1
            # Change color of button 0 to red and button 1 to green
            self.button_switch_0.SetBackgroundColour(self.red)
            self.button_switch_1.SetBackgroundColour(self.green)
        self.main_sizer.Layout()
        self.parent.GetSizer().Layout()
        self.grand_parent.GetSizer().Layout()

    def OnComboSwitch(self, event):
        """Method called when the combo box is changed.

        This method will change the switch text and render the switch boxes.
        It also displays the appropriate message on the canvas."""
        combo_value = self.combo_box_switch.GetValue()
        if combo_value in self.guiint.list_of_switches():
            self.switch_text = combo_value  # Only change this if valid
            self.renderSwitchBoxes()
            self.grand_parent.canvas.render(
                f"Combo box changed. New_value: {combo_value}")
        else:
            self.grand_parent.canvas.render("Invalid Selection Made")

    def _OnButtonSwitch0(self, event):
        """Method called when button 0 is pressed.

        This method will change the state of the switch to 0 and render the
        switch boxes."""
        switch_text = self.switch_text
        if switch_text is None:
            pass  # This can't ever happen
        else:
            self.guiint.set_switch_state(switch_text, 0)
            self.renderSwitchBoxes()
        text = f"Switch {switch_text} is now open."
        self.grand_parent.canvas.render(text)

    def _OnButtonSwitch1(self, event):
        """Method called when button 1 is pressed.

        This method will change the state of the switch to 1 and render the
        switch boxes."""
        switch_text = self.switch_text
        if switch_text is None:
            pass  # This can't ever happen
        else:
            self.guiint.set_switch_state(switch_text, 1)
            self.renderSwitchBoxes()
        text = f"Switch {switch_text} is now closed."

        self.grand_parent.canvas.render(text)


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
        self.main_sizer.Add(self.left_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.right_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # # Specify the colors for the buttons
        self.red = wx.Colour(226, 126, 126, 255)
        self.green = wx.Colour(0, 255, 0, 255)

        # Text for the monitors
        self.monitor_text = wx.StaticText(
            self, wx.ID_ANY, "Select Monitor: ")
        self.left_sizer.Add(self.monitor_text, 1, wx.EXPAND | wx.ALL, 10)

        # Have to create the combo box for the monitors
        combo_id_monitor = wx.NewIdRef()
        combo_choices = list(self.guiint.list_of_outputs())
        self.combo_box_monitor = wx.ComboBox(self, combo_id_monitor,
                                             choices=combo_choices,
                                             style=wx.TE_PROCESS_ENTER)
        # Bind the combo box
        self.combo_box_monitor.Bind(wx.EVT_COMBOBOX, self._OnComboMonitor)
        # Want it to work for both enter and selection
        self.combo_box_monitor.Bind(wx.EVT_TEXT_ENTER, self._OnComboMonitor)

        # Add combo box to monitor sizer
        self.left_sizer.Add(self.combo_box_monitor, 1, wx.ALL, 5)
        self.monitor_text = None  # The option chosen on the combo box

        # For representing the state of the monitor, will have two buttons
        # The button corresponding to the current state of the monitor
        # will be green and the other one will be red

        # Create the two buttons
        self.monitor_button_id_0, self.monitor_button_id_1 = wx.NewIdRef(
            count=2)
        self.button_monitor_0 = wx.Button(
            self, self.monitor_button_id_0, "Hide")
        self.button_monitor_1 = wx.Button(
            self, self.monitor_button_id_1, "Show")

        # Bind buttons
        self.button_monitor_0.Bind(wx.EVT_BUTTON, self._OnButtonMonitor0)
        self.button_monitor_1.Bind(wx.EVT_BUTTON, self._OnButtonMonitor1)

        # Add buttons to monitor state sizer
        self.right_sizer.Add(self.button_monitor_0, 1, wx.ALL, 5)
        self.right_sizer.Add(self.button_monitor_1, 1, wx.ALL, 5)
        # Initially hide the buttons
        self.button_monitor_0.Hide()
        self.button_monitor_1.Hide()

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
        self.button_monitor_0.Show()
        self.button_monitor_1.Show()
        # Set the colors of the buttons
        if monitor_state == 0:
            # Change color of button 0 to green and button 1 to red
            self.button_monitor_0.SetBackgroundColour(self.green)
            self.button_monitor_1.SetBackgroundColour(self.red)
        else:  # monitor_state == 1
            # Change color of button 0 to red and button 1 to green
            self.button_monitor_0.SetBackgroundColour(self.red)
            self.button_monitor_1.SetBackgroundColour(self.green)
        self.main_sizer.Layout()
        self.parent.GetSizer().Layout()
        self.grand_parent.GetSizer().Layout()

    def _OnComboMonitor(self, event):
        """Method called when the combo box is changed.

        Method changes the monitor text attribute and calls the
        _renderMonitorButtons() method.

        It also sends the appropriate message to the canvas."""
        combo_value = self.combo_box_monitor.GetValue()
        if combo_value in self.guiint.list_of_outputs():
            self.monitor_text = combo_value  # Only change this if valid
            self.renderMonitorButtons()
            self.grand_parent.canvas.render(
                f"Combo box changed. New_value: {combo_value}")
        else:
            self.grand_parent.canvas.render("Invalid Selection Made")

    def _OnButtonMonitor0(self, event):
        """Method called when the monitor button 0 is pressed.

        Method changes the state of the monitor to 0 and calls the
        _renderMonitorButtons() method.
        """
        monitor_text = self.monitor_text
        if monitor_text is None:
            pass
        else:
            self.guiint.set_output_state(monitor_text, 0)
            self.renderMonitorButtons()
            self.grand_parent.canvas.render_signals()
        text = f"Monitor {monitor_text} is now off."
        self.grand_parent.canvas.render(text)

    def _OnButtonMonitor1(self, event):
        """Method called when the monitor button 1 is pressed.

        Method changes the state of the monitor to 1 and calls the
        renderMonitorButtons() method."""
        monitor_text = self.monitor_text
        if monitor_text is None:
            pass
        else:
            self.guiint.set_output_state(monitor_text, 1)
            self.renderMonitorButtons()
            self.grand_parent.canvas.render_signals()
        text = f"Monitor {monitor_text} is now on."
        self.grand_parent.canvas.render(text)


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
        self.grand_parent = parent
        self.grand_parent = self.grand_parent.parent
        self.guiint = guiint

        # Creating the sizers
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.middle_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the sizers to the main sizer
        self.main_sizer.Add(self.top_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.middle_sizer, 0, wx.ALL, 5)

        # Add the text on the top
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "Cycles: ")
        self.top_sizer.Add(self.cycles_text, 1, wx.EXPAND | wx.ALL, 10)

        # Create the spin object
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "2", size=wx.Size(120, 10))
        # Can't have 0 cycles, default max seems to be 100!
        self.spin.SetMin(1)
        # Bind the spin object
        self.spin.Bind(wx.EVT_SPINCTRL, self._OnSpin)
        # Add spin to top sizer
        # self.spin.SetMinSize((wx.DefaultCoord, text_min_height))
        self.top_sizer.Add(self.spin, 1, wx.EXPAND | wx.ALL, 5)

        # Create the two buttons
        self.run_button_id, self.continue_button_id = wx.NewIdRef(count=2)
        self.button_run = wx.Button(self, self.run_button_id, "Run")
        self.button_continue = wx.Button(self, self.continue_button_id,
                                         "Continue")
        # Bind buttons
        self.button_run.Bind(wx.EVT_BUTTON, self._OnButtonRun)
        self.button_continue.Bind(wx.EVT_BUTTON, self._OnButtonContinue)
        # Add buttons to bottom sizer
        self.middle_sizer.Add(self.button_run, 1, wx.ALL, 5)
        self.middle_sizer.Add(self.button_continue, 1, wx.ALL, 5)
        # Want to hide this until the run button is pressed!
        self.button_continue.Hide()

        # Set the sizer
        self.SetSizer(self.main_sizer)

    def _OnButtonRun(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        success = self.guiint.run_network(self.spin.GetValue())
        if isinstance(success, str):
            wx.MessageBox(success, "Message", wx.OK | wx.ICON_ERROR)
        self.grand_parent.canvas.render(text)
        self.button_continue.Show()
        self.grand_parent.canvas.render_signals()
        self.main_sizer.Layout()

    def _OnButtonContinue(self, event):
        """Handle the event when the user clicks the continue button."""
        text = "Continue button pressed."
        successs = self.guiint.continue_network(self.spin.GetValue())
        if isinstance(successs, str):
            wx.MessageBox(successs, "Message", wx.OK | wx.ICON_ERROR)
        self.grand_parent.canvas.render(text)
        self.grand_parent.canvas.render_signals()
        self.Layout()

    def _OnSpin(self, event):
        """Handle the event when the user changes the spin value."""
        spin_value = self.spin.GetValue()
        self.grand_parent.canvas.render(f"Spin value: {spin_value}")
        # Can modify the text of the buttons to this
        if change_button_cycles:
            self.button_run.SetLabel(f"Run for: {spin_value}")
            self.button_continue.SetLabel(f"Continue for: {spin_value}")
            self.main_sizer.Layout()
            self.grand_parent.GetSizer().Layout()


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
                 scanner):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # File path for circuit file which can be chosen from the GUI
        self.file_path = None
        guiint = GuiInterface(names, devices, network, monitors, scanner)
        self.guiint = guiint
        # Configure the file menu
        fileMenu = wx.Menu()
        viewMenu = wx.Menu()
        helpMenu = wx.Menu()
        menuBar = wx.MenuBar()
        self.open_id, self.help_id_1, self.help_id_2 = wx.NewIdRef(count=3)
        self.reset_id, self.def_file_show_id = wx.NewIdRef(count=2)
        fileMenu.Append(self.open_id, "&Open")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        viewMenu.Append(self.reset_id, "&Reset")
        viewMenu.Append(self.def_file_show_id, "&Show Definition File")
        helpMenu.Append(self.help_id_1, "&EBNF Syntax")
        helpMenu.Append(self.help_id_2, "&User Guide")
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(viewMenu, "&View")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, guiint)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)

        right_panel = RightPanel(self, guiint)
        main_sizer.Add(right_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        elif Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Ankit Adhi Jessy\n2023",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        elif Id == self.open_id:
            openFileDialog = wx.FileDialog(self, "Open definition file", "",
                                           "",
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

        elif Id == self.help_id_1:
            with open("EBNF.txt", "r") as f:
                # wx.MessageBox(f.read(), "EBNF Syntax")
                box = MyDialog(self, message=f.read(),
                               title="EBNF Syntax", allow_wrap=False)
                box.ShowModal()
                box.Destroy()

        elif Id == self.help_id_2:
            wx.MessageBox("User Guide", "User Guide")
        elif Id == self.reset_id:
            self.canvas.reset_view()
        elif Id == self.def_file_show_id:
            file_path = self.guiint.scanner.path
            with open(file_path, "r") as f:
                box = MyDialog(self, message=f.read(),
                               title="Definition File", editable=False)
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
        super(MyDialog, self).__init__(parent, title=title, size=(500, 500))
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

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 1, wx.EXPAND)

        self.SetSizer(sizer)
