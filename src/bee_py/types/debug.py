from enum import Enum

from pydantic import BaseModel, Field


class BeeModes(Enum):
    FULL = "full"
    LIGHT = "light"
    ULTRA_LIGHT = "ultra-light"
    DEV = "dev"


class DebugStatus(BaseModel):
    peer: str = Field(..., alias="peer")
    proximity: float = Field(..., alias="proximity")
    bee_mode: BeeModes = Field(..., alias="beeMode")
    reserve_size: int = Field(..., alias="reserveSize")
    pullsync_rate: float = Field(..., alias="pullsyncRate")
    storage_radius: float = Field(..., alias="storageRadius")
    connected_peers: int = Field(..., alias="connectedPeers")
    neighborhood_size: int = Field(..., alias="neighborhoodSize")
    batch_commitment: int = Field(..., alias="batchCommitment")
    is_reachable: bool = Field(..., alias="isReachable")


class HealthStatus(Enum):
    OK = "ok"


class Health(BaseModel):
    status: HealthStatus = Field(..., alias="status")
    version: str = Field(..., alias="version")
    api_version: str = Field(..., alias="apiVersion")
    debug_api_version: str = Field(..., alias="debugApiVersion")


class NodeInfo(BaseModel):
    """
    Represents information about the Bee node.

    Attributes:
        gateway_mode (bool): Indicates whether the node is in a Gateway mode.
        Gateway mode is a restricted mode where some features are not available.
        bee_mode (BeeModes): Indicates in what mode Bee is running.
        chequebook_enabled (bool): Indicates whether the Bee node has its own deployed chequebook.
        swap_enabled (bool): Indicates whether SWAP is enabled for the Bee node.

        @see [Bee docs - Chequebook](https://docs.ethswarm.org/docs/introduction/terminology#cheques--chequebook)
        @see [Bee docs - SWAP](https://docs.ethswarm.org/docs/introduction/terminology#swap)
    """

    gateway_mode: bool = Field(..., alias="gatewayMode")
    bee_mode: BeeModes = Field(..., alias="beeMode")
    chequebook_enabled: bool = Field(..., alias="chequebookEnabled")
    swap_enabled: bool = Field(..., alias="swapEnabled")
