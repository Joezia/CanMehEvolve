
```cpp
FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_UINT8 bytesLeft = size;
    FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 typeSize = baseTypeSizes[typeIdx];
    const FIT_BYTE *byteData = static_cast<const FIT_BYTE*>(data);

    values.clear();

    if (GetType() == FIT_BASE_TYPE_STRING)
    {
        // Fast path: check if entire buffer is zeros
        const FIT_BYTE *end = byteData + bytesLeft;
        const FIT_BYTE *nullPos = std::find(byteData, end, 0);
        
        if (nullPos == end) // No null terminator → full string data
        {
            values.assign(byteData, end);
            values.push_back(0); // Null-terminate
            stringIndexes.clear();
            stringIndexes.push_back(0);
        }
        else if (nullPos == byteData) // Empty string
        {
            // Do nothing, values remains empty
        }
        else // Has embedded nulls
        {
            // Copy up to and including first null
            values.assign(byteData, nullPos + 1);
            stringIndexes.clear();
            stringIndexes.push_back(0);
            stringIndexes.push_back(static_cast<FIT_UINT8>(nullPos - byteData + 1));
            
            // Process remaining bytes for additional strings
            const FIT_BYTE *cur = nullPos + 1;
            while (cur < end)
            {
                nullPos = std::find(cur, end, 0);
                if (nullPos == cur)
                {
                    // Consecutive nulls → skip
                    cur++;
                    continue;
                }
                
                FIT_UINT8 strLen = static_cast<FIT_UINT8>(nullPos - cur);
                if (strLen > 0)
                {
                    values.insert(values.end(), cur, nullPos + 1);
                    stringIndexes.push_back(static_cast<FIT_UINT8>(values.size() - strLen - 1));
                }
                cur = nullPos + 1;
            }
        }
    }
    else
    {
        // Non-string: copy first non-invalid value block
        const FIT_BYTE *p = byteData;
        const FIT_BYTE *invalid = baseTypeInvalids[typeIdx];
        FIT_UINT8 remaining = bytesLeft;
        
        while (remaining >= typeSize)
        {
            if (std::memcmp(p, invalid, typeSize) != 0)
            {
                values.assign(byteData, byteData + bytesLeft);
                break;
            }
            p += typeSize;
            remaining -= typeSize;
        }
    }

    return FIT_TRUE;
}
