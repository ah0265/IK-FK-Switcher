"""
GT Custom Rig Interface - IK/FK Switcher for Maya (PySide2)
Version 1.3.23
"""

import maya.cmds as cmds
import maya.mel as mel
from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui


def maya_main_window():
    """Return Maya main window as a Qt object"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class GTCustomRigInterface(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(GTCustomRigInterface, self).__init__(parent)
        
        self.setWindowTitle("GT Custom Rig Interface (v1.3.23)")
        self.setMinimumWidth(500)
        self.setMinimumHeight(650)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.namespace = ""
        self.bake_mode = 'bake'
        
        # Default control naming conventions
        self.limb_controls = {
            'right_arm': {
                'fk': ['shoulder_r_FK', 'elbow_r_FK', 'wrist_r_FK'],
                'ik': ['arm_r_IK', 'elbow_r_PV'],
                'switch': 'arm_r_switch'
            },
            'left_arm': {
                'fk': ['shoulder_l_FK', 'elbow_l_FK', 'wrist_l_FK'],
                'ik': ['arm_l_IK', 'elbow_l_PV'],
                'switch': 'arm_l_switch'
            },
            'right_leg': {
                'fk': ['hip_r_FK', 'knee_r_FK', 'ankle_r_FK'],
                'ik': ['leg_r_IK', 'knee_r_PV'],
                'switch': 'leg_r_switch'
            },
            'left_leg': {
                'fk': ['hip_l_FK', 'knee_l_FK', 'ankle_l_FK'],
                'ik': ['leg_l_IK', 'knee_l_PV'],
                'switch': 'leg_l_switch'
            }
        }
        
        self.create_ui()
        self.create_connections()
    
    def create_ui(self):
        """Create the main UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_label = QtWidgets.QLabel("GT Custom Rig Interface")
        header_font = QtGui.QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Separator
        separator1 = QtWidgets.QFrame()
        separator1.setFrameShape(QtWidgets.QFrame.HLine)
        separator1.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(separator1)
        
        # Namespace section
        namespace_label = QtWidgets.QLabel("Namespace:")
        namespace_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(namespace_label)
        
        namespace_layout = QtWidgets.QHBoxLayout()
        self.namespace_field = QtWidgets.QLineEdit()
        self.namespace_field.setPlaceholderText("Namespace: (Optional)")
        namespace_layout.addWidget(self.namespace_field)
        
        self.get_namespace_btn = QtWidgets.QPushButton("Get")
        self.get_namespace_btn.setFixedWidth(80)
        namespace_layout.addWidget(self.get_namespace_btn)
        
        self.clear_namespace_btn = QtWidgets.QPushButton("Clear")
        self.clear_namespace_btn.setFixedWidth(80)
        namespace_layout.addWidget(self.clear_namespace_btn)
        
        main_layout.addLayout(namespace_layout)
        
        # Separator
        separator2 = QtWidgets.QFrame()
        separator2.setFrameShape(QtWidgets.QFrame.HLine)
        separator2.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(separator2)
        
        # Tab Widget
        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # FK/IK Tab
        fkik_tab = QtWidgets.QWidget()
        self.create_fkik_tab(fkik_tab)
        self.tab_widget.addTab(fkik_tab, "FK/IK")
        
        # Pose Tab
        pose_tab = QtWidgets.QWidget()
        pose_layout = QtWidgets.QVBoxLayout(pose_tab)
        pose_layout.addWidget(QtWidgets.QLabel("Pose Controls Coming Soon..."))
        self.tab_widget.addTab(pose_tab, "Pose")
        
        # Animation Tab
        anim_tab = QtWidgets.QWidget()
        anim_layout = QtWidgets.QVBoxLayout(anim_tab)
        anim_layout.addWidget(QtWidgets.QLabel("Animation Controls Coming Soon..."))
        self.tab_widget.addTab(anim_tab, "Animation")
        
        # Settings Tab
        settings_tab = QtWidgets.QWidget()
        settings_layout = QtWidgets.QVBoxLayout(settings_tab)
        settings_layout.addWidget(QtWidgets.QLabel("Settings Coming Soon..."))
        self.tab_widget.addTab(settings_tab, "Settings")
    
    def create_fkik_tab(self, parent):
        """Create the FK/IK switching interface"""
        layout = QtWidgets.QVBoxLayout(parent)
        layout.setSpacing(10)
        
        # Right Arm
        layout.addWidget(self.create_limb_section("Right Arm:", 'right_arm'))
        
        # Left Arm
        layout.addWidget(self.create_limb_section("Left Arm:", 'left_arm'))
        
        # Right Leg
        layout.addWidget(self.create_limb_section("Right Leg:", 'right_leg'))
        
        # Left Leg
        layout.addWidget(self.create_limb_section("Left Leg:", 'left_leg'))
        
        # Separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(separator)
        
        # Options section
        options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout()
        
        # Auto Key checkbox
        self.autokey_checkbox = QtWidgets.QCheckBox("Auto Key")
        options_layout.addWidget(self.autokey_checkbox)
        
        # Bake/Sparse radio buttons
        radio_layout = QtWidgets.QHBoxLayout()
        self.bake_radio = QtWidgets.QRadioButton("Bake")
        self.bake_radio.setChecked(True)
        self.sparse_radio = QtWidgets.QRadioButton("Sparse")
        radio_layout.addWidget(self.bake_radio)
        radio_layout.addWidget(self.sparse_radio)
        radio_layout.addStretch()
        options_layout.addLayout(radio_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Frame range section
        range_group = QtWidgets.QGroupBox("Frame Range")
        range_layout = QtWidgets.QVBoxLayout()
        
        # Start and End frame
        frame_layout = QtWidgets.QHBoxLayout()
        frame_layout.addWidget(QtWidgets.QLabel("Start:"))
        self.start_frame = QtWidgets.QSpinBox()
        self.start_frame.setRange(-10000, 10000)
        self.start_frame.setValue(1)
        self.start_frame.setFixedWidth(80)
        frame_layout.addWidget(self.start_frame)
        
        self.get_start_btn = QtWidgets.QPushButton("Get")
        self.get_start_btn.setFixedWidth(60)
        frame_layout.addWidget(self.get_start_btn)
        
        frame_layout.addWidget(QtWidgets.QLabel("End:"))
        self.end_frame = QtWidgets.QSpinBox()
        self.end_frame.setRange(-10000, 10000)
        self.end_frame.setValue(10)
        self.end_frame.setFixedWidth(80)
        frame_layout.addWidget(self.end_frame)
        
        self.get_end_btn = QtWidgets.QPushButton("Get")
        self.get_end_btn.setFixedWidth(60)
        frame_layout.addWidget(self.get_end_btn)
        
        frame_layout.addStretch()
        range_layout.addLayout(frame_layout)
        
        # Range buttons
        range_btn_layout = QtWidgets.QHBoxLayout()
        self.selection_range_btn = QtWidgets.QPushButton("Get Selection Range")
        self.selection_range_btn.setMinimumHeight(35)
        range_btn_layout.addWidget(self.selection_range_btn)
        
        self.timeline_range_btn = QtWidgets.QPushButton("Get Timeline Range")
        self.timeline_range_btn.setMinimumHeight(35)
        range_btn_layout.addWidget(self.timeline_range_btn)
        
        range_layout.addLayout(range_btn_layout)
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)
        
        layout.addStretch()
    
    def create_limb_section(self, label, limb_name):
        """Create a limb section with FK/IK/Switch buttons"""
        group = QtWidgets.QGroupBox(label)
        layout = QtWidgets.QVBoxLayout()
        
        # FK and IK buttons
        button_layout = QtWidgets.QHBoxLayout()
        fk_btn = QtWidgets.QPushButton("FK")
        fk_btn.setMinimumHeight(40)
        fk_btn.clicked.connect(lambda: self.switch_to_mode(limb_name, 'fk'))
        button_layout.addWidget(fk_btn)
        
        ik_btn = QtWidgets.QPushButton("IK")
        ik_btn.setMinimumHeight(40)
        ik_btn.clicked.connect(lambda: self.switch_to_mode(limb_name, 'ik'))
        button_layout.addWidget(ik_btn)
        
        layout.addLayout(button_layout)
        
        # Switch button
        switch_btn = QtWidgets.QPushButton("Switch")
        switch_btn.setMinimumHeight(40)
        switch_btn.clicked.connect(lambda: self.smart_switch(limb_name))
        layout.addWidget(switch_btn)
        
        group.setLayout(layout)
        return group
    
    def create_connections(self):
        """Create signal connections"""
        self.get_namespace_btn.clicked.connect(self.get_namespace)
        self.clear_namespace_btn.clicked.connect(self.clear_namespace)
        
        self.bake_radio.toggled.connect(lambda: self.set_mode('bake'))
        self.sparse_radio.toggled.connect(lambda: self.set_mode('sparse'))
        
        self.get_start_btn.clicked.connect(self.get_start_frame)
        self.get_end_btn.clicked.connect(self.get_end_frame)
        self.selection_range_btn.clicked.connect(self.get_selection_range)
        self.timeline_range_btn.clicked.connect(self.get_timeline_range)
    
    def set_mode(self, mode):
        """Set the bake mode"""
        self.bake_mode = mode
    
    def get_namespace(self):
        """Get namespace from selected object"""
        sel = cmds.ls(selection=True)
        if sel:
            obj = sel[0]
            if ':' in obj:
                namespace = obj.split(':')[0]
                self.namespace_field.setText(namespace)
                self.namespace = namespace
                QtWidgets.QMessageBox.information(self, 'Success', f'Namespace set to: {namespace}')
            else:
                QtWidgets.QMessageBox.information(self, 'Info', 'Selected object has no namespace')
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'Please select an object with a namespace')
    
    def clear_namespace(self):
        """Clear the namespace field"""
        self.namespace_field.clear()
        self.namespace = ""
    
    def get_control_name(self, control):
        """Get the full control name with namespace"""
        if self.namespace:
            return f"{self.namespace}:{control}"
        return control
    
    def detect_current_mode(self, limb):
        """Detect if limb is currently in IK or FK mode"""
        switch_ctrl = self.get_control_name(self.limb_controls[limb]['switch'])
        
        if not cmds.objExists(switch_ctrl):
            QtWidgets.QMessageBox.warning(self, 'Warning', f"Switch control not found: {switch_ctrl}")
            return None
        
        # Check for common switch attributes
        for attr in ['ikFk', 'fkIk', 'IK_FK', 'FK_IK', 'ikBlend', 'fkikBlend']:
            if cmds.attributeQuery(attr, node=switch_ctrl, exists=True):
                value = cmds.getAttr(f"{switch_ctrl}.{attr}")
                # Typically 0 = FK, 1 = IK (but this can vary)
                return 'ik' if value > 0.5 else 'fk'
        
        QtWidgets.QMessageBox.warning(self, 'Warning', 
                                     f"Could not find IK/FK switch attribute on {switch_ctrl}")
        return None
    
    def switch_to_mode(self, limb, target_mode):
        """Switch limb to specified mode (FK or IK)"""
        current_mode = self.detect_current_mode(limb)
        
        if current_mode is None:
            return
        
        if current_mode == target_mode:
            QtWidgets.QMessageBox.information(self, 'Info', 
                                             f"{limb} is already in {target_mode.upper()} mode")
            return
        
        # Perform the switch
        self.perform_switch(limb, current_mode, target_mode)
    
    def smart_switch(self, limb):
        """Automatically detect current mode and switch to opposite"""
        current_mode = self.detect_current_mode(limb)
        
        if current_mode is None:
            return
        
        target_mode = 'fk' if current_mode == 'ik' else 'ik'
        self.perform_switch(limb, current_mode, target_mode)
    
    def perform_switch(self, limb, from_mode, to_mode):
        """Perform the actual IK/FK switch with matching"""
        switch_ctrl = self.get_control_name(self.limb_controls[limb]['switch'])
        autokey = self.autokey_checkbox.isChecked()
        
        # Get frame range for baking
        start = self.start_frame.value()
        end = self.end_frame.value()
        
        if self.bake_mode == 'bake' and autokey:
            # Bake the switch over frame range
            self.bake_switch(limb, from_mode, to_mode, start, end)
        else:
            # Single frame switch
            self.match_and_switch(limb, from_mode, to_mode)
        
        QtWidgets.QMessageBox.information(self, 'Success',
                                         f'{limb.replace("_", " ").title()} switched from {from_mode.upper()} to {to_mode.upper()}')
    
    def match_and_switch(self, limb, from_mode, to_mode):
        """Match positions and switch on current frame"""
        switch_ctrl = self.get_control_name(self.limb_controls[limb]['switch'])
        
        # Find the switch attribute
        switch_attr = None
        for attr in ['ikFk', 'fkIk', 'IK_FK', 'FK_IK', 'ikBlend']:
            if cmds.attributeQuery(attr, node=switch_ctrl, exists=True):
                switch_attr = attr
                break
        
        if switch_attr:
            # Set the switch value (0 for FK, 1 for IK typically)
            target_value = 1 if to_mode == 'ik' else 0
            cmds.setAttr(f"{switch_ctrl}.{switch_attr}", target_value)
            
            if self.autokey_checkbox.isChecked():
                cmds.setKeyframe(switch_ctrl, attribute=switch_attr)
    
    def bake_switch(self, limb, from_mode, to_mode, start, end):
        """Bake the IK/FK switch over a frame range"""
        current_time = cmds.currentTime(query=True)
        
        for frame in range(start, end + 1):
            cmds.currentTime(frame)
            self.match_and_switch(limb, from_mode, to_mode)
        
        cmds.currentTime(current_time)
    
    def get_start_frame(self):
        """Set start frame to current time"""
        current = int(cmds.currentTime(query=True))
        self.start_frame.setValue(current)
    
    def get_end_frame(self):
        """Set end frame to current time"""
        current = int(cmds.currentTime(query=True))
        self.end_frame.setValue(current)
    
    def get_selection_range(self):
        """Get frame range from timeline selection"""
        aTimeSlider = mel.eval('$tmpVar=$gPlayBackSlider')
        if cmds.timeControl(aTimeSlider, query=True, rangeVisible=True):
            frame_range = cmds.timeControl(aTimeSlider, query=True, rangeArray=True)
            self.start_frame.setValue(int(frame_range[0]))
            self.end_frame.setValue(int(frame_range[1] - 1))
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'No timeline range selected')
    
    def get_timeline_range(self):
        """Get full timeline range"""
        start = int(cmds.playbackOptions(query=True, minTime=True))
        end = int(cmds.playbackOptions(query=True, maxTime=True))
        self.start_frame.setValue(start)
        self.end_frame.setValue(end)


def show():
    """Show the GT Custom Rig Interface"""
    global gt_rig_interface
    
    try:
        gt_rig_interface.close()
        gt_rig_interface.deleteLater()
    except:
        pass
    
    gt_rig_interface = GTCustomRigInterface()
    gt_rig_interface.show()


# Run the tool
if __name__ == "__main__":
    show()
