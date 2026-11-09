
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 typeIdx = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[typeIdx];
    
    if (fieldArrayIndex >= (FIT_UINT8)values.size() / size)
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[typeIdx]);
    }

    T rv;
    const FIT_UINT8 offset = fieldArrayIndex * size;
    std::memcpy(&rv, &values[offset], size);
    return rv;
}
