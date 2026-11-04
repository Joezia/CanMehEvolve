
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Find first non-zero byte to check if string is empty
        const FIT_BYTE* end = byteData + bytesLeft;
        const FIT_BYTE* firstNonZero = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });
        
        if (firstNonZero == end)
            return FIT_TRUE; // Empty string, nothing to do

        // Reserve space for efficiency
        values.reserve(bytesLeft + 1);
        values.assign(byteData, end);
        
        // Ensure null-termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // For non-string types, copy all data if not entirely invalid
        const FIT_BYTE* invalidPtr = baseTypeInvalids[typeIdx];
        bool allInvalid = true;
        const FIT_BYTE* p = byteData;
        
        while (bytesLeft >= typeSize)
        {
            if (memcmp(p, invalidPtr, typeSize) != 0)
            {
                allInvalid = false;
                break;
            }
            p += typeSize;
            bytesLeft -= typeSize;
        }
        
        if (!allInvalid)
        {
            values.resize(size);
            std::memcpy(values.data(), byteData, size);
        }
    }

    return FIT_TRUE;
}
