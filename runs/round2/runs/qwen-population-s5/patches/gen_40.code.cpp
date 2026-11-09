
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE* byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Find first non-zero byte
        const FIT_BYTE* end = byteData + bytesLeft;
        const FIT_BYTE* firstNonZero = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });
        
        if (firstNonZero == end) // All zeros or empty
            return FIT_TRUE;
        
        stringIndexes.clear();
        stringIndexes.push_back(0);

        // Copy all bytes and track null terminators for string indexes
        FIT_UINT8 pos = 0;
        for (const FIT_BYTE* p = byteData; p < end; ++p, ++pos)
        {
            values.push_back(*p);
            if (*p == 0 && pos + 1 < size)
                stringIndexes.push_back(pos + 1);
        }

        // Ensure null termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // For non-string types, check if entire buffer is invalid
        const FIT_BYTE* invalidValue = baseTypeInvalids[typeIdx];
        bool allInvalid = true;
        
        for (FIT_UINT8 i = 0; i < bytesLeft; i += typeSize)
        {
            if (i + typeSize <= bytesLeft && std::memcmp(byteData + i, invalidValue, typeSize) != 0)
            {
                allInvalid = false;
                break;
            }
        }
        
        if (!allInvalid)
            values.assign(byteData, byteData + bytesLeft);
    }

    return FIT_TRUE;
}
