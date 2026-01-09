"""
GT Custom Rig Interface (v1.3.23) - IK/FK Switch Tool for Maya
"""

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import maya.cmds as cmds
import maya.mel as mel
import re

class GTIKFKSwitchTool(QtWidgets.QDialog):
    """Main IK/FK Switch Tool Window"""
    
    def __init__(self, parent=None):
        super(GTIKFKSwitchTool, self).__init__(parent)
        
        self.setWindowTitle("GT Custom Rig Interface (v1.3.23)")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Store namespace for rig
        self.current_namespace = ""
        
        # Define IK/FK control naming conventions
        self.control_patterns = {
            'right_arm': {
                'fk': ['arm', 'right', 'fk'],
                'ik': ['arm', 'right', 'ik']
            },
            'left_arm': {
                'fk': ['arm', 'left', 'fk'],
                'ik': ['arm', 'left', 'ik']
            },
            'right_leg': {
                'fk': ['leg', 'right', 'fk'],
                'ik': ['leg', 'right', 'ik']
            },
            'left_leg': {
                'fk': ['leg', 'left', 'fk'],
                'ik': ['leg', 'left', 'ik']
            }
        }
        
        self.init_ui()
        self.refresh_namespace()
        
    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # 1. Namespace Section
        namespace_layout = QtWidgets.QHBoxLayout()
        namespace_layout.addWidget(QtWidgets.QLabel("Namespace:"))
        
        self.namespace_combo = QtWidgets.QComboBox()
        self.namespace_combo.setEditable(True)
        self.namespace_combo.setMinimumWidth(150)
        namespace_layout.addWidget(self.namespace_combo)
        
        self.get_clear_btn = QtWidgets.QPushButton("Get Clear")
        self.get_clear_btn.clicked.connect(self.refresh_namespace)
        namespace_layout.addWidget(self.get_clear_btn)
        
        namespace_layout.addStretch()
        main_layout.addLayout(namespace_layout)
        
        # Separator
        main_layout.addWidget(self.create_separator())
        
        # 2. IK/FK Switch Grid
        grid_widget = QtWidgets.QWidget()
        grid_layout = QtWidgets.QGridLayout(grid_widget)
        
        # Headers
        headers = ["FK/IK", "Pose", "Animation", "Settings"]
        for col, header in enumerate(headers):
            header_label = QtWidgets.QLabel(header)
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("font-weight: bold; background-color: #333; color: white; padding: 5px;")
            grid_layout.addWidget(header_label, 0, col)
        
        # Right Arm Section
        row = 1
        grid_layout.addWidget(QtWidgets.QLabel("Right Arm:"), row, 0)
        
        # Right Arm FK/IK Radio Buttons
        right_arm_group = QtWidgets.QButtonGroup(self)
        self.right_arm_fk = QtWidgets.QRadioButton("FK")
        self.right_arm_ik = QtWidgets.QRadioButton("IK")
        right_arm_group.addButton(self.right_arm_fk)
        right_arm_group.addButton(self.right_arm_ik)
        
        radio_layout = QtWidgets.QHBoxLayout()
        radio_layout.addWidget(self.right_arm_fk)
        radio_layout.addWidget(self.right_arm_ik)
        radio_widget = QtWidgets.QWidget()
        radio_widget.setLayout(radio_layout)
        grid_layout.addWidget(radio_widget, row, 1)
        
        # Right Arm Switch Button
        self.right_arm_switch = QtWidgets.QPushButton("Switch")
        self.right_arm_switch.clicked.connect(lambda: self.switch_ik_fk('right_arm'))
        grid_layout.addWidget(self.right_arm_switch, row, 2)
        
        # Right Arm Status Label
        self.right_arm_status = QtWidgets.QLabel("Unknown")
        grid_layout.addWidget(self.right_arm_status, row, 3)
        
        # Left Arm Section
        row = 2
        grid_layout.addWidget(QtWidgets.QLabel("Left Arm:"), row, 0)
        
        # Left Arm FK/IK Radio Buttons
        left_arm_group = QtWidgets.QButtonGroup(self)
        self.left_arm_fk = QtWidgets.QRadioButton("FK")
        self.left_arm_ik = QtWidgets.QRadioButton("IK")
        left_arm_group.addButton(self.left_arm_fk)
        left_arm_group.addButton(self.left_arm_ik)
        
        radio_layout = QtWidgets.QHBoxLayout()
        radio_layout.addWidget(self.left_arm_fk)
        radio_layout.addWidget(self.left_arm_ik)
        radio_widget = QtWidgets.QWidget()
        radio_widget.setLayout(radio_layout)
        grid_layout.addWidget(radio_widget, row, 1)
        
        # Left Arm Switch Button
        self.left_arm_switch = QtWidgets.QPushButton("Switch")
        self.left_arm_switch.clicked.connect(lambda: self.switch_ik_fk('left_arm'))
        grid_layout.addWidget(self.left_arm_switch, row, 2)
        
        # Left Arm Status Label
        self.left_arm_status = QtWidgets.QLabel("Unknown")
        grid_layout.addWidget(self.left_arm_status, row, 3)
        
        # Separator
        row = 3
        grid_layout.addWidget(self.create_separator(), row, 0, 1, 4)
        
        # Right Leg Section
        row = 4
        grid_layout.addWidget(QtWidgets.QLabel("Right Leg:"), row, 0)
        
        # Right Leg FK/IK Radio Buttons
        right_leg_group = QtWidgets.QButtonGroup(self)
        self.right_leg_fk = QtWidgets.QRadioButton("FK")
        self.right_leg_ik = QtWidgets.QRadioButton("IK")
        right_leg_group.addButton(self.right_leg_fk)
        right_leg_group.addButton(self.right_leg_ik)
        
        radio_layout = QtWidgets.QHBoxLayout()
        radio_layout.addWidget(self.right_leg_fk)
        radio_layout.addWidget(self.right_leg_ik)
        radio_widget = QtWidgets.QWidget()
        radio_widget.setLayout(radio_layout)
        grid_layout.addWidget(radio_widget, row, 1)
        
        # Right Leg Switch Button
        self.right_leg_switch = QtWidgets.QPushButton("Switch")
        self.right_leg_switch.clicked.connect(lambda: self.switch_ik_fk('right_leg'))
        grid_layout.addWidget(self.right_leg_switch, row, 2)
        
        # Right Leg Status Label
        self.right_leg_status = QtWidgets.QLabel("Unknown")
        grid_layout.addWidget(self.right_leg_status, row, 3)
        
        # Left Leg Section
        row = 5
        grid_layout.addWidget(QtWidgets.QLabel("Left Leg:"), row, 0)
        
        # Left Leg FK/IK Radio Buttons
        left_leg_group = QtWidgets.QButtonGroup(self)
        self.left_leg_fk = QtWidgets.QRadioButton("FK")
        self.left_leg_ik = QtWidgets.QRadioButton("IK")
        left_leg_group.addButton(self.left_leg_fk)
        left_leg_group.addButton(self.left_leg_ik)
        
        radio_layout = QtWidgets.QHBoxLayout()
        radio_layout.addWidget(self.left_leg_fk)
        radio_layout.addWidget(self.left_leg_ik)
        radio_widget = QtWidgets.QWidget()
        radio_widget.setLayout(radio_layout)
        grid_layout.addWidget(radio_widget, row, 1)
        
        # Left Leg Switch Button
        self.left_leg_switch = QtWidgets.QPushButton("Switch")
        self.left_leg_switch.clicked.connect(lambda: self.switch_ik_fk('left_leg'))
        grid_layout.addWidget(self.left_leg_switch, row, 2)
        
        # Left Leg Status Label
        self.left_leg_status = QtWidgets.QLabel("Unknown")
        grid_layout.addWidget(self.left_leg_status, row, 3)
        
        main_layout.addWidget(grid_widget)
        
        # Separator
        main_layout.addWidget(self.create_separator())
        
        # 3. Options Section
        options_layout = QtWidgets.QHBoxLayout()
        
        # Auto Key Checkbox
        self.auto_key_check = QtWidgets.QCheckBox("Auto Key")
        options_layout.addWidget(self.auto_key_check)
        
        # Bake/Sparse Radio Buttons
        options_layout.addWidget(QtWidgets.QLabel("Bake:"))
        self.bake_radio = QtWidgets.QRadioButton("Bake")
        self.sparse_radio = QtWidgets.QRadioButton("Sparse")
        self.bake_radio.setChecked(True)
        options_layout.addWidget(self.bake_radio)
        options_layout.addWidget(self.sparse_radio)
        
        options_layout.addStretch()
        main_layout.addLayout(options_layout)
        
        # 4. Timeline Range Section
        range_layout = QtWidgets.QHBoxLayout()
        
        range_layout.addWidget(QtWidgets.QLabel("Start:"))
        self.start_field = QtWidgets.QLineEdit("1")
        self.start_field.setMaximumWidth(50)
        range_layout.addWidget(self.start_field)
        
        range_layout.addWidget(QtWidgets.QLabel("End:"))
        self.end_field = QtWidgets.QLineEdit("10")
        self.end_field.setMaximumWidth(50)
        range_layout.addWidget(self.end_field)
        
        # Get End Button
        self.get_end_btn = QtWidgets.QPushButton("Get End")
        self.get_end_btn.clicked.connect(self.get_timeline_end)
        range_layout.addWidget(self.get_end_btn)
        
        # Get Selection Range Button
        self.get_selection_range_btn = QtWidgets.QPushButton("Get Selection Range")
        self.get_selection_range_btn.clicked.connect(self.get_selection_range)
        range_layout.addWidget(self.get_selection_range_btn)
        
        # Get Timeline Range Button
        self.get_timeline_range_btn = QtWidgets.QPushButton("Get Timeline Range")
        self.get_timeline_range_btn.clicked.connect(self.get_timeline_range)
        range_layout.addWidget(self.get_timeline_range_btn)
        
        range_layout.addStretch()
        main_layout.addLayout(range_layout)
        
        # 5. Detect Current State Button
        detect_layout = QtWidgets.QHBoxLayout()
        detect_layout.addStretch()
        
        self.detect_state_btn = QtWidgets.QPushButton("Detect Current IK/FK State")
        self.detect_state_btn.clicked.connect(self.detect_current_state)
        self.detect_state_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        detect_layout.addWidget(self.detect_state_btn)
        
        detect_layout.addStretch()
        main_layout.addLayout(detect_layout)
        
        # 6. Apply All Button
        apply_layout = QtWidgets.QHBoxLayout()
        apply_layout.addStretch()
        
        self.apply_all_btn = QtWidgets.QPushButton("Apply All Switches")
        self.apply_all_btn.clicked.connect(self.apply_all_switches)
        self.apply_all_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        apply_all_btn.setMinimumHeight(40)
        apply_layout.addWidget(self.apply_all_btn)
        
        apply_layout.addStretch()
        main_layout.addLayout(apply_layout)
        
        # Initial detection
        self.detect_current_state()
        
    def create_separator(self):
        """Create a horizontal separator line"""
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: #666;")
        return separator
        
    def refresh_namespace(self):
        """Refresh namespace dropdown with available namespaces"""
        self.namespace_combo.clear()
        
        # Add empty namespace option
        self.namespace_combo.addItem("")
        
        # Get all namespaces
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        
        # Filter out unwanted namespaces
        filtered_namespaces = []
        for ns in namespaces:
            if ns not in ['UI', 'shared']:
                filtered_namespaces.append(ns)
        
        # Add namespaces to dropdown
        for ns in filtered_namespaces:
            self.namespace_combo.addItem(ns)
        
        # Try to detect current namespace from selection
        selection = cmds.ls(selection=True)
        if selection:
            for obj in selection:
                if ':' in obj:
                    ns = obj.split(':')[0]
                    index = self.namespace_combo.findText(ns)
                    if index >= 0:
                        self.namespace_combo.setCurrentIndex(index)
                        break
        
    def get_namespace(self):
        """Get the current namespace from dropdown"""
        ns = self.namespace_combo.currentText()
        if ns:
            return ns + ":"
        return ""
        
    def find_control(self, limb_type, control_type):
        """Find controls for a specific limb and type"""
        namespace = self.get_namespace()
        
        # Get all objects in the namespace
        all_objects = cmds.ls(namespace + "*", transforms=True)
        
        patterns = self.control_patterns[limb_type][control_type]
        
        for obj in all_objects:
            obj_lower = obj.lower()
            # Check if all pattern words are in the object name
            if all(pattern in obj_lower for pattern in patterns):
                # Check if it's a control (usually has _ctrl suffix or similar)
                if 'ctrl' in obj_lower or 'ctl' in obj_lower or 'control' in obj_lower:
                    return obj
        
        # If no control found, look for any object with the patterns
        for obj in all_objects:
            obj_lower = obj.lower()
            if all(pattern in obj_lower for pattern in patterns):
                return obj
                
        return None
        
    def detect_ik_fk_state(self, limb_type):
        """Detect whether the limb is currently in IK or FK mode"""
        namespace = self.get_namespace()
        
        # Try to find IK control
        ik_control = self.find_control(limb_type, 'ik')
        fk_control = self.find_control(limb_type, 'fk')
        
        if ik_control and fk_control:
            # Check visibility or custom attributes
            try:
                # Try to get switch attribute
                switch_attrs = cmds.listAttr(ik_control, userDefined=True) or []
                for attr in switch_attrs:
                    if 'switch' in attr.lower() or 'ikfk' in attr.lower():
                        try:
                            val = cmds.getAttr(ik_control + "." + attr)
                            return "IK" if val > 0.5 else "FK"
                        except:
                            pass
            except:
                pass
            
            # Check visibility as fallback
            try:
                ik_visible = cmds.getAttr(ik_control + ".visibility")
                fk_visible = cmds.getAttr(fk_control + ".visibility")
                
                if ik_visible and not fk_visible:
                    return "IK"
                elif fk_visible and not ik_visible:
                    return "FK"
            except:
                pass
        
        # Try to find blend attributes
        all_objects = cmds.ls(namespace + "*", transforms=True)
        for obj in all_objects:
            try:
                attrs = cmds.listAttr(obj, userDefined=True) or []
                for attr in attrs:
                    attr_lower = attr.lower()
                    if 'blend' in attr_lower and ('ik' in attr_lower or 'fk' in attr_lower):
                        try:
                            val = cmds.getAttr(obj + "." + attr)
                            if 'ik' in attr_lower:
                                return "IK" if val > 0.5 else "FK"
                            else:
                                return "FK" if val > 0.5 else "IK"
                        except:
                            pass
            except:
                continue
        
        return "Unknown"
        
    def detect_current_state(self):
        """Detect current IK/FK state for all limbs"""
        limbs = ['right_arm', 'left_arm', 'right_leg', 'left_leg']
        
        for limb in limbs:
            state = self.detect_ik_fk_state(limb)
            
            # Update UI
            if limb == 'right_arm':
                self.right_arm_status.setText(state)
                self.right_arm_fk.setChecked(state == "FK")
                self.right_arm_ik.setChecked(state == "IK")
            elif limb == 'left_arm':
                self.left_arm_status.setText(state)
                self.left_arm_fk.setChecked(state == "FK")
                self.left_arm_ik.setChecked(state == "IK")
            elif limb == 'right_leg':
                self.right_leg_status.setText(state)
                self.right_leg_fk.setChecked(state == "FK")
                self.right_leg_ik.setChecked(state == "IK")
            elif limb == 'left_leg':
                self.left_leg_status.setText(state)
                self.left_leg_fk.setChecked(state == "FK")
                self.left_leg_ik.setChecked(state == "IK")
        
    def switch_ik_fk(self, limb_type):
        """Switch between IK and FK for a specific limb"""
        target_state = "IK"  # Default to switching to IK
        
        # Determine target state based on radio button
        if limb_type == 'right_arm':
            target_state = "IK" if self.right_arm_fk.isChecked() else "FK"
        elif limb_type == 'left_arm':
            target_state = "IK" if self.left_arm_fk.isChecked() else "FK"
        elif limb_type == 'right_leg':
            target_state = "IK" if self.right_leg_fk.isChecked() else "FK"
        elif limb_type == 'left_leg':
            target_state = "IK" if self.left_leg_fk.isChecked() else "FK"
        
        namespace = self.get_namespace()
        
        # Find IK/FK switch attribute
        all_objects = cmds.ls(namespace + "*", transforms=True)
        switch_attr = None
        switch_node = None
        
        for obj in all_objects:
            try:
                attrs = cmds.listAttr(obj, userDefined=True) or []
                for attr in attrs:
                    attr_lower = attr.lower()
                    if 'switch' in attr_lower or 'ikfk' in attr_lower:
                        # Check if this attribute controls the right limb
                        obj_lower = obj.lower()
                        limb_patterns = self.control_patterns[limb_type]['ik'] + self.control_patterns[limb_type]['fk']
                        
                        if any(pattern in obj_lower for pattern in limb_patterns):
                            switch_attr = attr
                            switch_node = obj
                            break
            except:
                continue
            
            if switch_attr:
                break
        
        if switch_node and switch_attr:
            # Set the switch attribute
            value = 1.0 if target_state == "IK" else 0.0
            
            # Check if auto-key is enabled
            if self.auto_key_check.isChecked():
                current_time = cmds.currentTime(query=True)
                cmds.setKeyframe(switch_node, attribute=switch_attr, time=current_time, value=value)
            else:
                cmds.setAttr(switch_node + "." + switch_attr, value)
            
            # Update status
            self.update_limb_status(limb_type, target_state)
            
            cmds.inViewMessage(
                amg=f'Switched {limb_type.replace("_", " ").title()} to {target_state}',
                pos='midCenter',
                fade=True
            )
        else:
            # Fallback: toggle visibility of IK/FK controls
            ik_control = self.find_control(limb_type, 'ik')
            fk_control = self.find_control(limb_type, 'fk')
            
            if ik_control and fk_control:
                ik_value = 1.0 if target_state == "IK" else 0.0
                fk_value = 1.0 if target_state == "FK" else 0.0
                
                if self.auto_key_check.isChecked():
                    current_time = cmds.currentTime(query=True)
                    cmds.setKeyframe(ik_control, attribute="visibility", time=current_time, value=ik_value)
                    cmds.setKeyframe(fk_control, attribute="visibility", time=current_time, value=fk_value)
                else:
                    cmds.setAttr(ik_control + ".visibility", ik_value)
                    cmds.setAttr(fk_control + ".visibility", fk_value)
                
                self.update_limb_status(limb_type, target_state)
                
                cmds.inViewMessage(
                    amg=f'Switched {limb_type.replace("_", " ").title()} to {target_state}',
                    pos='midCenter',
                    fade=True
                )
            else:
                cmds.warning(f"Could not find IK/FK controls for {limb_type}")
    
    def update_limb_status(self, limb_type, state):
        """Update the status label for a limb"""
        if limb_type == 'right_arm':
            self.right_arm_status.setText(state)
            self.right_arm_fk.setChecked(state == "FK")
            self.right_arm_ik.setChecked(state == "IK")
        elif limb_type == 'left_arm':
            self.left_arm_status.setText(state)
            self.left_arm_fk.setChecked(state == "FK")
            self.left_arm_ik.setChecked(state == "IK")
        elif limb_type == 'right_leg':
            self.right_leg_status.setText(state)
            self.right_leg_fk.setChecked(state == "FK")
            self.right_leg_ik.setChecked(state == "IK")
        elif limb_type == 'left_leg':
            self.left_leg_status.setText(state)
            self.left_leg_fk.setChecked(state == "FK")
            self.left_leg_ik.setChecked(state == "IK")
    
    def apply_all_switches(self):
        """Apply IK/FK switches for all limbs"""
        limbs = ['right_arm', 'left_arm', 'right_leg', 'left_leg']
        
        for limb in limbs:
            self.switch_ik_fk(limb)
        
        cmds.inViewMessage(
            amg='Applied all IK/FK switches',
            pos='midCenter',
            fade=True
        )
    
    def get_timeline_end(self):
        """Get the end frame from timeline and update the end field"""
        playback_end = cmds.playbackOptions(query=True, max=True)
        self.end_field.setText(str(int(playback_end)))
    
    def get_selection_range(self):
        """Get range from selected keys in graph editor"""
        try:
            # Try to get range from graph editor
            mel.eval('$tmp = timeControl -q -rangeArray $gPlayBackSlider')
            range_array = mel.eval('$tmp = $gPlayBackSlider')
            
            if range_array and len(range_array) >= 2:
                self.start_field.setText(str(int(range_array[0])))
                self.end_field.setText(str(int(range_array[1])))
            else:
                # Fallback to timeline range
                self.get_timeline_range()
        except:
            self.get_timeline_range()
    
    def get_timeline_range(self):
        """Get the full timeline range"""
        playback_start = cmds.playbackOptions(query=True, min=True)
        playback_end = cmds.playbackOptions(query=True, max=True)
        
        self.start_field.setText(str(int(playback_start)))
        self.end_field.setText(str(int(playback_end)))
    
    def bake_animation(self):
        """Bake animation based on selected options"""
        if not self.bake_radio.isChecked() and not self.sparse_radio.isChecked():
            cmds.warning("Please select Bake or Sparse mode")
            return
        
        try:
            start_frame = int(self.start_field.text())
            end_frame = int(self.end_field.text())
        except ValueError:
            cmds.warning("Invalid frame range")
            return
        
        # Get selected objects or all controls
        selection = cmds.ls(selection=True, transforms=True)
        
        if not selection:
            # Get all likely controls in namespace
            namespace = self.get_namespace()
            selection = cmds.ls(namespace + "*_ctrl", namespace + "*_ctl", namespace + "*control*", transforms=True)
        
        if not selection:
            cmds.warning("No objects selected for baking")
            return
        
        # Set bake options
        sparse_mode = self.sparse_radio.isChecked()
        
        cmds.bakeResults(
            selection,
            simulation=True,
            time=(start_frame, end_frame),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseCurveBake=sparse_mode,
            removeBakedAttributeFromLayer=False,
            removeBakedAnimFromLayer=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=True,
            controlPoints=False,
            shape=True
        )
        
        cmds.inViewMessage(
            amg=f'Baked animation from frame {start_frame} to {end_frame}',
            pos='midCenter',
            fade=True
        )

# Function to show the tool
def show_ikfk_switch_tool():
    """Show the IK/FK Switch Tool window"""
    try:
        # Close existing window
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.objectName() == "GTIKFKSwitchTool":
                widget.close()
    except:
        pass
    
    # Create and show new window
    dialog = GTIKFKSwitchTool()
    dialog.setObjectName("GTIKFKSwitchTool")
    dialog.show()
    
    return dialog

# Run the tool
if __name__ == "__main__":
    show_ikfk_switch_tool()
