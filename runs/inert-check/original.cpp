DetailedProtocolVersion::DetailedProtocolVersion(FIT_UINT8 major, FIT_UINT8 minor)
{
    version = ( major << FIT_PROTOCOL_VERSION_MAJOR_SHIFT ) | minor;
}

