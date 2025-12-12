from dotenv import dotenv_values
from discord import Interaction

import constants


def format_error(error):
    return f"{error.__class__.__name__}: {error}"

def is_admin(interaction: Interaction):
    admins = [int(admin_id) for admin_id in dotenv_values(constants.CONFIG_FILE)[constants.ADMINS_KEY].split('\n')]
    return interaction.user.id in admins

def get_bobs():
    bob_strings = [bob for bob in dotenv_values(constants.CONFIG_FILE)[constants.BOB_KEY].split('\n')]
    return {
        int(bob[0]): bob[1] for bob in (bob.split(':') for bob in bob_strings)
    }

def check_if_not_bob(interaction: Interaction):
    return interaction.user.id not in get_bobs()