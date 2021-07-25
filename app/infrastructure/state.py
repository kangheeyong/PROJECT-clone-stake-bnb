from typing import Optional

import services.data_service as svc
from models.owners import Owner


active_account: Optional[Owner] = None


def reload_account():
    global active_account
    if not active_account:
        return

    active_account = svc.find_account_by_email(active_account.email)
