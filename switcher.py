"""
GT Custom Rig Interface - Universal IK/FK Switcher for Maya
Version 1.3.23
Works with MetaHuman, Unreal, mGear, and Custom Rigs
"""

import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


def maya_main_window():
    """Return Maya main window as a Qt object"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class GTCustomRigInterface(QtWidgets.QDialog):
    
    # Rig presets for different rig types
    RIG_PRESETS = {
        'MetaHuman (mGear)': {
            'right_arm': {
                'fk': ['arm_R0_fk0_ctl', 'arm_R0_fk1_ctl', 'arm_R0_fk2_ctl'],
                'ik': ['arm_R0_ik_ctl', 'arm_R0_upv_ctl'],
                'switch': 'arm_R0_settings',
                'switch_attr': 'blend'
            },
            'left_arm': {
                'fk': ['arm_L0_fk0_ctl', 'arm_L0_fk1_ctl', 'arm_L0_fk2_ctl'],
                'ik': ['arm_L0_ik_ctl', 'arm_L0_upv_ctl'],
                'switch': 'arm_L0_settings',
                'switch_attr': 'blend'
            },
            'right_leg': {
                'fk': ['leg_R0_fk0_ctl', 'leg_R0_fk1_ctl', 'leg_R0_fk2_ctl'],
                'ik': ['leg_R0_ik_ctl', 'leg_R0_upv_ctl'],
                'switch': 'leg_R0_settings',
                'switch_attr': 'blend'
            },
            'left_leg': {
                'fk': ['leg_L0_fk0_ctl', 'leg_L0_fk1_ctl', 'leg_L0_fk2_ctl'],
                'ik': ['leg_L0_ik_ctl', 'leg_L0_upv_ctl'],
                'switch': 'leg_L0_settings',
                'switch_attr': 'blend'
            }
        },
        'Unreal Mannequin': {
            'right_arm': {
                'fk': ['upperarm_r', 'lowerarm_r', 'hand_r'],
                'ik': ['ik_hand_r', 'pole_r'],
                'switch': 'ik_hand_r',
                'switch_attr': 'ikBlend'
            },
            'left_arm': {
                'fk': ['upperarm_l', 'lowerarm_l', 'hand_l'],
                'ik': ['ik_hand_l', 'pole_l'],
                'switch': 'ik_hand_l',
                'switch_attr': 'ikBlend'
            },
            'right_leg': {
                'fk': ['thigh_r', 'calf_r', 'foot_r'],
                'ik': ['ik_foot_r', 'pole_r_leg'],
                'switch': 'ik_foot_r',
                'switch_attr': 'ikBlend'
            },
            'left_leg': {
                'fk': ['thigh_l', 'calf_l', 'foot_l'],
                'ik': ['ik_foot_l', 'pole_l_leg'],
                'switch': 'ik_foot_l',
                'switch_attr': 'ikBlend'
            }
        },
        'Custom': {
            'right_arm': {
                'fk': ['shoulder_r_FK_ctrl', 'elbow_r_FK_ctrl', 'wrist_r_FK_ctrl'],
                'ik': ['arm_r_IK_ctrl', 'elbow_r_PV_ctrl'],
                'switch': 'arm_r_switch_ctrl',
                'switch_attr': 'ikFkBlend'
            },
            'left_arm': {
                'fk': ['shoulder_l_FK_ctrl', 'elbow_l_FK_ctrl', 'wrist_l_FK_ctrl'],
                'ik': ['arm_l_IK_ctrl', 'elbow_l_PV_ctrl'],
                'switch': 'arm_l_switch_ctrl',
                'switch_attr': 'ikFkBlend'
            },
            'right_leg': {
                'fk': ['hip_r_FK_ctrl', 'knee_r_FK_ctrl', 'ankle_r_FK_ctrl'],
                'ik': ['leg_r_IK_ctrl', 'knee_r_PV_ctrl'],
                'switch': 'leg_r_switch_ctrl',
                'switch_attr': 'ikFkBlend'
            },
            'left_leg': {
                'fk': ['hip_l_FK_ctrl', 'knee_l_FK_ctrl', 'ankle_l_FK_ctrl'],
                'ik': ['leg_l_IK_ctrl', 'knee_l_PV_ctrl'],
                'switch': 'leg_l_switch_ctrl',
                'switch_attr': 'ikFkBlend'
            }
        }
    }
    
    def __init__(self, parent=maya_main_window()):
        super(GTCustomRigInterface, self).__init__(parent)
        
        self.setWindowTitle("GT Custom Rig Interface (v1.3.23)")
        self.setMinimumWidth(550)
        self.setMinimumHeight(750)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.namespace = ""
        self.bake_mode = 'bake'
        self.limb_buttons = {}
        self.limb_controls = {}
        
        self.create_ui()
        self.create_connections()
        
        # Try auto-detection
        self.auto_detect_rig()
    
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
        
        main_layout.addWidget(self.create_separator())
        
        # Rig Type Selection
        rig_type_layout = QtWidgets.QHBoxLayout()
        rig_type_layout.addWidget(QtWidgets.QLabel("Rig Type:"))
        self.rig_type_combo = QtWidgets.QComboBox()
        self.rig_type_combo.addItems(list(self.RIG_PRESETS.keys()))
        rig_type_layout.addWidget(self.rig_type_combo)
        
        self.detect_rig_btn = QtWidgets.QPushButton("Auto Detect")
        self.detect_rig_btn.setFixedWidth(100)
        rig_type_layout.addWidget(self.detect_rig_btn)
        
        main_layout.addLayout(rig_type_layout)
        
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
        
        # Status label
        self.status_label = QtWidgets.QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Help button
        help_btn = QtWidgets.QPushButton("Help")
        help_btn.setMaximumWidth(100)
        help_btn.clicked.connect(self.show_help)
        help_layout = QtWidgets.QHBoxLayout()
        help_layout.addStretch()
        help_layout.addWidget(help_btn)
        main_layout.addLayout(help_layout)
        
        main_layout.addWidget(self.create_separator())
        
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
        self.create_settings_tab(settings_tab)
        self.tab_widget.addTab(settings_tab, "Settings")
    
    def create_separator(self):
        """Create a horizontal separator line"""
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        return separator
    
    def create_fkik_tab(self, parent):
        """Create the FK/IK switching interface"""
        layout = QtWidgets.QVBoxLayout(parent)
        layout.setSpacing(5)
        
        # Scroll area for limbs
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        # Create limb sections
        scroll_layout.addWidget(self.create_limb_section("Right Arm:", 'right_arm'))
        scroll_layout.addWidget(self.create_limb_section("Left Arm:", 'left_arm'))
        scroll_layout.addWidget(self.create_limb_section("Right Leg:", 'right_leg'))
        scroll_layout.addWidget(self.create_limb_section("Left Leg:", 'left_leg'))
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        layout.addWidget(self.create_separator())
        
        # Options section
        options_group = QtWidgets.QGroupBox("Options")
        options_layout = QtWidgets.QVBoxLayout()
        
        self.autokey_checkbox = QtWidgets.QCheckBox("Auto Key")
        options_layout.addWidget(self.autokey_checkbox)
        
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
    
    def create_settings_tab(self, parent):
        """Create settings tab for custom rig configuration"""
        layout = QtWidgets.QVBoxLayout(parent)
        
        info_label = QtWidgets.QLabel(
            "<b>Custom Rig Configuration</b><br><br>"
            "To configure a custom rig:<br>"
            "1. Select 'Custom' from the Rig Type dropdown<br>"
            "2. Edit the control names in the code to match your rig<br>"
            "3. Specify the switch attribute name<br><br>"
            "Check the Help button for more details."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def create_limb_section(self, label, limb_name):
        """Create a limb section with FK/IK/Switch buttons"""
        group = QtWidgets.QGroupBox(label)
        layout = QtWidgets.QVBoxLayout()
        
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
        
        switch_btn = QtWidgets.QPushButton("Switch")
        switch_btn.setMinimumHeight(40)
        switch_btn.clicked.connect(lambda: self.smart_switch(limb_name))
        layout.addWidget(switch_btn)
        
        self.limb_buttons[limb_name] = {
            'fk': fk_btn,
            'ik': ik_btn,
            'switch': switch_btn
        }
        
        group.setLayout(layout)
        return group
    
    def create_connections(self):
        """Create signal connections"""
        self.get_namespace_btn.clicked.connect(self.get_namespace)
        self.clear_namespace_btn.clicked.connect(self.clear_namespace)
        self.detect_rig_btn.clicked.connect(self.auto_detect_rig)
        self.rig_type_combo.currentTextChanged.connect(self.on_rig_type_changed)
        
        self.bake_radio.toggled.connect(lambda: self.set_mode('bake'))
        self.sparse_radio.toggled.connect(lambda: self.set_mode('sparse'))
        
        self.get_start_btn.clicked.connect(self.get_start_frame)
        self.get_end_btn.clicked.connect(self.get_end_frame)
        self.selection_range_btn.clicked.connect(self.get_selection_range)
        self.timeline_range_btn.clicked.connect(self.get_timeline_range)
        
        self.namespace_field.textChanged.connect(self.on_namespace_changed)
    
    def on_rig_type_changed(self):
        """Called when rig type changes"""
        rig_type = self.rig_type_combo.currentText()
        self.limb_controls = self.RIG_PRESETS[rig_type].copy()
        self.update_all_button_states()
    
    def on_namespace_changed(self):
        """Called when namespace field text changes"""
        self.namespace = self.namespace_field.text()
        self.update_all_button_states()
    
    def auto_detect_rig(self):
        """Auto-detect rig type and namespace"""
        detected = False
        
        # Try each rig preset
        for rig_type, rig_data in self.RIG_PRESETS.items():
            namespaces = self.find_rig_namespaces(rig_data)
            
            if namespaces:
                self.rig_type_combo.setCurrentText(rig_type)
                self.limb_controls = rig_data.copy()
                
                # Use first namespace found
                namespace = namespaces[0]
                self.namespace_field.setText(namespace)
                self.namespace = namespace
                
                self.set_status(f"Detected: {rig_type}" + (f" ({namespace})" if namespace else ""), "green")
                detected = True
                break
        
        if not detected:
            self.set_status("No rig detected - using Custom preset", "orange")
            self.rig_type_combo.setCurrentText("Custom")
            self.limb_controls = self.RIG_PRESETS['Custom'].copy()
        
        self.update_all_button_states()
    
    def find_rig_namespaces(self, rig_data):
        """Search scene for rig controls and extract namespaces"""
        namespaces = set()
        
        for limb_name, limb_info in rig_data.items():
            switch_ctrl = limb_info['switch']
            
            # Search for control with any namespace
            found = cmds.ls(f"*:{switch_ctrl}", type='transform')
            if not found:
                # Also try without namespace
                found = cmds.ls(switch_ctrl, type='transform')
            
            for obj in found:
                if ':' in obj:
                    ns = obj.split(':')[0]
                    namespaces.add(ns)
                else:
                    namespaces.add("")  # No namespace
        
        return list(namespaces)
    
    def set_status(self, message, color="green"):
        """Update status label"""
        self.status_label.setText(f"Status: {message}")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
<h3>GT Custom Rig Interface - Help</h3>

<b>Auto Detection:</b><br>
• Click "Auto Detect" to automatically find your rig type<br>
• Supports MetaHuman (mGear), Unreal Mannequin, and Custom rigs<br>
• Automatically detects namespaces<br><br>

<b>Rig Types:</b><br>
• <b>MetaHuman (mGear):</b> For MetaHumans rigged with mGear<br>
• <b>Unreal Mannequin:</b> For standard Unreal Engine rigs<br>
• <b>Custom:</b> For custom rigs (requires code modification)<br><br>

<b>Namespace:</b><br>
• Auto-detected with "Auto Detect" button<br>
• Or click "Get" to detect from selected object<br>
• Or manually enter in the text field<br><br>

<b>FK/IK Buttons:</b><br>
• <b>Green highlight</b> = Current active mode<br>
• Click FK or IK to switch to that mode<br>
• Click "Switch" to toggle between modes<br><br>

<b>MetaHuman Notes:</b><br>
• Works with mGear-rigged MetaHumans<br>
• For MetaHumans exported from Bridge, add HumanIK rig first<br>
• Make sure to bake the rig before exporting back to Unreal<br><br>

<b>Troubleshooting:</b><br>
• If controls not found, check rig type selection<br>
• Verify namespace is correct<br>
• Check status message for details<br>
• For custom rigs, edit control names in Settings tab
        """
        
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Help")
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setText(help_text)
        msg.exec_()
    
    def set_mode(self, mode):
        """Set the bake mode"""
        self.bake_mode = mode
    
    def get_namespace(self):
        """Get namespace from selected object or scene"""
        sel = cmds.ls(selection=True)
        
        if sel:
            obj = sel[0]
            if ':' in obj:
                namespace = obj.split(':')[0]
                self.namespace_field.setText(namespace)
                self.namespace = namespace
                self.update_all_button_states()
                self.set_status(f"Namespace: {namespace}", "green")
                return
        
        # Try auto-detect
        self.auto_detect_rig()
    
    def clear_namespace(self):
        """Clear the namespace field"""
        self.namespace_field.clear()
        self.namespace = ""
        self.update_all_button_states()
    
    def get_control_name(self, control):
        """Get the full control name with namespace"""
        if self.namespace:
            return f"{self.namespace}:{control}"
        return control
    
    def detect_current_mode(self, limb):
        """Detect if limb is currently in IK or FK mode"""
        if limb not in self.limb_controls:
            return None
            
        limb_data = self.limb_controls[limb]
        switch_ctrl = self.get_control_name(limb_data['switch'])
        
        if not cmds.objExists(switch_ctrl):
            return None
        
        # Try the specified switch attribute
        if 'switch_attr' in limb_data:
            attr = limb_data['switch_attr']
            if cmds.attributeQuery(attr, node=switch_ctrl, exists=True):
                value = cmds.getAttr(f"{switch_ctrl}.{attr}")
                # 0 = FK, 1 = IK for most rigs
                return 'ik' if value > 0.5 else 'fk'
        
        # Fallback: common attributes
        for attr in ['blend', 'ikFkBlend', 'ikBlend', 'ikFk', 'fkIk', 'IK_FK']:
            if cmds.attributeQuery(attr, node=switch_ctrl, exists=True):
                value = cmds.getAttr(f"{switch_ctrl}.{attr}")
                return 'ik' if value > 0.5 else 'fk'
        
        return None
    
    def update_button_state(self, limb_name):
        """Update button highlighting based on current mode"""
        if limb_name not in self.limb_buttons:
            return
        
        current_mode = self.detect_current_mode(limb_name)
        fk_btn = self.limb_buttons[limb_name]['fk']
        ik_btn = self.limb_buttons[limb_name]['ik']
        
        default_style = ""
        active_style = "background-color: #4CAF50; color: white; font-weight: bold;"
        
        if current_mode == 'fk':
            fk_btn.setStyleSheet(active_style)
            ik_btn.setStyleSheet(default_style)
        elif current_mode == 'ik':
            ik_btn.setStyleSheet(active_style)
            fk_btn.setStyleSheet(default_style)
        else:
            fk_btn.setStyleSheet(default_style)
            ik_btn.setStyleSheet(default_style)
    
    def update_all_button_states(self):
        """Update all limb button states"""
        for limb_name in self.limb_buttons.keys():
            self.update_button_state(limb_name)
    
    def switch_to_mode(self, limb, target_mode):
        """Switch limb to specified mode (FK or IK)"""
        current_mode = self.detect_current_mode(limb)
        
        if current_mode is None:
            switch_ctrl = self.get_control_name(self.limb_controls[limb]['switch'])
            QtWidgets.QMessageBox.warning(self, 'Warning', 
                                         f"Could not find switch control for {limb}.\n"
                                         f"Looking for: {switch_ctrl}\n\n"
                                         f"Try using 'Auto Detect' or check your rig type.")
            return
        
        if current_mode == target_mode:
            self.set_status(f"{limb.replace('_', ' ').title()} already in {target_mode.upper()}", "orange")
            return
        
        self.perform_switch(limb, current_mode, target_mode)
    
    def smart_switch(self, limb):
        """Automatically detect current mode and switch to opposite"""
        current_mode = self.detect_current_mode(limb)
        
        if current_mode is None:
            switch_ctrl = self.get_control_name(self.limb_controls[limb]['switch'])
            QtWidgets.QMessageBox.warning(self, 'Warning',
                                         f"Could not find switch control for {limb}.\n"
                                         f"Looking for: {switch_ctrl}\n\n"
                                         f"Try using 'Auto Detect' or check your rig type.")
            return
        
        target_mode = 'fk' if current_mode == 'ik' else 'ik'
        self.perform_switch(limb, current_mode, target_mode)
    
    def perform_switch(self, limb, from_mode, to_mode):
        """Perform the actual IK/FK switch"""
        autokey = self.autokey_checkbox.isChecked()
        start = self.start_frame.value()
        end = self.end_frame.value()
        
        if self.bake_mode == 'bake' and autokey and start < end:
            self.bake_switch(limb, from_mode, to_mode, start, end)
        else:
            self.match_and_switch(limb, from_mode, to_mode)
        
        self.update_button_state(limb)
        self.set_status(f"{limb.replace('_', ' ').title()}: {from_mode.upper()} → {to_mode.upper()}", "green")
    
    def match_and_switch(self, limb, from_mode, to_mode):
        """Match positions and switch on current frame"""
        limb_data = self.limb_controls[limb]
        switch_ctrl = self.get_control_name(limb_data['switch'])
        
        switch_attr = None
        if 'switch_attr' in limb_data:
            attr = limb_data['switch_attr']
            if cmds.attributeQuery(attr, node=switch_ctrl, exists=True):
                switch_attr = attr
        
        if not switch_attr:
            for attr in ['blend', 'ikFkBlend', 'ikBlend', 'ikFk']:
                if cmds.attributeQuery(attr, node=switch_ctrl, exists=True):
                    switch_attr = attr
                    break
        
        if switch_attr:
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
