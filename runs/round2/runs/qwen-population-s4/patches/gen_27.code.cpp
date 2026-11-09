
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    if (fieldArrayIndex >= (FIT_UINT8)values.size()) {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8 size = baseTypeSizes[type];
    const FIT_UINT8* ptr = &values[(fieldArrayIndex * size)];
    
    T rv;
    std::memcpy(&rv, ptr, size);
    return rv;
}
