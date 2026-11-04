
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK]);
    }

    const FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    if (size == sizeof(T))
    {
        T rv;
        std::memcpy(&rv, &values[fieldArrayIndex * size], size);
        return rv;
    }

    T rv = 0;
    for (FIT_UINT8 i = 0; i < size; i++)
    {
        rv |= static_cast<T>(values[(fieldArrayIndex * size) + i]) << (i * 8);
    }
    return rv;
}
