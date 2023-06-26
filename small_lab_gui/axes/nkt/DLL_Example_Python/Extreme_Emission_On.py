from NKTP_DLL import *

openResult = openPorts('COM4', 0, 0)
print('Opening the comport:', PortResultTypes(openResult))

rdResult, FWVersionStr = registerReadAscii('COM4', 18, 0x65, -1)
print('Reading firmware version str:', FWVersionStr, RegisterResultTypes(rdResult))

result = registerWriteU8('COM4', 15, 0x30, 3, -1)
print('Setting emission ON - Extreme:', RegisterResultTypes(result))

result = registerWriteU8('COM4', 16, 0x30, 1, -1)
print('Setting rf', RegisterResultTypes(result))

result = registerWriteU32('COM4', 16, 0x90, int(632*1000), -1)
print('Setting select wavelength 1', RegisterResultTypes(result))

closeResult = closePorts('COM4')
print('Close the comport:', PortResultTypes(closeResult))

