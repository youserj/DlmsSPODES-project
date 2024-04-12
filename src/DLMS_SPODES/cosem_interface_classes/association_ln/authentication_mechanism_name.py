from functools import lru_cache
from ...types import common_data_types as cdt
from . import mechanism_id


class AuthenticationMechanismName(cdt.Structure):
    """ Contains the name of the authentication mechanism for the association (see IEC 62056-53). The authentication mechanism name is specified as an
    OBJECT IDENTIFIER in 7.3.7.2 of IEC 62056-53. The authentication_mechanism_name attribute includes the arc labels of the OBJECT IDENTIFIER. """
    DEFAULT = (2, 16, 756, 5, 8, 2, 0)
    joint_iso_ctt_element: cdt.Unsigned
    country_element: cdt.Unsigned
    country_name_element: cdt.LongUnsigned
    identified_organization_element: cdt.Unsigned
    DLMS_UA_element: cdt.Unsigned
    authentication_mechanism_name_element: cdt.Unsigned
    mechanism_id_element: mechanism_id.MechanismIdElement

    @classmethod
    @lru_cache(maxsize=32)
    def get_AARQ_mechanism_name(cls, cryptographic: int, algorithm_id: int) -> bytes:
        """according to DLMS UA 1000-2 Ed. 10 9.4.2.2.4 Cryptographic algorithm ID-s"""
        default = list(AuthenticationMechanismName.DEFAULT)
        default[5] = cryptographic
        default[6] = algorithm_id
        return AuthenticationMechanismName(tuple(default)).get_a_xdr()
