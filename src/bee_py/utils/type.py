from typing import IO, Any, Union

from ens.utils import is_valid_ens_name
from swarm_cid import ReferenceType, decode_cid, encode_reference

from bee_py.types.type import (
    BATCH_ID_HEX_LENGTH,
    ENCRYPTED_REFERENCE_HEX_LENGTH,
    PSS_TARGET_HEX_LENGTH_MAX,
    PUBKEY_HEX_LENGTH,
    REFERENCE_HEX_LENGTH,
    AllTagsOptions,
    BeeRequestOptions,
    FeedType,
    FileUploadOptions,
    ReferenceOrENS,
    Tag,
    UploadOptions,
    UploadResult,
    UploadResultWithCid,
)
from bee_py.utils.error import BeeArgumentError, BeeError
from bee_py.utils.hex import assert_hex_string, is_hex_string, is_prefixed_hex_string


def assert_non_negative_integer(value: Union[int, str], name: str = "Value"):
    """
    Assert that the provided value is a non-negative integer.

    Args:
        value (Union[int, str]): The value to check.
        name (str, optional): The name of the value. Defaults to 'Value'.

    Raises:
        ValueError: If the value is not a non-negative integer.
    """
    if not isinstance(value, (int, str)):
        msg = f"{name} must be a number or a string representing a number"
        raise ValueError(msg)
    value = int(value) if isinstance(value, str) else value
    if value < 0:
        msg = f"{name} has to be bigger or equal to zero"
        raise ValueError(msg)


def make_tag_uid(tag_uid: Union[int, str, None]) -> int:
    """
    Utility function that returns Tag UID

    Args:
        tag_uid (Union[int, str, None]): The tag UID to check.

    Returns:
        int: The tag UID as an integer.

    Raises:
        TypeError: If the tag UID is not a non-negative integer.
    """
    if not tag_uid:
        msg = "TagUid was expected but got None instead!"
        raise TypeError(msg)

    if isinstance(tag_uid, Tag):
        return tag_uid.uid
    elif isinstance(tag_uid, int):
        assert_non_negative_integer(tag_uid, "UID")
        return tag_uid
    elif isinstance(tag_uid, str):
        try:
            int_value = int(tag_uid)
            if int_value < 0:
                msg = f"TagUid was expected to be positive non-negative integer! Got {int_value}"
                raise TypeError(msg)
            return int_value
        except ValueError as e:
            msg = "Passed tagUid string is not valid integer!"
            raise TypeError(msg) from e
    msg = "tagUid has to be either Tag or a number (UID)!"
    raise TypeError(msg)


def assert_reference(value: Any) -> None:
    try:
        assert_hex_string(value, REFERENCE_HEX_LENGTH)
    except TypeError:
        assert_hex_string(value, ENCRYPTED_REFERENCE_HEX_LENGTH)


def assert_reference_or_ens(value: Any) -> None:
    if not isinstance(value, str):
        msg = "ReferenceOrEns has to be a string!"
        raise TypeError(msg)

    if is_hex_string(value):
        assert_reference(value)

    if not is_valid_ens_name(value):
        msg = "ReferenceOrEns is not valid Reference, but also not valid ENS domain."
        raise TypeError(msg)


def make_reference_or_ens(value: Any, expected_cid_type: ReferenceType) -> ReferenceOrENS:
    """
    Converts a Swarm CID or ENS name to a hex-encoded Swarm Reference.

    Args:
    value (str): The Swarm CID or ENS name.
    expected_cid_type (str): The expected type of the Swarm CID.

    Returns:
    str: The hex-encoded Swarm Reference.
    """
    if not isinstance(value, str):
        msg = "ReferenceCidOrEns has to be a string!"
        raise TypeError(msg)

    try:
        result = decode_cid(value)

        if result.type != expected_cid_type:
            msg = f'CID was expected to be of type {expected_cid_type}, but got instead {result.type if result.type else "non-Swarm CID"}'  # noqa: E501
            raise BeeError(msg)

        return result.reference
    except BeeError as e:
        raise e

    assert_reference_or_ens(value)

    return value


def add_cid_conversion_function(result: UploadResult, cid_type: str) -> UploadResultWithCid:
    """
    Adds a getter method to the result object that converts the reference to a CID base32 encoded string.

    Args:
        result (UploadResult): The object to add the getter method to.
        cid_type (str): The type of the CID.

    Returns:
        UploadResultWithCid
    """

    def cid():
        return encode_reference(str(result.reference), cid_type)

    return UploadResultWithCid(cid=cid, reference=result.reference, tagUid=result.tag_uid)


def assert_request_options(options: Any, name: str = "RequestOptions") -> None:
    """
    Checks that a value is a valid BeeRequestOptions object.

    Args:
       options (Any): The value to check.
       name (str): The name of the object, for error messages.

    Raises:
       TypeError: If the value is not an object.
       ValueError: If the `retry` or `timeout` options are not non-negative integers.
    """
    if options is None:
        return

    if not isinstance(options, BeeRequestOptions):
        if not isinstance(options, dict):
            msg = f"Options must be an instance of BeeRequestOptions or dictionary. Got: {type(options)}"
            raise TypeError(msg)

    if isinstance(options, dict):
        options = BeeRequestOptions.model_validate(options)

    if options.retry:
        if (
            not isinstance(
                options.retry,
                int,
            )
            or options.retry < 0
        ):
            msg = f"{name}.retry has to be a non-negative integer!"
            raise BeeArgumentError(msg, options.retry)

    if options.timeout:
        if not isinstance(options.timeout, int) or options.timeout < 0:
            msg = f"{name}.timeout has to be a non-negative integer!"
            raise BeeArgumentError(msg, options.timeout)


def assert_upload_options(value: Any, name: str = "UploadOptions") -> None:
    """
    Asserts that a value is a valid BeeRequestOptions object.

    Args:
        value (Any): The value to check.
        name (str): The name of the object, for error messages.

    Raises:
        TypeError: If the value is not an object.
        ValueError: If the `retry` or `timeout` options are not non-negative integers.
    """
    assert_request_options(value, name)

    if not isinstance(value, UploadOptions):
        value = UploadOptions.model_validate(value)

    options = value

    if options.pin and not isinstance(options.pin, bool):
        msg = f"options.pin property in {name} has to be boolean or None!"
        raise TypeError(msg)

    if options.encrypt and not isinstance(options.encrypt, bool):
        msg = f"options.encrypt property in {name} has to be boolean or None!"
        raise TypeError(msg)

    if options.tag:
        if not isinstance(options.tag, int):
            msg = f"options.tag property in {name} has to be number or None!"
            raise TypeError(msg)
        if options.tag <= 0:
            msg = f"options.tag property in {name} has to be non-negative"
            raise BeeArgumentError(msg, options.tag)


def assert_file_upload_options(value: Any, name: str = "FileUploadOptions") -> None:
    """
    Asserts that a value is a valid FileUploadOptions object.

    Args:
        value (Any): The value to check.
        name (str): The name of the object, for error messages.

    Raises:
        TypeError: If the value is not an object.
        ValueError: If the `size` or `contentType` options are not of the correct type.
    """

    assert_upload_options(value, name)
    if isinstance(value, dict):
        if value.get("size", None) and isinstance(value.get("size"), int):
            msg = "size property in FileUploadOptions has to be number or None!"
            raise TypeError(msg)

    if not isinstance(value, FileUploadOptions):
        value = FileUploadOptions.model_validate(value)

    options = value

    if options.size:
        if not isinstance(options.size, int):
            msg = "size property in FileUploadOptions has to be number or None!"
            raise TypeError(msg)
        elif options.size < 0:
            msg = "size property in FileUploadOptions has to be a non-negative integer"
            raise ValueError(msg)

    if options.content_type and not isinstance(options.content_type, str):
        msg = "contentType property in FileUploadOptions has to be string or None!"
        raise TypeError(msg)


def assert_collection_upload_options(value: Any, name: str = "CollectionUploadOptions") -> None:
    """
    Asserts that a value is a valid CollectionUploadOptions object.

    Args:
        value (Any): The value to check.
        name (str): The name of the object, for error messages.

    Raises:
        TypeError: If the value is not an object.
        ValueError: If the `indexDocument` or `errorDocument` options are not of the correct type.
    """

    assert_upload_options(value, name)

    options = value

    if options.index_document:
        if not isinstance(options.index_document, str):
            msg = "indexDocument property in CollectionUploadOptions has to be string or None!"
            raise TypeError(msg)

    if options.error_document:
        if not isinstance(options.error_document, str):
            msg = "errorDocument property in CollectionUploadOptions has to be string or None!"
            raise TypeError(msg)


def is_tag(value: Any) -> bool:
    """
    Checks whether the given value is a valid Tag object.

    Args:
        value (Any): The value to check.

    Returns:
        bool: True if the value is a valid Tag object, False otherwise.
    """
    return isinstance(value, Tag)


def assert_address_prefix(value: str, name: str = "AddressPrefix") -> None:
    """
    Asserts that a value is a valid Bee address prefix.

    Args:
        value (str): The value to check.
        name (str): The name of the argument, for error messages.

    Raises:
        TypeError: If the value is not a string.
        ValueError: If the value is not a valid hex string or if it exceeds the maximum length.
    """

    assert_hex_string(value)

    if len(value) > PSS_TARGET_HEX_LENGTH_MAX:
        msg = f"{name} must have a maximum length of {PSS_TARGET_HEX_LENGTH_MAX}. Got string with length {len(value)}"
        raise ValueError(msg)


def assert_postage_batch_options(value: Any, name: str = "PostageBatchOptions") -> None:
    """
    Asserts that a value is a valid PostageBatchOptions object.

    Args:
        value (Any): The value to check.
        name (str): The name of the object, for error messages.

    Raises:
        TypeError: If the value is not an object.
        ValueError: If the `gasPrice`, `immutableFlag`, `waitForUsable`, or `waitForUsableTimeout` options
        are not of the correct type or have invalid values.
    """

    if value is None:
        return

    options = value

    assert_request_options(options, name)

    if options.gas_price:
        if not isinstance(options.gas_price, int) or options.gas_price < 0:
            msg = "gasPrice must be a non-negative integer"
            raise ValueError(msg)

    if options.immutable_flag:
        if not isinstance(options.immutable_flag, bool):
            msg = "immutableFlag must be a boolean"
            raise ValueError(msg)

    if options.wait_for_usable:
        if not isinstance(options.wait_for_usable, bool):
            msg = "waitForUsable must be a boolean"
            raise ValueError(msg)

    if options.wait_for_usable_timeout:
        if not isinstance(options.wait_for_usable_timeout, int) or options.wait_for_usable_timeout < 0:
            msg = "waitForUsableTimeout must be a non-negative integer"
            raise ValueError(msg)


def assert_transaction_options(value: Any, name: str = "TransactionOptions"):
    """
    Validates that a value is a valid TransactionOptions object.

    Args:
        value (Any): The value to check.
        name (str): The name of the object, for error messages.

    Raises:
        ValueError: If the `gasLimit` or `gasPrice` options are not non-negative integers.
    """
    if value is None:
        return

    options = value
    assert_request_options(options, "TransactionOptions")

    if options.gas_price:
        if not isinstance(options.gas_price, int) or options.gas_price < 0:
            msg = f"{name}.gas_price must be a non-negative integer"
            raise ValueError(msg)

    if options.gas_limit:
        if not isinstance(options.gas_limit, int) or options.gas_limit < 0:
            msg = f"{name}.gas_limit must be a non-negative integer"
            raise ValueError(msg)


def assert_cashout_options(value: Any, name: str = "CashoutOptions"):
    """
    CashoutOptions is an alias for TransactionOptions
    """
    assert_transaction_options(value, name)


def assert_all_tags_options(value: Any, name: str = "AllTagsOptions"):
    if not isinstance(value, AllTagsOptions):
        msg = f"Not a valid {name} data"
        raise TypeError(msg)


def assert_transaction_hash(transaction_hash: Any, name: str = "TransactionHash"):
    """
    Validates that a value is a valid TransactionHash.

    Args:
        transaction_hash (Any): The value to check.
        name (str): The name of the object, for error messages.

    Raises:
        TypeError: If the transaction_hash is not a string or does not have the correct length.
    """
    if not isinstance(transaction_hash, str):
        msg = "TransactionHash has to be a string!"
        raise TypeError(msg)

    if not is_prefixed_hex_string(transaction_hash):
        raise TypeError()

    # Hash is 64 long + '0x' prefix = 66
    if len(transaction_hash) != PUBKEY_HEX_LENGTH:
        msg = f"{name} has to be prefixed hex string with total length 66 (0x prefix including)"
        raise TypeError(msg)


def assert_public_key(value: Any) -> None:
    assert_hex_string(value, PUBKEY_HEX_LENGTH)


def is_feed_type(_type: Union[FeedType, str]) -> bool:
    """
    Check if the given value is a valid feed type.

    Args:
        _type (Union[FeedType, str]): The value to check.

    Returns:
        bool: True if the value is a valid feed type, False otherwise.
    """
    return isinstance(_type, str) and _type in [member.value for member in FeedType]


def assert_feed_type(_type: Union[FeedType, str]) -> None:
    """
    Assert that the given value is a valid feed type.

    Args:
        _type (Union[FeedType, str]): The value to check.

    Raises:
        TypeError: If the value is not a valid feed type.
    """
    if not is_feed_type(_type):
        msg = "Invalid feed type"
        raise TypeError(msg)


def assert_batch_id(value: Any) -> None:
    if not value:
        msg = f"{value} is not a valid value for postage batch id"
        raise BeeError(msg)
    assert_hex_string(value, BATCH_ID_HEX_LENGTH)


def assert_file_data(value: Union[str, bytes, IO]) -> None:
    """
    Check whether the given parameter is a correct file representation for file upload.
    Raises TypeError if not valid.

    Args:
        value (Union[str, ByteString, IO, File]): The value to check.

    Raises:
        TypeError: If the value is not a valid file representation.
    """
    if not isinstance(value, (str, bytes, IO)):
        msg = "Data must be either str, bytes, IO, or File!"
        raise TypeError(msg)
