
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[type];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE*>(data);
    FIT_UINT8 bytesLeft = size;

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Find first non-zero byte
        FIT_UINT8 idx = 0;
        while (idx < bytesLeft && byteData[idx] == 0) idx++;

        if (idx == bytesLeft) return FIT_TRUE; // all zeros, empty string

        // Reserve space for performance
        values.reserve(bytesLeft + 1);

        // Copy all bytes, track string indexes
        FIT_UINT8 stringPos = 0;
        stringIndexes.clear();
        stringIndexes.push_back(stringPos);

        while (bytesLeft > 0)
        {
            FIT_BYTE byte = *byteData++;
            values.push_back(byte);
            stringPos++;
            bytesLeft--;

            if (byte == 0 && bytesLeft > 0)
                stringIndexes.push_back(stringPos);
        }

        // Ensure null termination
        if (values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // For non-string types: skip leading invalid values
        const FIT_BYTE *invalid = baseTypeInvalids[type];
        FIT_UINT8 remaining = bytesLeft;

        // Fast path: skip invalid records in bulk using pointer arithmetic
        const FIT_BYTE *p = byteData;
        while (remaining >= typeSize)
        {
            if (memcmp(p, invalid, typeSize) != 0)
                break;
            p += typeSize;
            remaining -= typeSize;
        }

        // Copy remaining valid data in one go
        if (remaining > 0)
        {
            values.resize(remaining);
            std::memcpy(values.data(), p, remaining);
        }
    }

    return FIT_TRUE;
}
