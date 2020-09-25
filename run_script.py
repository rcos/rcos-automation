from rcosautomation.discord.scripts import create_channels2, delete_channels, matterbridge, pairing, member_roles
import sys
from dotenv import load_dotenv
load_dotenv()

# Ensure script name was given
if len(sys.argv) == 1:
    print('Invalid script name')
    sys.exit(1)

script = sys.argv[1]
if script == 'create_channels':
    create_channels2.run()
elif script == 'delete_channels':
    delete_channels.run()
elif script == 'matterbridge':
    matterbridge.run()
elif script == 'pairing':
    pairing.run()
elif script == 'member_roles':
    member_roles.run()
else:
    print('Unknown script name.')
