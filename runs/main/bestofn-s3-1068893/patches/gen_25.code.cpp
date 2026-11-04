
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    FIT_BASE_TYPE type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[type];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (type == FIT_BASE_TYPE_STRING)
    {
        // Fast path: scan for first non-zero byte
        const FIT_BYTE* end = byteData + bytesLeft;
        const FIT_BYTE* firstNonZero = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });

        if (firstNonZero == end) // all zeros or empty
            return FIT_TRUE;

        values.reserve(bytesLeft + 1); // pre-allocate to avoid reallocations
        values.assign(byteData, end);
        
        // Ensure null termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // Skip leading invalid values
        const FIT_BYTE* invalid = baseTypeInvalids[type];
        const FIT_BYTE* p = byteData;
        const FIT_BYTE* end = byteData + bytesLeft;

        while (p + typeSize <= end)
        {
            if (std::memcmp(p, invalid, typeSize) != 0)
                break;
            p += typeSize;
        }

        // Copy remaining data (including any trailing invalid values)
        if (p < end)
            values.assign(p, end);
    }

    return FIT_TRUE;
}
