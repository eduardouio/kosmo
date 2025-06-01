from .PartnerCreateUpdate import (
    PartnerCreateView,
    PartnerUpdateView,
    PartnerUpdateParent,
)
from .Bank import (
    BankDetailView,
    BankListView,
    BankCreateView,
    BankUpdateView,
    BankDeleteView,
)
from .Contact import (
    ContactDetailView,
    ContactListView,
    ContactCreateView,
    ContactUpdateView,
    ContactDeleteView,
)
from .DAEPartners import (
    DAECreateView,
    DAEUpdateView,
    DAEDeleteView,
    DAEListView,
    DAEDetailView,
)
from .PartnerDelete import PartnerDeleteView
from .PartnerDetail import PartnerDetailView
from .PartnerList import PartnerListView
from .PartnerAutoRegister import PartnerAutoRegister
from .PartnerAutoRegisterList import PartnerAutoRegisterList

__all__ = [
    'PartnerCreateView',
    'PartnerUpdateView',
    'PartnerUpdateParent',
    'BankDetailView',
    'BankListView',
    'BankCreateView',
    'BankUpdateView',
    'BankDeleteView',
    'ContactDetailView',
    'ContactListView',
    'ContactCreateView',
    'ContactUpdateView',
    'ContactDeleteView',
    'DAECreateView',
    'DAEUpdateView',
    'DAEDeleteView',
    'DAEListView',
    'DAEDetailView',
    'PartnerDeleteView',
    'PartnerDetailView',
    'PartnerListView',
    'PartnerAutoRegister',
    'PartnerAutoRegisterList',
]
