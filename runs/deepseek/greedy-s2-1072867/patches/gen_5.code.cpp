template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 baseType = type & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[baseType];
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[baseType]);
    }

    const FIT_UINT8* p = values.data() + fieldArrayIndex * size;

    if constexpr (sizeof(T) >= 1)
    {
        if (size == 1)
        {
            return static_cast<T>(p[0]);
        }
    }
    if constexpr (sizeof(T) >= 2)
    {
        if (size == 2)
        {
            FIT_UINT16 v;
            std::memcpy(&v, p, 2);
            return static_cast<T>(v);
        }
    }
    if constexpr (sizeof(T) >= 4)
    {
        if (size == 4)
        {
            FIT_UINT32 v;
            std::memcpy(&v, p, 4);
            return static_cast<T>(v);
        }
    }
    if constexpr (sizeof(T) >= 8)
    {
        if (size == 8)
        {
            FIT_UINT64 v;
            std::memcpy(&v, p, 8);
            return static_cast<T>(v);
        }
    }

    T rv = 0;
    for (int i = 0; i < size; i++)
    {
        rv |= static_cast<T>(p[i]) << (i * 8);
    }
    return rv;
}
