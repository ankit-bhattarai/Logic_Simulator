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

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
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
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, guiint):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
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

    def render_signal(self, x_start, y_start, values, name, colour=(0.0, 0.0, 1.0),
                      width=20, height=25):
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


class RightPanel(wx.Panel):
    def __init__(self, parent, guiint):
        super().__init__(parent=parent)  # Initialise
        self.parent = parent
        self.guiint = guiint

        # Creating the sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        middle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        switch_main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        monitor_main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(top_sizer, 0, wx.ALL, 5)
        main_sizer.Add(middle_sizer, 0, wx.ALL, 5)
        main_sizer.Add(switch_main_sizer, 0, wx.ALL, 10)
        main_sizer.Add(monitor_main_sizer, 0, wx.ALL, 10)

        # Creating and Adding the smaller sizers to switch sizer
        switch_select_sizer = wx.BoxSizer(wx.VERTICAL)
        switch_state_sizer = wx.BoxSizer(wx.VERTICAL)
        switch_main_sizer.Add(switch_select_sizer, 0, wx.ALL, 5)
        switch_main_sizer.Add(switch_state_sizer, 0, wx.ALL, 5)

        # Creating and Adding the smaller sizers to monitor sizer
        monitor_select_sizer = wx.BoxSizer(wx.VERTICAL)
        monitor_state_sizer = wx.BoxSizer(wx.VERTICAL)
        monitor_main_sizer.Add(monitor_select_sizer, 0, wx.ALL, 5)
        monitor_main_sizer.Add(monitor_state_sizer, 0, wx.ALL, 5)

        # Add the text on the top
        self.cycles_text = wx.StaticText(self, wx.ID_ANY, "Cycles: ")
        top_sizer.Add(self.cycles_text, 1, wx.EXPAND | wx.ALL, 10)

        # Create the spin object
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10", size=wx.Size(120, 10))
        # Can't have 0 cycles, default max seems to be 100!
        self.spin.SetMin(1)
        # Bind the spin object
        self.spin.Bind(wx.EVT_SPINCTRL, self.OnSpin)
        # Add spin to top sizer
        # self.spin.SetMinSize((wx.DefaultCoord, text_min_height))
        top_sizer.Add(self.spin, 1, wx.EXPAND | wx.ALL, 5)

        # Create the two buttons
        self.run_button_id, self.continue_button_id = wx.NewIdRef(count=2)
        self.button_run = wx.Button(self, self.run_button_id, "Run")
        self.button_continue = wx.Button(self, self.continue_button_id,
                                         "Continue")
        # Bind buttons
        self.button_run.Bind(wx.EVT_BUTTON, self.OnButtonRun)
        self.button_continue.Bind(wx.EVT_BUTTON, self.OnButtonContinue)
        # Add buttons to bottom sizer
        middle_sizer.Add(self.button_run, 1, wx.ALL, 5)
        middle_sizer.Add(self.button_continue, 1, wx.ALL, 5)
        # Want to hide this until the run button is pressed!
        self.button_continue.Hide()

        # Text for the switches
        self.switch_text = wx.StaticText(
            self, wx.ID_ANY, "Select Switch and state: ")
        switch_select_sizer.Add(self.switch_text, 1, wx.EXPAND | wx.ALL, 10)

        # Have to create the combo box for the switches
        combo_id_switch = wx.NewIdRef()
        self.combo_box_switch = wx.ComboBox(self, combo_id_switch,
                                            choices=list(
                                                self.guiint.list_of_switches()),
                                            style=wx.TE_PROCESS_ENTER)
        # Bind the combo box
        self.combo_box_switch.Bind(wx.EVT_COMBOBOX, self.OnComboSwitch)
        # Want it to work for both enter and selection
        self.combo_box_switch.Bind(wx.EVT_TEXT_ENTER, self.OnComboSwitch)
        # Add combo box to switch sizer
        switch_select_sizer.Add(self.combo_box_switch, 1, wx.ALL, 5)
        self.switch_text = None  # The option chosen on the combo box

        # For representing the state of the switch, will have two buttons
        # The button corresponding to the current state of the switch
        # will be green and the other one will be red

        # Create the two buttons
        self.switch_button_id_0, self.switch_button_id_1 = wx.NewIdRef(count=2)
        self.button_switch_0 = wx.Button(
            self, self.switch_button_id_0, "Closed")
        self.button_switch_1 = wx.Button(
            self, self.switch_button_id_1, "Open")

        # Bind buttons
        self.button_switch_0.Bind(wx.EVT_BUTTON, self.OnButtonSwitch0)
        self.button_switch_1.Bind(wx.EVT_BUTTON, self.OnButtonSwitch1)

        # Add buttons to switch state sizer
        switch_state_sizer.Add(self.button_switch_0, 1, wx.ALL, 5)
        switch_state_sizer.Add(self.button_switch_1, 1, wx.ALL, 5)
        # Initially hide the buttons
        self.button_switch_0.Hide()
        self.button_switch_1.Hide()

        # Specify the colors for the buttons
        self.red = wx.Colour(226, 126, 126, 255)
        self.green = wx.Colour(0, 255, 0, 255)

        # Text for the monitors
        self.monitor_text = wx.StaticText(
            self, wx.ID_ANY, "Select Monitor: ")
        monitor_select_sizer.Add(self.monitor_text, 1, wx.EXPAND | wx.ALL, 10)

        # Have to create the combo box for the monitors
        combo_id_monitor = wx.NewIdRef()
        self.combo_box_monitor = wx.ComboBox(self, combo_id_monitor,
                                             choices=list(
                                                 self.guiint.list_of_outputs()),
                                             style=wx.TE_PROCESS_ENTER)
        # Bind the combo box
        self.combo_box_monitor.Bind(wx.EVT_COMBOBOX, self.OnComboMonitor)
        # Want it to work for both enter and selection
        self.combo_box_monitor.Bind(wx.EVT_TEXT_ENTER, self.OnComboMonitor)

        # Add combo box to monitor sizer
        monitor_select_sizer.Add(self.combo_box_monitor, 1, wx.ALL, 5)
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
        self.button_monitor_0.Bind(wx.EVT_BUTTON, self.OnButtonMonitor0)
        self.button_monitor_1.Bind(wx.EVT_BUTTON, self.OnButtonMonitor1)

        # Add buttons to monitor state sizer
        monitor_state_sizer.Add(self.button_monitor_0, 1, wx.ALL, 5)
        monitor_state_sizer.Add(self.button_monitor_1, 1, wx.ALL, 5)
        # Initially hide the buttons
        self.button_monitor_0.Hide()
        self.button_monitor_1.Hide()

        # Set the sizer for the panel
        self.SetSizer(main_sizer)

    def OnButtonRun(self, event):
        """Handle the event when the user clicks the run button."""
        text = "Run button pressed."
        self.guiint.run_network(self.spin.GetValue())
        self.parent.canvas.render(text)
        self.button_continue.Show()
        self.parent.canvas.render_signals()
        self.Layout()

    def OnButtonContinue(self, event):
        """Handle the event when the user clicks the continue button."""
        text = "Continue button pressed."
        self.parent.canvas.render(text)
        self.guiint.continue_network(self.spin.GetValue())
        self.parent.canvas.render_signals()

    def OnSpin(self, event):
        spin_value = self.spin.GetValue()
        self.parent.canvas.render(f"Spin value: {spin_value}")
        # Can modify the text of the buttons to this
        if change_button_cycles:
            self.button_run.SetLabel(f"Run for: {spin_value}")
            self.button_continue.SetLabel(f"Continue for: {spin_value}")
            self.GetSizer().Layout()
            self.parent.GetSizer().Layout()

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
        self.GetSizer().Layout()
        self.parent.GetSizer().Layout()

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
        self.GetSizer().Layout()
        self.parent.GetSizer().Layout()

    def OnComboSwitch(self, event):
        combo_value = self.combo_box_switch.GetValue()
        if combo_value in self.guiint.list_of_switches():
            self.switch_text = combo_value  # Only change this if valid
            self.renderSwitchBoxes()
            print("Combo box changed. New_value:", combo_value)
            self.parent.canvas.render(
                f"Combo box changed. New_value: {combo_value}")

        else:
            self.parent.canvas.render("Invalid Selection Made")

    def OnComboMonitor(self, event):
        combo_value = self.combo_box_monitor.GetValue()
        if combo_value in self.guiint.list_of_outputs():
            self.monitor_text = combo_value  # Only change this if valid
            self.renderMonitorButtons()
            print("Combo box changed. New_value:", combo_value)
            self.parent.canvas.render(
                f"Combo box changed. New_value: {combo_value}")
        else:
            self.parent.canvas.render("Invalid Selection Made")

    def OnButtonSwitch0(self, event):
        switch_text = self.switch_text
        if switch_text is None:
            pass  # This can't ever happen
        else:
            self.guiint.set_switch_state(switch_text, 0)
            self.renderSwitchBoxes()
        text = f"Switch {switch_text} is now open."
        self.parent.canvas.render(text)

    def OnButtonSwitch1(self, event):
        switch_text = self.switch_text
        if switch_text is None:
            pass  # This can't ever happen
        else:
            self.guiint.set_switch_state(switch_text, 1)
            self.renderSwitchBoxes()
        text = f"Switch {switch_text} is now closed."

        self.parent.canvas.render(text)

    def OnButtonMonitor0(self, event):
        monitor_text = self.monitor_text
        if monitor_text is None:
            pass
        else:
            self.guiint.set_output_state(monitor_text, 0)
            self.renderMonitorButtons()
            self.parent.canvas.render_signals()
        text = f"Monitor {monitor_text} is now off."
        self.parent.canvas.render(text)

    def OnButtonMonitor1(self, event):
        monitor_text = self.monitor_text
        if monitor_text is None:
            pass
        else:
            self.guiint.set_output_state(monitor_text, 1)
            self.renderMonitorButtons()
            self.parent.canvas.render_signals()
        text = f"Monitor {monitor_text} is now on."
        self.parent.canvas.render(text)


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

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # File path for circuit file which can be chosen from the GUI
        self.file_path = None
        guiint = GuiInterface(names, devices, network, monitors)
        # Configure the file menu
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()
        menuBar = wx.MenuBar()
        self.open_id, self.help_id_1, self.help_id_2 = wx.NewIdRef(count=3)
        fileMenu.Append(self.open_id, "&Open")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        helpMenu.Append(self.help_id_1, "&EBNF Syntax")
        helpMenu.Append(self.help_id_2, "&User Guide")
        menuBar.Append(fileMenu, "&File")
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
            print("Path: ", self.file_path)

        elif Id == self.help_id_1:
            print("Help: EBNF Syntax required")
        elif Id == self.help_id_2:
            print("Help: User guide required")
