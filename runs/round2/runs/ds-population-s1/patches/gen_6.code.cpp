FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    const FIT_UINT8 type = GetType();
    const FIT_UINT8 typeIndex = type & FIT_BASE_TYPE_NUM_MASK;
    const FIT_BYTE *byteData = (const FIT_BYTE *) data;

    values.clear();

    if (type == FIT_BASE_TYPE_STRING)
    {
        const FIT_BYTE *end = byteData + size;
        const FIT_BYTE *p = byteData;

        while (p < end && *p == 0)
            ++p;

        if (p == end)
            return FIT_TRUE;

        stringIndexes.push_back(0);

        values.insert(values.end(), byteData, end);

        if (values.back() != 0)
            values.push_back(0);

        if (size > 2)
        {
            const FIT_BYTE *nullEnd = byteData + size - 2;
            for (const FIT_BYTE *q = byteData; q < nullEnd; ++q)
            {
                if (*q == 0)
                    stringIndexes.push_back(static_cast<FIT_UINT8>(q - byteData + 1));
            }
        }

        return FIT_TRUE;
    }

    if (size == 0)
        return FIT_TRUE;

    const FIT_UINT8 typeSize = baseTypeSizes[typeIndex];
    const FIT_BYTE *invalid = baseTypeInvalids[typeIndex];

    bool valid = false;

    if (typeSize == 1)
    {
        const FIT_BYTE inv = invalid[0];
        for (int i = 0; i < size; ++i)
        {
            if (byteData[i] != inv)
            {
                valid = true;
                break;
            }
        }
    }
    else if (typeSize == 2)
    {
        FIT_UINT16 inv;
        memcpy(&inv, invalid, sizeof(inv));
        for (int i = 0; i < size; i += 2)
        {
            FIT_UINT16 v;
            memcpy(&v, byteData + i, sizeof(v));
            if (v != inv)
            {
                valid = true;
                break;
            }
        }
    }
    else if (typeSize == 4)
    {
        FIT_UINT32 inv;
        memcpy(&inv, invalid, sizeof(inv));
        for (int i = 0; i < size; i += 4)
        {
            FIT_UINT32 v;
            memcpy(&v, byteData + i, sizeof(v));
            if (v != inv)
            {
                valid = true;
                break;
            }
        }
    }
    else if (typeSize == 8)
    {
        FIT_UINT64 inv;
        memcpy(&inv, invalid, sizeof(inv));
        for (int i = 0; i < size; i += 8)
        {
            FIT_UINT64 v;
            memcpy(&v, byteData + i, sizeof(v));
            if (v != inv)
            {
                valid = true;
                break;
            }
        }
    }
    else
    {
        int bytes = size;
        const FIT_BYTE *point = byteData;

        while (bytes > 0)
        {
            if (memcmp(point, invalid, typeSize) != 0)
            {
                valid = true;
                break;
            }
            point += typeSize;
            bytes -= typeSize;
        }
    }

    if (valid)
        values.insert(values.end(), byteData, byteData + size);

    return FIT_TRUE;
}
