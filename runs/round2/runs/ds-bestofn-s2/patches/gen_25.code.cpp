template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType();
    const FIT_UINT8 baseType = type & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[baseType];
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[baseType]);
    }

    const FIT_UINT8* p = values.data() + (fieldArrayIndex * size);
    FIT_UINT64 rv = 0;
    switch (size)
    {
    case 1:
        rv = p[0];
        break;
    case 2:
        rv = static_cast<FIT_UINT64>(p[0]) |
             (static_cast<FIT_UINT64>(p[1]) << 8);
        break;
    case 4:
        rv = static_cast<FIT_UINT64>(p[0]) |
             (static_cast<FIT_UINT64>(p[1]) << 8) |
             (static_cast<FIT_UINT64>(p[2]) << 16) |
             (static_cast<FIT_UINT64>(p[3]) << 24);
        break;
    case 8:
        rv = static_cast<FIT_UINT64>(p[0]) |
             (static_cast<FIT_UINT64>(p[1]) << 8) |
             (static_cast<FIT_UINT64>(p[2]) << 16) |
             (static_cast<FIT_UINT64>(p[3]) << 24) |
             (static_cast<FIT_UINT64>(p[4]) << 32) |
             (static_cast<FIT_UINT64>(p[5]) << 40) |
             (static_cast<FIT_UINT64>(p[6]) << 48) |
             (static_cast<FIT_UINT64>(p[7]) << 56);
        break;
    default:
        for (int i = 0; i < size; i++)
        {
            rv |= static_cast<FIT_UINT64>(p[i]) << (i * 8);
        }
        break;
    }
    return static_cast<T>(rv);
}
