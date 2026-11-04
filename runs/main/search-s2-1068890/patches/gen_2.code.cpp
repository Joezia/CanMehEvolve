
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    const FIT_BYTE* byteData = static_cast<const FIT_BYTE*>(data);
    const FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 typeSize = baseTypeSizes[typeIdx];

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Find first non-zero byte to detect empty strings
        const FIT_BYTE* end = byteData + size;
        const FIT_BYTE* firstNonZero = std::find_if(byteData, end, [](FIT_BYTE b) { return b != 0; });
        
        if (firstNonZero == end) // empty string
        {
            // Empty string case: no data, nothing to add
            return FIT_TRUE;
        }

        // Copy all bytes (including null terminators)
        values.assign(byteData, end);
        
        // Ensure null termination
        if (values.empty() || values.back() != 0)
            values.push_back(0);
    }
    else
    {
        // For non-string types, check if entire buffer is invalid
        const FIT_BYTE* invalidPtr = baseTypeInvalids[typeIdx];
        bool hasValidData = false;
        
        // Fast path: check if entire buffer is invalid
        if (size >= typeSize)
        {
            // Compare in chunks of typeSize
            for (FIT_UINT8 i = 0; i < size; i += typeSize)
            {
                if (std::memcmp(byteData + i, invalidPtr, typeSize) != 0)
                {
                    hasValidData = true;
                    break;
                }
            }
        }
        
        if (hasValidData)
        {
            values.assign(byteData, byteData + size);
        }
    }

    return FIT_TRUE;
}
