
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE* byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();
    stringIndexes.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Fast path: find first non-zero byte
        const FIT_BYTE* end = byteData + bytesLeft;
        const FIT_BYTE* firstNonZero = byteData;
        while (firstNonZero < end && *firstNonZero == 0)
            ++firstNonZero;

        if (firstNonZero == end) // Entirely zero string
            return FIT_TRUE;

        // Record initial position
        stringIndexes.push_back(0);

        // Process string: copy bytes and track null terminators
        FIT_UINT8 stringPos = 0;
        const FIT_BYTE* p = firstNonZero;
        // Pre-reserve capacity to avoid reallocations
        FIT_UINT8 remaining = static_cast<FIT_UINT8>(end - p);
        values.reserve(values.size() + remaining);

        for (; p < end; ++p)
        {
            values.push_back(*p);
            ++stringPos;
            if (*p == 0 && stringPos < size)
                stringIndexes.push_back(stringPos);
        }

        // Ensure null termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // Non-string: skip entirely invalid values at the start
        const FIT_BYTE* invalidPtr = baseTypeInvalids[typeIdx];
        const FIT_BYTE* p = byteData;

        // Inline the comparison loop for better branch prediction
        while (bytesLeft >= typeSize)
        {
            // Unroll memcmp for small typeSize (typically 1-8 bytes)
            FIT_BOOL isInvalid = FIT_FALSE;
            for (FIT_UINT8 i = 0; i < typeSize; ++i)
            {
                if (p[i] != invalidPtr[i])
                {
                    isInvalid = FIT_TRUE;
                    break;
                }
            }
            if (isInvalid)
                break;
            p += typeSize;
            bytesLeft -= typeSize;
        }

        // Copy remaining valid data
        if (bytesLeft > 0)
        {
            FIT_UINT8 len = bytesLeft;
            values.reserve(values.size() + len);
            values.insert(values.end(), p, p + len);
        }
    }

    return FIT_TRUE;
}
