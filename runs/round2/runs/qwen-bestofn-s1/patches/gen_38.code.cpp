
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK]);
    }

    const FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    if (size == 0) return T{};

    const FIT_UINT8 offset = fieldArrayIndex * size;
    T rv = 0;
    
    if constexpr (std::is_same_v<T, FIT_UINT8>) {
        rv = static_cast<T>(values[offset]);
    } else if constexpr (std::is_same_v<T, FIT_SINT8>) {
        rv = static_cast<T>(static_cast<FIT_INT8>(values[offset]));
    } else if constexpr (sizeof(T) <= 4) {
        // For 16/32-bit types, use memcpy to avoid alignment issues
        // and leverage compiler's optimized copy
        const void* src = &values[offset];
        std::memcpy(&rv, src, size);
    } else {
        // For 64-bit types (FIT_UINT64/FIT_SINT64)
        const void* src = &values[offset];
        std::memcpy(&rv, src, size);
    }
    
    return rv;
}
