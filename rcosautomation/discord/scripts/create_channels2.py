from rcosautomation.discord.constants import RCOS_SERVER_ID, VIEW_CHANNELS, CATEGORY, VOICE_CHANNEL, DISCORD_PM_ROLE_ID, MANAGE_MESSAGES, TEXT_CHANNEL
from rcosautomation.discord.channels import add_channel_if_not_exists, edit_channel, find_channel
from rcosautomation.discord.roles import add_role_if_not_exists
from typing import List, Dict, Optional
from csv import DictReader
import requests
import re


def run():
    projects = []
    small_groups = dict()

    with open('projects.csv', 'r') as file:
        csv_reader = DictReader(file)
        for project in csv_reader:
            small_group = int(project['Small Group #'])
            if small_group not in small_groups:
                small_groups[small_group] = []

            small_groups[small_group].append(project)

    for small_group in sorted(small_groups.keys()):
        title = f'Small Group {small_group}'
        # Create role
        small_group_role = add_role_if_not_exists(title)

        # Create @everyone permission overwrites
        perms = [
            {
                'id': RCOS_SERVER_ID,
                'type': 'role',
                'deny': VIEW_CHANNELS
            },
            {
                'id': small_group_role['id'],
                'type': 'role',
                'allow': VIEW_CHANNELS
            }
        ]

        # Create category for small group to hold general and project channels
        small_group_category = add_channel_if_not_exists(
            title, CATEGORY, perms=perms)

        # Create this small group's general channels
        small_group_text_channel = add_channel_if_not_exists(
            title, parent_id=small_group_category['id'])
        small_group_voice_channel = add_channel_if_not_exists(
            title, channel_type=VOICE_CHANNEL, parent_id=small_group_category['id'])

        # Create this small group's project channels and roles
        for project in small_groups[small_group]:
            project_role = add_role_if_not_exists(
                project['Project Name'], hoist=True)
            project_perms = [
                {
                    'id': RCOS_SERVER_ID,
                    'type': 'role',
                    'deny': VIEW_CHANNELS
                },
                {
                    'id': project_role['id'],
                    'type': 'role',
                    'allow': VIEW_CHANNELS
                },
                {
                    'id': DISCORD_PM_ROLE_ID,
                    'type': 'role',
                    'allow': MANAGE_MESSAGES
                }
            ]

            print(
                f'Looking for text channel for project {project["Project Name"]}')
            project_text_channel = find_channel(
                project['Project Name'], channel_type=TEXT_CHANNEL, ignore_parent=True)
            if project_text_channel == None:
                print('Not found! Creating now...')
                project_text_channel = add_channel_if_not_exists(
                    project['Project Name'], channel_type=TEXT_CHANNEL, topic=f'🗨️ Discussion channel for {project["Project Name"]}', parent_id=small_group_category['id'], perms=project_perms)
            else:
                print('Found! Moving to small group category and applying perms')
                # Move channel to category
                edit_channel(project_text_channel['id'], {
                             'parent_id': small_group_category['id'], 'position': 2, 'topic': f'🗨️ Discussion channel for {project["Project Name"]} led by {project["Project Lead (RCS ID)"]}', 'permission_overwrites': project_perms})

            print(
                f'Looking for voice channel for project {project["Project Name"]}')
            project_voice_channel = find_channel(
                project['Project Name'], channel_type=VOICE_CHANNEL, ignore_parent=True)
            if project_voice_channel == None:
                print('NOT FOUND! Creating now...')
                project_voice_channel = add_channel_if_not_exists(
                    project['Project Name'], channel_type=VOICE_CHANNEL, parent_id=small_group_category['id'], perms=project_perms)
            else:
                print('Found! Moving to small group category and applying perms')
                # Move channel to category
                edit_channel(project_voice_channel['id'], {
                             'parent_id': small_group_category['id'], 'permission_overwrites': project_perms})

            input('Press ENTER to continue...')

            # project_voice_channel = add_channel_if_not_exists(
            #     project['Project Name'], channel_type=VOICE_CHANNEL, parent_id=small_group_category['id'], perms=project_perms)
