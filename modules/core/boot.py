"""Boot File to enable Serial comms via the USB"""
import usb_cdc
usb_cdc.enable(data=True)