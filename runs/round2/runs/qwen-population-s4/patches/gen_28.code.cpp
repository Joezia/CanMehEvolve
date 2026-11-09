
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 baseTypeIndex = GetType() & FIT_BASE_TYPE_NUM_MASK;
    if (fieldArrayIndex >= (FIT_UINT8)values.size() / baseTypeSizes[baseTypeIndex]) {
        return *reinterpret_cast<const T*>(baseTypeInvalids[baseTypeIndex]);
    }

    const FIT_UINT8 size = baseTypeSizes[baseTypeIndex];
    const FIT_UINT8* ptr = &values[fieldArrayIndex * size];
    
    T rv;
    std::memcpy(&rv, ptr, size);
    return rv;
}
