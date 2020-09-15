import sys
from discord import create_channels, delete_channels, matterbridge, pairing

# Ensure script name was given
if len(sys.argv) == 1:
    print('Invalid script name')
    sys.exit(1)

script = sys.argv[1]
if script == 'create_channels':
    create_channels.run()
elif script == 'delete_channels':
    delete_channels.run()
elif script == 'matterbridge':
    matterbridge.run()
elif script == 'pairing':
    pairing.run()
else:
    print('Unknown script name.')
