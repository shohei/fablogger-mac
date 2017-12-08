class Response:
    ADVERTISING = 0xAD
    DATA        = 0xDA
    RESPONSE    = 0xDD
    ERROR       = 0xE0

class Status:
    BLE_OK                       = 0x00
    BLE_INVALID_STATE            = 0x01
    BLE_PACKET_PENDING           = 0x02
    BLE_PACKET_LENGTH_SHORT      = 0x03
    BLE_PACKET_LENGTH_LONG       = 0x04
    BLE_PACKET_LEN_MISMATCH      = 0x05
    BLE_PACKET_INVALID_SIZE      = 0x06
    BLE_HEADER_INVALID_CODE      = 0x07
    BLE_HEADER_INVALID_COMMAND   = 0x08
    BLE_ADVERT_INVALID_INTERVAL  = 0x09
    BLE_SYSTEM_BUSY              = 0x0A
    BLE_SYSTEM_ERROR             = 0x0B

class Command:
    PING        = 0xA0
    CONNECT     = 0xC0
    DISCONNECT  = 0xC7
    MEASURE     = 0x00
    STOP        = 0x01
    TRANSFER    = 0x02
    ADV_RATE    = 0x03
    BLINK       = 0x04
    UPTIME      = 0x05
