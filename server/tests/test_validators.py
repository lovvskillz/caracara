from django.core.exceptions import ValidationError
from pytest import mark, raises

from server.validators import validate_cidr_notation


@mark.parametrize(
    "ip_net",
    [
        "123.123.123.248/29",
        "123.123.123.0/24",
        "192.168.0.0/24",
        "255.255.255.0/24",
        "1.1.1.0/24",
        "89.45.19.0/24",
    ],
)
def test__cidr_validator__valid_notation(ip_net: str):
    """
    Ensure that valid CIDR notations don't raise an exception.
    """
    assert validate_cidr_notation(ip_net) == ip_net


@mark.parametrize(
    "ip_net", ["123.123.123.0/33", "256.255.255.0/24", "not valid", "123.123.l23.0/24"]
)
def test__cidr_validator__invalid_notation(ip_net: str):
    """
    Ensure that invalid CIDR notations raise an exception.
    """
    with raises(ValidationError) as excinfo:
        validate_cidr_notation(ip_net)

    assert (
        str(excinfo.value.message) == "The given IP Net is not a valid CIDR notation."
    )


@mark.parametrize(
    "ip_net, error_message",
    [
        ("123.123.224.0/23", "The subnet mask should not be lower than 24."),
        ("123.123.123.252/30", "The subnet mask should not be greater than 29."),
    ],
)
def test__cidr_validator__out_of_reasonable_subnet_mask_range(
    ip_net: str, error_message: str
):
    """
    Ensure that the subnet mask is not too low or too high.
    """
    with raises(ValidationError) as excinfo:
        validate_cidr_notation(ip_net)

    assert str(excinfo.value.message) == error_message


@mark.parametrize(
    "ip_net, expected_ip_net",
    [
        ("123.123.224.1/24", "123.123.224.0/24"),
        ("123.123.224.130/25", "123.123.224.128/25"),
        ("123.123.123.68/28", "123.123.123.64/28"),
        ("123.123.123.252/29", "123.123.123.248/29"),
    ],
)
def test__cidr_validator__invalid_network_prefix(ip_net: str, expected_ip_net: str):
    """
    Ensure that the network prefix must be valid.
    """
    with raises(ValidationError) as excinfo:
        validate_cidr_notation(ip_net)

    assert (
        str(excinfo.value.message) == f"The CIDR notation should be {expected_ip_net}."
    )
