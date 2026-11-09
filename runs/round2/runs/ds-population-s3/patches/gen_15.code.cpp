template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = static_cast<FIT_UINT8>(GetType() & FIT_BASE_TYPE_NUM_MASK);
    const FIT_UINT8 size = baseTypeSizes[type];

    if (fieldArrayIndex >= static_cast<FIT_UINT8>(values.size()))
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* src = values.data() + (fieldArrayIndex * size);

    if (size == sizeof(T))
    {
        T rv;
        std::memcpy(&rv, src, sizeof(T));
        return rv;
    }

    T rv = 0;
    for (int i = 0; i < size; i++)
    {
        rv |= static_cast<T>(src[i]) << (i * 8);
    }
    return rv;
}
