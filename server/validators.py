from re import match

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cidr_notation(ip_net: str) -> str:
    """
    Ensure that the given IP net is a valid CIDR notation.
    """
    if match(
        r'^((?:25[0-5]|2[0-4]?[0-9]?|[13-9][0-9]?[0-9]?|0)\.){3}(?:25[0-5]|2[0-4]?[0-9]?|[13-9][0-9]?[0-9]?|0)/(3[0-2]?|[1-2]?\d|\d)$',
        ip_net,
    ):
        net_id, suffix = tuple(ip_net.split('/'))
        suffix = int(suffix)
        if suffix < 24:
            raise ValidationError(_("The subnet mask should not be lower than 24."))
        if suffix > 29:
            raise ValidationError(_("The subnet mask should not be greater than 29."))
        remaining_bits = 32 - suffix
        last_byte = net_id.split('.')[3]
        if int(last_byte) != (expected_last_byte := 256 - 2**remaining_bits):
            expected_ip_net = (
                f'{net_id.rsplit(last_byte, 1)[0]}{expected_last_byte}/{suffix}'
            )
            raise ValidationError(
                _("The CIDR notation should be %(ip_net)s.")
                % {'ip_net': expected_ip_net}
            )
        return ip_net
    raise ValidationError(_("The given IP Net is not a valid CIDR notation."))
