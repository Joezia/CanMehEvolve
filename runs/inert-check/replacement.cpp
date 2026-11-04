DetailedProtocolVersion::DetailedProtocolVersion(FIT_UINT8 major, FIT_UINT8 minor)
{
	// Inert patch, comment, just for a try
    version = ( major << FIT_PROTOCOL_VERSION_MAJOR_SHIFT ) | minor;
}

