from tomlkit import parse, dumps, document, table, comment, aot

# Constants
REMOTE_NICKNAME_FORMAT = '**{NICK}**: '

doc = document()

# General settings
doc['general'] = table()
doc['general']['IgnoreFailureOnStart'] = False

# DISCORD
print('Let\'s setup Discord...')
doc['discord'] = table()
doc['discord'].comment('Discord server connection settings')
doc['discord']['rcos'] = table()

doc['discord']['rcos']['Token'] = input('Bot Token: ')
doc['discord']['rcos']['Token'].comment(
    'SECRET bot token found on https://discord.com/developers')

doc['discord']['rcos']['Server'] = input('Server: ')
doc['discord']['rcos']['Server'].comment(
    'The ID of the Discord server. Can be found in URL when on Discord or if Developer Mode is turned on and right-clicking the server icon.')

doc['discord']['rcos']['RemoteNickFormat'] = REMOTE_NICKNAME_FORMAT
doc['discord']['rcos']['RemoteNickFormat'].comment(
    'The prefix to apply to messages.')

# MATTERMOST
print('Now Mattermost...')
doc['mattermost'] = table()
doc['mattermost'].comment('Mattermost server connection settings')
doc['mattermost']['rcos'] = table()

doc['mattermost']['rcos']['Server'] = 'chat.rcos.io:443'
doc['mattermost']['rcos']['Server'].comment(
    'URL of the Mattermost server with no http:// or https:// prepended')

doc['mattermost']['rcos']['Team'] = 'rcos'
doc['mattermost']['rcos']['Team'].comment(
    'The "team", found as the first part of URL when on Mattermost server')

doc['mattermost']['rcos']['RemoteNickFormat'] = REMOTE_NICKNAME_FORMAT
doc['mattermost']['rcos']['RemoteNickFormat'].comment(
    'The prefix to apply to messages.')

doc['mattermost']['rcos']['Login'] = input('Mattermost username: ')
doc['mattermost']['rcos']['Login'].comment('The prefix to apply to messages.')

doc['mattermost']['rcos']['Password'] = input('Mattermost password: ')
doc['mattermost']['rcos']['Password'].comment('The password of the Mattermost user to use.')

# The channels to pair
# (Discord channel, Mattermost channel)
channel_pairs = [
    ('testing', 'testing'),
    ('testing-2', 'testing-2')
]

gateways = aot()

for index, pair in enumerate(channel_pairs):
    gateway = table()
    gateway['name'] = f'gateway-{index}'
    gateway['enable'] = True
    
    gateway['inout'] = aot()
    gateway_discord = table()
    gateway_discord['account'] = 'discord.rcos'
    gateway_discord['channel'] = pair[0]
    gateway['inout'].append(gateway_discord)

    gateway_mattermost = table()
    gateway_mattermost['account'] = 'mattermost.rcos'
    gateway_mattermost['channel'] = pair[1]
    gateway['inout'].append(gateway_mattermost)

    gateways.append(gateway)


doc.add('gateway', gateways)

with open('matterbridge.toml', 'w') as outfile:
    outfile.write(dumps(doc))
