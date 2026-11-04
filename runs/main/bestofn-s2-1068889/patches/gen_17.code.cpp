
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK]);
    }

    const FIT_UINT8 size = baseTypeSizes[GetType() & FIT_BASE_TYPE_NUM_MASK];
    const size_t offset = fieldArrayIndex * size;

    if constexpr (std::is_same_v<T, FIT_UINT8> || std::is_same_v<T, FIT_INT8>) {
        return static_cast<T>(values[offset]);
    } else if constexpr (std::is_same_v<T, FIT_UINT16> || std::is_same_v<T, FIT_INT16>) {
        FIT_UINT16 rv = 0;
        std::memcpy(&rv, &values[offset], 2);
        return static_cast<T>(rv);
    } else if constexpr (std::is_same_v<T, FIT_UINT32> || std::is_same_v<T, FIT_INT32>) {
        FIT_UINT32 rv = 0;
        std::memcpy(&rv, &values[offset], 4);
        return static_cast<T>(rv);
    } else if constexpr (std::is_same_v<T, FIT_UINT64> || std::is_same_v<T, FIT_INT64>) {
        FIT_UINT64 rv = 0;
        std::memcpy(&rv, &values[offset], 8);
        return static_cast<T>(rv);
    } else {
        // Fallback for other types
        T rv = 0;
        for (FIT_UINT8 i = 0; i < size; i++) {
            rv |= static_cast<T>(values[offset + i]) << (i * 8);
        }
        return rv;
    }
}
