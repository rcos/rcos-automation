from rcosautomation.discord.constants import RCOS_SERVER_ID, VIEW_CHANNELS, CATEGORY, VOICE_CHANNEL, DISCORD_PM_ROLE_ID, MANAGE_MESSAGES, TEXT_CHANNEL
from rcosautomation.discord.channels import add_channel_if_not_exists
from rcosautomation.discord.roles import add_role_if_not_exists
from typing import List, Dict, Optional
from csv import DictReader
import requests
import re


def run():
    students = dict()
    small_groups = dict()

    with open('students.csv', 'r') as file:
        csv_reader = DictReader(file)
        for row in csv_reader:
            students[row['rcs_id']] = row

            if row['small_group'] not in small_groups:
                small_groups[row['small_group']] = set()

            small_groups[row['small_group']].add(row['project'])

    for small_group in small_groups:
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
            project_role = add_role_if_not_exists(project, hoist=True)
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
            project_text_channel = add_channel_if_not_exists(
                project, channel_type=TEXT_CHANNEL, topic=f'🗨️ Discussion channel for {project}', parent_id=small_group_category['id'], perms=project_perms)
            project_voice_channel = add_channel_if_not_exists(
                project, channel_type=VOICE_CHANNEL, parent_id=small_group_category['id'], perms=project_perms)
