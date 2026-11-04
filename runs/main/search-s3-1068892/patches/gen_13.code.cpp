
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
        const FIT_BYTE* firstNonZero = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });

        if (firstNonZero == end) // Entirely zero string
            return FIT_TRUE;

        // Record initial position
        stringIndexes.push_back(0);

        // Process string: copy bytes and track null terminators
        FIT_UINT8 stringPos = 0;
        for (const FIT_BYTE* p = firstNonZero; p < end; ++p)
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

        while (bytesLeft >= typeSize)
        {
            if (std::memcmp(p, invalidPtr, typeSize) != 0)
                break;
            p += typeSize;
            bytesLeft -= typeSize;
        }

        // Copy remaining valid data
        if (bytesLeft > 0)
            values.insert(values.end(), p, p + bytesLeft);
    }

    return FIT_TRUE;
}
