from re import match

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cidr_notation(ip_net: str) -> str:
    """
    Ensure that the given IP net is a valid CIDR notation.
    """
    if match(
        r"^((?:25[0-5]|2[0-4]?[0-9]?|[13-9][0-9]?[0-9]?|0)\.){3}(?:25[0-5]|2[0-4]?[0-9]?|[13-9][0-9]?[0-9]?|0)/(3[0-2]?|[1-2]?\d|\d)$",
        ip_net,
    ):
        network_prefix, suffix = tuple(ip_net.split("/"))
        suffix = int(suffix)
        if suffix < 24:
            raise ValidationError(_("The subnet mask should not be lower than 24."))
        if suffix > 29:
            raise ValidationError(_("The subnet mask should not be greater than 29."))
        remaining_bits = 32 - suffix
        last_byte = int(network_prefix.split(".")[3])
        if last_byte % (ip_net_range := 2**remaining_bits) != 0:
            expected_last_byte = int(last_byte / ip_net_range) * ip_net_range
            expected_ip_net = f"{network_prefix.rsplit(str(last_byte), 1)[0]}{expected_last_byte}/{suffix}"
            raise ValidationError(
                _("The CIDR notation should be %(ip_net)s.")
                % {"ip_net": expected_ip_net}
            )
        return ip_net
    raise ValidationError(_("The given IP Net is not a valid CIDR notation."))
