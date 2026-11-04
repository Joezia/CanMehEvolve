
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[type];
    const FIT_BYTE* byteData = static_cast<const FIT_BYTE*>(data);
    FIT_UINT8 bytesLeft = size;

    values.clear();

    if (type == FIT_BASE_TYPE_NUM_STRING)
    {
        const FIT_BYTE* invalid = baseTypeInvalids[type];
        
        // Skip leading invalid values for non-string types
        while (bytesLeft >= typeSize)
        {
            if (memcmp(byteData, invalid, typeSize) != 0)
                break;
            byteData += typeSize;
            bytesLeft -= typeSize;
        }

        // Copy remaining valid data
        if (bytesLeft > 0)
            values.insert(values.end(), byteData, byteData + bytesLeft);
    }
    else
    {
        // String type processing
        const FIT_BYTE* end = byteData + size;
        FIT_UINT8 stringPos = 0;
        stringIndexes.clear();
        stringIndexes.push_back(stringPos);

        while (byteData < end)
        {
            FIT_BYTE byte = *byteData++;
            values.push_back(byte);
            
            if (byte == 0 && byteData < end)
                stringIndexes.push_back(values.size());
        }

        // Ensure null termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }

    return FIT_TRUE;
}
