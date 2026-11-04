
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK]);
    }

    const FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    T rv = 0;
    const FIT_UINT8* ptr = &values[(fieldArrayIndex * size)];
    
    if constexpr (std::is_same_v<T, FIT_UINT8> || std::is_same_v<T, FIT_SINT8>) {
        rv = static_cast<T>(*ptr);
    } else if constexpr (std::is_same_v<T, FIT_UINT16> || std::is_same_v<T, FIT_SINT16>) {
        std::memcpy(&rv, ptr, 2);
    } else if constexpr (std::is_same_v<T, FIT_UINT32> || std::is_same_v<T, FIT_SINT32>) {
        std::memcpy(&rv, ptr, 4);
    } else if constexpr (std::is_same_v<T, FIT_UINT64> || std::is_same_v<T, FIT_SINT64>) {
        std::memcpy(&rv, ptr, 8);
    } else {
        for (FIT_UINT8 i = 0; i < size; i++) {
            rv |= static_cast<T>(ptr[i]) << (i * 8);
        }
    }
    
    return rv;
}
