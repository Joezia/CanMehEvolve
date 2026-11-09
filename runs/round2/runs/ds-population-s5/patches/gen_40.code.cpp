FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    const FIT_UINT8 type = GetType();
    const FIT_UINT8 typeIndex = type & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 typeSize = baseTypeSizes[typeIndex];
    FIT_BYTE *byteData = (FIT_BYTE *) data;

    values.clear();

    if (type == FIT_BASE_TYPE_STRING)
    {
        FIT_UINT8 index = 0;
        while (index < size)
        {
            if (byteData[index] != 0)
                break;
            index++;
        }

        if (index == size)
            return FIT_TRUE;

        stringIndexes.push_back(0);

        values.assign(byteData, byteData + size);

        if (size > 2)
        {
            const FIT_BYTE *p = byteData;
            const FIT_BYTE *end = byteData + size;
            while (p < end)
            {
                const void *found = std::memchr(p, 0, (size_t)(end - p));
                if (found == 0)
                    break;

                const FIT_UINT8 pos = (FIT_UINT8)((const FIT_BYTE *)found - byteData);
                if (pos + 2 < size)
                    stringIndexes.push_back((FIT_UINT8)(pos + 1));

                p = (const FIT_BYTE *)found + 1;
            }
        }

        if (values.back() != 0)
            values.push_back(0);
    }
    else
    {
        const FIT_BYTE *invalid = baseTypeInvalids[typeIndex];
        const FIT_BYTE *point = byteData;
        int bytes = size;
        FIT_BOOL hasData = FIT_FALSE;

        switch (typeSize)
        {
            case 1:
                while (bytes > 0)
                {
                    if (*point != invalid[0])
                    {
                        hasData = FIT_TRUE;
                        break;
                    }
                    ++point;
                    --bytes;
                }
                break;

            case 2:
                while (bytes > 0)
                {
                    if (point[0] != invalid[0] || point[1] != invalid[1])
                    {
                        hasData = FIT_TRUE;
                        break;
                    }
                    point += 2;
                    bytes -= 2;
                }
                break;

            case 4:
                while (bytes > 0)
                {
                    if (point[0] != invalid[0] || point[1] != invalid[1] ||
                        point[2] != invalid[2] || point[3] != invalid[3])
                    {
                        hasData = FIT_TRUE;
                        break;
                    }
                    point += 4;
                    bytes -= 4;
                }
                break;

            case 8:
                while (bytes > 0)
                {
                    if (point[0] != invalid[0] || point[1] != invalid[1] ||
                        point[2] != invalid[2] || point[3] != invalid[3] ||
                        point[4] != invalid[4] || point[5] != invalid[5] ||
                        point[6] != invalid[6] || point[7] != invalid[7])
                    {
                        hasData = FIT_TRUE;
                        break;
                    }
                    point += 8;
                    bytes -= 8;
                }
                break;

            default:
                while (bytes > 0)
                {
                    if (std::memcmp(point, invalid, typeSize) != 0)
                    {
                        hasData = FIT_TRUE;
                        break;
                    }
                    point += typeSize;
                    bytes -= typeSize;
                }
                break;
        }

        if (hasData)
            values.assign(byteData, byteData + size);
    }

    return FIT_TRUE;
}
