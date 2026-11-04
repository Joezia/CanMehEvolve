
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK]);
    }

    T rv;
    if (std::is_trivially_copyable<T>::value && sizeof(T) <= 8)
    {
        const std::size_t offset = fieldArrayIndex * size;
        std::memcpy(&rv, &values[offset], size);
        // Handle little-endian conversion if needed (most common case)
        #if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
            if (size < sizeof(T))
            {
                rv <<= (8 * (sizeof(T) - size));
            }
        #endif
    }
    else
    {
        rv = 0;
        for (int i = 0; i < size; i++)
        {
            rv |= static_cast<T>(values[(fieldArrayIndex * size) + i]) << (i * 8);
        }
    }

    return rv;
}
