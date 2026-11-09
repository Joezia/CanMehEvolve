template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[type];

    if (fieldArrayIndex >= static_cast<FIT_UINT8>(values.size()))
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* p = values.data() + (fieldArrayIndex * size);

    if (size == 1)
    {
        return static_cast<T>(p[0]);
    }
    if (size == 2 && sizeof(T) >= 2)
    {
        T rv = 0;
        std::memcpy(&rv, p, 2);
        return rv;
    }
    if (size == 4 && sizeof(T) >= 4)
    {
        T rv = 0;
        std::memcpy(&rv, p, 4);
        return rv;
    }
    if (size == 8 && sizeof(T) >= 8)
    {
        T rv = 0;
        std::memcpy(&rv, p, 8);
        return rv;
    }

    T rv = 0;
    for (int i = 0; i < size; i++)
    {
        rv |= static_cast<T>(p[i]) << (i * 8);
    }
    return rv;
}
