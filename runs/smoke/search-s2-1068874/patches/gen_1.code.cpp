
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE* byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Fast string handling: check for all-zero input first
        if (std::all_of(byteData, byteData + size, [](FIT_BYTE b) { return b == 0; }))
        {
            return FIT_TRUE;
        }

        // Copy entire buffer and find null terminators for stringIndexes
        values.assign(byteData, byteData + size);
        
        // Ensure null-termination
        if (!values.empty() && values.back() != 0)
        {
            values.push_back(0);
        }

        // Build stringIndexes by scanning for nulls in original data
        stringIndexes.clear();
        FIT_UINT8 pos = 0;
        for (FIT_UINT8 i = 0; i < size; ++i)
        {
            if (byteData[i] == 0)
            {
                stringIndexes.push_back(pos);
                pos = i + 1;
            }
        }
        stringIndexes.push_back(pos);
    }
    else
    {
        // Skip leading invalid values
        FIT_UINT8 bytesLeft = size;
        const FIT_BYTE* invalidPtr = baseTypeInvalids[typeIdx];

        while (bytesLeft >= typeSize)
        {
            if (std::memcmp(byteData, invalidPtr, typeSize) != 0)
            {
                break;
            }
            byteData += typeSize;
            bytesLeft -= typeSize;
        }

        // If there's remaining valid data, copy it
        if (bytesLeft > 0)
        {
            values.insert(values.end(), byteData, byteData + bytesLeft);
        }
    }

    return FIT_TRUE;
}
