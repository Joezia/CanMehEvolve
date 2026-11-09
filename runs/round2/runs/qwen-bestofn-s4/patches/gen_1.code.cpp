
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Fast path: find first non-zero byte
        const FIT_BYTE* end = byteData + bytesLeft;
        const FIT_BYTE* p = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });
        
        if (p == end) // all zeros, empty string
            return FIT_TRUE;

        // Process string: collect bytes and track null-terminated segments
        stringIndexes.clear();
        stringIndexes.push_back(0);
        
        for (const FIT_BYTE* q = byteData; q < end; ++q)
        {
            values.push_back(*q);
            if (*q == 0 && (q - byteData + 1) < size)
                stringIndexes.push_back(q - byteData + 1);
        }

        // Ensure null termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // For non-string types, skip leading invalid values (all bytes equal to invalid pattern)
        const FIT_BYTE* invalid = baseTypeInvalids[typeIdx];
        const FIT_BYTE* pos = byteData;
        const FIT_BYTE* end = byteData + bytesLeft;
        
        // Process in chunks of typeSize where possible
        while (pos + typeSize <= end)
        {
            if (std::memcmp(pos, invalid, typeSize) != 0)
                break;
            pos += typeSize;
        }
        
        // Copy remaining valid data if any
        if (pos < end)
            values.insert(values.end(), pos, end);
    }

    return FIT_TRUE;
}
