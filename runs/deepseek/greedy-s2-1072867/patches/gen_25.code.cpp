template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;

    if (__builtin_expect(fieldArrayIndex >= static_cast<FIT_UINT8>(values.size()), 0))
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* const data = values.data();
    const FIT_UINT8 size = baseTypeSizes[type];

    if (__builtin_expect(size == 1, 1))
    {
        return static_cast<T>(data[fieldArrayIndex]);
    }

    const FIT_UINT8* const p = data + (fieldArrayIndex * size);

    if constexpr (std::is_integral<T>::value)
    {
        if (size == sizeof(T))
        {
            T rv;
            std::memcpy(&rv, p, sizeof(T));
            return rv;
        }
    }

    if (size == 2)
    {
        FIT_UINT16 rv;
        std::memcpy(&rv, p, 2);
        return static_cast<T>(rv);
    }

    if (size == 4)
    {
        FIT_UINT32 rv;
        std::memcpy(&rv, p, 4);
        return static_cast<T>(rv);
    }

    if (size == 8)
    {
        FIT_UINT64 rv;
        std::memcpy(&rv, p, 8);
        return static_cast<T>(rv);
    }

    FIT_UINT64 rv = 0;
    for (int i = 0; i < size; ++i)
    {
        rv |= static_cast<FIT_UINT64>(p[i]) << (i * 8);
    }
    return static_cast<T>(rv);
}
