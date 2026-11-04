
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[type];
    
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* data = &values[(fieldArrayIndex * size)];
    
    // Handle common small sizes with optimized code paths
    if (size == 1) return static_cast<T>(data[0]);
    if (size == 2) return static_cast<T>(static_cast<uint16_t>(data[0]) | (static_cast<uint16_t>(data[1]) << 8));
    if (size == 3) return static_cast<T>(static_cast<uint32_t>(data[0]) | (static_cast<uint32_t>(data[1]) << 8) | (static_cast<uint32_t>(data[2]) << 16));
    if (size == 4) {
        uint32_t val;
        std::memcpy(&val, data, 4);
        return static_cast<T>(val);
    }
    
    // Fallback for larger types (rare in practice)
    T rv = 0;
    for (FIT_UINT8 i = 0; i < size; i++)
    {
        rv |= static_cast<T>(data[i]) << (i * 8);
    }
    return rv;
}
