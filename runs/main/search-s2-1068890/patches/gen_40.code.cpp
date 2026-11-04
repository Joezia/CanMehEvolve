
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    FIT_UINT8 typeIndex = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIndex];
    const FIT_BYTE* byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();
    stringIndexes.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Fast path: scan for first non-zero byte
        const FIT_BYTE* end = byteData + bytesLeft;
        const FIT_BYTE* firstNonZero = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });

        if (firstNonZero == end)
            return FIT_TRUE;

        values.reserve(bytesLeft + 1); // Pre-allocate to avoid reallocations
        values.insert(values.end(), byteData, end);
        
        // Record string index for first non-zero string
        FIT_UINT8 stringPos = static_cast<FIT_UINT8>(firstNonZero - byteData);
        stringIndexes.push_back(stringPos);

        // Scan for null terminators to record subsequent string positions
        for (const FIT_BYTE* p = firstNonZero; p < end; ++p)
        {
            if (*p == 0 && (p - byteData + 1 < size))
                stringIndexes.push_back(static_cast<FIT_UINT8>(p - byteData + 1));
        }

        // Ensure null termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // For non-string types: skip leading invalid-value chunks
        const FIT_BYTE* invalidVal = baseTypeInvalids[typeIndex];
        const FIT_BYTE* p = byteData;
        FIT_UINT8 remaining = bytesLeft;

        while (remaining >= typeSize)
        {
            if (std::memcmp(p, invalidVal, typeSize) != 0)
                break;
            p += typeSize;
            remaining -= typeSize;
        }

        if (remaining > 0)
            values.insert(values.end(), p, p + remaining);
    }

    return FIT_TRUE;
}
