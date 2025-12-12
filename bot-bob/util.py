from dotenv import dotenv_values

import constants

class Util:
    @staticmethod
    def is_admin(user_id: int):
        admins = [int(admin_id) for admin_id in dotenv_values(constants.CONFIG_FILE)[constants.ADMINS_KEY].split('\n')]
        return user_id in admins