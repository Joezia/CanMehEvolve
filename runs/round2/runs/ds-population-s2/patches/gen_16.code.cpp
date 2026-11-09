FIT_BOOL FieldBase::Read(const void *data, const FIT_UINT8 size)
{
    FIT_BYTE *byteData = (FIT_BYTE *) data;
    const FIT_UINT8 type = GetType();

    if (type == FIT_BASE_TYPE_STRING)
    {
        FIT_UINT8 index = 0;
        while (index < size && byteData[index] == 0)
        {
            ++index;
        }

        if (index == size)
        {
            values.clear();
            return FIT_TRUE;
        }

        stringIndexes.push_back(0);
        values.assign(byteData, byteData + size);

        for (FIT_UINT8 i = 0; i + 2 < size; ++i)
        {
            if (byteData[i] == 0)
            {
                stringIndexes.push_back(i + 1);
            }
        }

        if (byteData[size - 1] != 0)
        {
            values.push_back(0);
        }

        return FIT_TRUE;
    }

    const FIT_UINT8 baseType = type & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 typeSize = baseTypeSizes[baseType];
    const FIT_BYTE *invalid = baseTypeInvalids[baseType];
    int bytes = size;
    FIT_BYTE *point = byteData;

    switch (typeSize)
    {
        case 1:
        {
            const FIT_BYTE inv = invalid[0];
            while (bytes > 0)
            {
                if (*point != inv)
                {
                    values.assign(byteData, byteData + size);
                    return FIT_TRUE;
                }
                ++point;
                --bytes;
            }
        }
        break;

        case 2:
        {
            FIT_UINT16 inv;
            memcpy(&inv, invalid, 2);
            while (bytes > 0)
            {
                FIT_UINT16 value;
                memcpy(&value, point, 2);
                if (value != inv)
                {
                    values.assign(byteData, byteData + size);
                    return FIT_TRUE;
                }
                point += 2;
                bytes -= 2;
            }
        }
        break;

        case 4:
        {
            FIT_UINT32 inv;
            memcpy(&inv, invalid, 4);
            while (bytes > 0)
            {
                FIT_UINT32 value;
                memcpy(&value, point, 4);
                if (value != inv)
                {
                    values.assign(byteData, byteData + size);
                    return FIT_TRUE;
                }
                point += 4;
                bytes -= 4;
            }
        }
        break;

        case 8:
        {
            FIT_UINT64 inv;
            memcpy(&inv, invalid, 8);
            while (bytes > 0)
            {
                FIT_UINT64 value;
                memcpy(&value, point, 8);
                if (value != inv)
                {
                    values.assign(byteData, byteData + size);
                    return FIT_TRUE;
                }
                point += 8;
                bytes -= 8;
            }
        }
        break;

        default:
        {
            while (bytes > 0)
            {
                if (memcmp(point, invalid, typeSize) != 0)
                {
                    values.assign(byteData, byteData + size);
                    return FIT_TRUE;
                }
                point += typeSize;
                bytes -= typeSize;
            }
        }
        break;
    }

    values.clear();
    return FIT_TRUE;
}
