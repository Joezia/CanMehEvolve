template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;

    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8 size = baseTypeSizes[type];
    const FIT_UINT8* p = values.data() + (fieldArrayIndex * size);

    switch (size)
    {
    case 1:
        return static_cast<T>(p[0]);
    case 2:
        return static_cast<T>(
            static_cast<FIT_UINT64>(p[0]) |
            (static_cast<FIT_UINT64>(p[1]) << 8));
    case 4:
        return static_cast<T>(
            static_cast<FIT_UINT64>(p[0]) |
            (static_cast<FIT_UINT64>(p[1]) << 8) |
            (static_cast<FIT_UINT64>(p[2]) << 16) |
            (static_cast<FIT_UINT64>(p[3]) << 24));
    case 8:
        return static_cast<T>(
            static_cast<FIT_UINT64>(p[0]) |
            (static_cast<FIT_UINT64>(p[1]) << 8) |
            (static_cast<FIT_UINT64>(p[2]) << 16) |
            (static_cast<FIT_UINT64>(p[3]) << 24) |
            (static_cast<FIT_UINT64>(p[4]) << 32) |
            (static_cast<FIT_UINT64>(p[5]) << 40) |
            (static_cast<FIT_UINT64>(p[6]) << 48) |
            (static_cast<FIT_UINT64>(p[7]) << 56));
    default:
    {
        FIT_UINT64 rv = 0;
        for (int i = 0; i < size; i++)
        {
            rv |= static_cast<FIT_UINT64>(p[i]) << (i * 8);
        }
        return static_cast<T>(rv);
    }
    }
}
