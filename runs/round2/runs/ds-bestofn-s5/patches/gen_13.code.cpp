template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[type];
    if (fieldArrayIndex >= static_cast<FIT_UINT8>(values.size()))
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* p = values.data() + static_cast<size_t>(fieldArrayIndex) * size;

    if (size == sizeof(T))
    {
        T rv;
        std::memcpy(&rv, p, sizeof(T));
        return rv;
    }

    T rv = 0;
    for (int i = 0; i < size; i++)
    {
        rv |= static_cast<T>(p[i]) << (i * 8);
    }

    return rv;
}
