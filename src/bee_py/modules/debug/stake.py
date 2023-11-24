from typing import Optional, Union

from bee_py.types.type import BeeRequestOptions, NumberString, RedistributionState, TransactionOptions
from bee_py.utils.http import http
from bee_py.utils.logging import logger

STAKE_ENDPOINT = "stake"
REDISTRIBUTION_ENDPOINT = "redistributionstate"


def get_stake(request_options: BeeRequestOptions) -> NumberString:
    """
    Retrieves the staked amount from the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        str: The staked amount as a string.
    """

    config = {
        "url": STAKE_ENDPOINT,
        "method": "get",
    }
    response = http(request_options, config)

    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    return response.json()["stakedAmount"]


def stake(
    request_options: BeeRequestOptions,
    amount: str,
    options: Optional[Union[dict, TransactionOptions]] = None,
):
    """
    Stakes a specified amount of tokens on the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.
        amount (str): The amount of tokens to stake.
        options (TransactionOptions, optional): Optional transaction options. Defaults to None.
    """

    headers = {}
    if isinstance(options, dict):
        if options and "gasPrice" in options:
            headers["gas-price"] = str(options["gasPrice"])

        if options and "gasLimit" in options:
            headers["gas-limit"] = str(options["gasLimit"])
    else:
        if options and options.gas_price:
            headers["gas-price"] = options.gas_price

        if options and options.gas_limit:
            headers["gas-limit"] = options.gas_limit

    config = {
        "url": f"{STAKE_ENDPOINT}/{amount}",
        "method": "post",
        "headers": headers,
    }

    http(request_options, config)


def get_redistribution_state(request_options: BeeRequestOptions) -> RedistributionState:
    """
    Retrieves the current redistribution state from the Bee node.

    Args:
        request_options (BeeRequestOptions): Ky Options for making requests.

    Returns:
        RedistributionState: The current redistribution state.
    """
    config = {
        "url": REDISTRIBUTION_ENDPOINT,
        "method": "get",
    }

    response = http(request_options, config)
    if response.status_code != 200:  # noqa: PLR2004
        logger.info(response.json())
        logger.error(response.raise_for_status())

    redistribution_state = response.json()

    return RedistributionState.parse_obj(redistribution_state)
