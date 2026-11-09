
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE* byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();
    stringIndexes.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Fast check for empty string (all zeros)
        bool hasNonZero = false;
        for (FIT_UINT8 i = 0; i < size; ++i)
        {
            if (byteData[i] != 0)
            {
                hasNonZero = true;
                break;
            }
        }
        
        if (!hasNonZero)
            return FIT_TRUE;
        
        // First string starts at position 0
        stringIndexes.push_back(0);
        
        // Copy data and track string boundaries
        FIT_UINT8 pos = 0;
        for (FIT_UINT8 i = 0; i < size; ++i)
        {
            FIT_BYTE b = byteData[i];
            values.push_back(b);
            ++pos;
            
            if (b == 0 && pos < size)
            {
                stringIndexes.push_back(pos);
            }
        }
        
        // Null terminate if not already
        if (values.empty() || values.back() != 0)
        {
            values.push_back(0);
        }
    }
    else
    {
        // Check all full type-sized blocks for invalid values
        FIT_UINT8 remaining = size;
        const FIT_BYTE* p = byteData;
        const FIT_BYTE* invalid = baseTypeInvalids[typeIdx];
        bool hasNonInvalid = false;
        
        while (remaining >= typeSize)
        {
            if (std::memcmp(p, invalid, typeSize) != 0)
            {
                hasNonInvalid = true;
                break;
            }
            p += typeSize;
            remaining -= typeSize;
        }
        
        // If there's a partial block at the end, it's always non-invalid
        if (remaining > 0)
        {
            hasNonInvalid = true;
        }
        
        if (hasNonInvalid)
        {
            values.insert(values.end(), byteData, byteData + size);
        }
    }

    return FIT_TRUE;
}
