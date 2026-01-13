import maya.cmds as cmds

# Search for common IK/FK control patterns
print("\n" + "="*50)
print("SEARCHING FOR RIG CONTROLS")
print("="*50)

# Common patterns to search for
patterns = [
    "*_ik_*", "*_IK_*", "*_ik*", "*IK*",
    "*_fk*", "*_FK*", 
    "*_ctrl", "*_control", "*_CTRL",
    "*_settings", "*_switch*",
    "*blend*", "*ikfk*"
]

print("\n=== Searching for controls ===\n")

for pattern in patterns:
    found = cmds.ls(pattern, type='transform')
    if found:
        print(f"\n--- Pattern: {pattern} ---")
        for obj in found[:10]:  # Show first 10 matches
            print(f"  {obj}")
            
            # Check for IK/FK attributes
            attrs = cmds.listAttr(obj, userDefined=True, keyable=True) or []
            relevant_attrs = [a for a in attrs if any(x in a.lower() for x in ['ik', 'fk', 'blend'])]
            if relevant_attrs:
                print(f"    Attributes: {relevant_attrs}")


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
    show()</parameter>
