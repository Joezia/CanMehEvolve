
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    const FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Early exit if entire buffer is zeros
        bool hasNonZero = false;
        for (FIT_UINT8 i = 0; i < bytesLeft; ++i) {
            if (byteData[i] != 0) {
                hasNonZero = true;
                break;
            }
        }
        if (!hasNonZero) return FIT_TRUE;

        // Reserve space for efficiency
        values.reserve(bytesLeft + 1);

        // Copy all bytes, tracking nulls for string indexes
        FIT_UINT8 stringPos = 0;
        stringIndexes.clear();
        stringIndexes.push_back(0);

        for (FIT_UINT8 i = 0; i < bytesLeft; ++i) {
            FIT_BYTE byte = byteData[i];
            values.push_back(byte);
            if (byte == 0 && stringPos + 1 < size) {
                stringIndexes.push_back(stringPos + 1);
            }
            stringPos++;
        }

        // Null-terminate if needed
        if (values.back() != 0) {
            values.push_back(0);
        }
    }
    else
    {
        // Fast path: skip invalid values (all bytes matching the invalid sentinel)
        const FIT_BYTE* invalid = baseTypeInvalids[typeIdx];
        const FIT_BYTE* end = byteData + bytesLeft;
        const FIT_BYTE* p = byteData;

        while (p + typeSize <= end) {
            if (std::memcmp(p, invalid, typeSize) != 0) {
                values.insert(values.end(), byteData, byteData + bytesLeft);
                break;
            }
            p += typeSize;
        }
    }

    return FIT_TRUE;
}
