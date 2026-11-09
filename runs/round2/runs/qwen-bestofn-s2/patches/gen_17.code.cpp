
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 typeIndex = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[typeIndex];
    
    if (fieldArrayIndex >= (FIT_UINT8)values.size() / size)
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[typeIndex]);
    }

    T rv;
    const std::size_t offset = fieldArrayIndex * size;
    std::memcpy(&rv, &values[offset], size);
    
    return rv;
}
