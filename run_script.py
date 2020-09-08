import sys
from discord import create_channels, delete_channels, generate_matterbridge_config

# Ensure script name was given
if len(sys.argv) == 1:
    print('Invalid script name')
    sys.exit(1)

script = sys.argv[1]
if script == 'create_channels':
    create_channels.run()
elif script == 'delete_channels':
    delete_channels.run()
elif script == 'generate_matterbridge_config':
    generate_matterbridge_config.run()
else:
    print('Unknown script name.')
