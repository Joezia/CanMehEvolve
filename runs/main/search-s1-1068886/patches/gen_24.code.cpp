
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 size = baseTypeSizes[type];
    
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* data = &values[(fieldArrayIndex * size)];
    T rv;
    std::memcpy(&rv, data, size);
    return rv;
}
