
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 typeIndex = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIndex];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Find first non-zero byte to detect if string is empty
        const FIT_BYTE* end = byteData + size;
        const FIT_BYTE* firstNonZero = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });
        
        if (firstNonZero == end)
            return FIT_TRUE; // Empty string, nothing to do

        values.reserve(size + 1); // Pre-allocate for efficiency
        
        // Process string byte-by-byte, tracking positions for string indexes
        FIT_UINT8 stringPos = 0;
        for (const FIT_BYTE* p = byteData; p < end; ++p, ++stringPos)
        {
            FIT_BYTE byte = *p;
            values.push_back(byte);
            
            // Record new string start after null terminator (if space remains)
            if (byte == 0 && stringPos + 1 < size)
                stringIndexes.push_back(stringPos + 1);
        }

        // Null-terminate if not already
        if (values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // For non-string types, skip all-invalid segments and copy the first valid chunk
        const FIT_BYTE* p = byteData;
        const FIT_BYTE* end = p + size;
        const FIT_BYTE* invalidValue = baseTypeInvalids[typeIndex];

        while (p + typeSize <= end)
        {
            if (memcmp(p, invalidValue, typeSize) != 0)
            {
                // Found valid data: copy remaining bytes and break
                values.insert(values.end(), p, end);
                break;
            }
            p += typeSize;
        }
    }

    return FIT_TRUE;
}
